import os
import glob
import shutil
import tempfile
from pathlib import Path
from fastapi import Depends
from lightrag import QueryParam
from app.infrastructure.rag_anything import RagEngine, get_rag_engine
from app.repositories.rag_repository import RagRepository, get_rag_repository
from app.repositories.document_repository import DocumentRepository, get_document_repository
from app.schemas.document_schema import DocumentCreateDTO, DocumentResponseDTO
from app.services.s3_service import S3Service, get_s3_service

class RagService:
    def __init__(
        self,
        rag_repo: RagRepository,
        document_repo: DocumentRepository,
        s3_service: S3Service,
        rag_engine: RagEngine
    ):
        self.rag_repo = rag_repo
        self.document_repo = document_repo
        self.s3_service = s3_service
        self.rag_engine = rag_engine


    # rag engince이 파일을 읽어올 수 있도록 임시 파일을 생성
    async def save_to_temp_file(self, content) -> str:
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp.write(content)
        temp.close()

        return temp.name
    

    async def ingest_document(self, file, member_id: int) -> DocumentResponseDTO:
        # 1. 파일 읽기
        content = await file.read()
        await file.seek(0) #file stream reset

        # 2. S3 파일 업로드
        s3_result = await self.s3_service.upload_file(file, "documents")

        # 3. doucuments 테이블에 DB에 추가
        new_document = DocumentCreateDTO(
            document_name=s3_result.original_filename,
            document_s3_key=s3_result.original_key,
            member_id=member_id
        )
        created_document = await self.document_repo.create_document(new_document)

        # 4. 임시파일 경로 생성
        file_path = await self.save_to_temp_file(content)
        
        # 5. embedding dir를 각 created_document로 나눔(filter)
        rag = await self.rag_engine.get_rag(created_document.id)

        # 6. rag_engine 멀티모달 전처리 및 임베딩
        await rag.process_document_complete(
            file_path=file_path,
            output_dir="./rag_output",
            parse_method="auto",
            file_name=str(created_document.id) # 생성된 document id로 추적
        )

        # 7. workspace 경로로 /rag_output 파일 저장
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent #workspace
        rag_output_dir = str(BASE_DIR / "rag_output")

        # 8. 임시로 저장된 파일 -> S3 버킷에 저장 후 삭제
        for local_url in glob.glob(f"{rag_output_dir}/**/*.png", recursive=True) + \
                          glob.glob(f"{rag_output_dir}/**/*.jpg", recursive=True):
            s3_result = await self.s3_service.upload_local_file(local_url, "rag_images")
            s3_url = s3_result.original_file_url
            await self.rag_repo.replace_image_path_in_all_chunks(local_url, s3_url)

        # 9. 임시 파일 삭제
        shutil.rmtree(rag_output_dir, ignore_errors=True)
        os.remove(file_path)

        # 10. 반환
        return DocumentResponseDTO(
            id=created_document.id,
            document_name=created_document.document_name,
            document_s3_key=created_document.document_s3_key,
            document_created_at=created_document.document_created_at,
            member_id=member_id
        )


    async def query(self, question: str, document_id: int) -> str:
        final_question = question + """
            답변 시 아래 규칙을 따르세요:

            1. 관련 이미지가 있다면 반드시 마크다운 이미지 형식으로 포함하세요.
            형식: ![이미지설명](이미지URL)
            예시: ![포트폴리오 헤더](http://localhost:7000/image/path/image_0.png)

            2. 관련 이미지의 경로도 반드시 포함하세요
            형식: image_path: 이미지URL
            예시: image_path: http://localhost:7000/image/path/image_0.png

            3. 이미지는 관련 설명 바로 아래에 삽입하세요.
            
            4. 존재하지 않는 이미지 URL은 절대 만들어내지 마세요.
        """

        rag = await self.rag_engine.get_rag(document_id)
        result = await rag.lightrag.aquery(
            final_question,
            param=QueryParam("hybrid")
        )

        return result



def get_rag_service(
    rag_repo: RagRepository = Depends(get_rag_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    s3_service: S3Service = Depends(get_s3_service),
    rag_engine: RagEngine = Depends(get_rag_engine)
):
    return RagService(rag_repo, document_repo, s3_service, rag_engine)
