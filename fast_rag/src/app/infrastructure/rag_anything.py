import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pathlib import Path
from contextlib import asynccontextmanager
import numpy as np
from raganything import RAGAnything, RAGAnythingConfig
from lightrag import LightRAG
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.utils import EmbeddingFunc
from lightrag.kg.postgres_impl import PostgreSQLDB
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
BASE_DIR = Path(__file__).resolve().parent.parent

config = RAGAnythingConfig(
    working_dir=str(BASE_DIR / "rag_storage"),
    parser="docling",  # Parser selection: mineru, docling, or paddleocr
    parse_method="auto",  # Parse method: auto, ocr, or txt
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True,
)

@asynccontextmanager
async def init_rag_anything(app: FastAPI):
    try:
        def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
            return openai_complete_if_cache(
                "gpt-5.4-nano",
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=api_key,
                **kwargs,
            )

        def vision_model_func(
            prompt, system_prompt=None, history_messages=[], image_data=None, messages=None, **kwargs
        ):
            if messages:
                return openai_complete_if_cache(
                    "gpt-5.4-mini",
                    "",
                    messages=messages,
                    api_key=api_key,
                    **kwargs,
                )
            elif image_data:
                return openai_complete_if_cache(
                    "gpt-5.4-mini",
                    "",
                    messages=[
                        {"role": "system", "content": system_prompt} if system_prompt else None,
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}"
                                    },
                                },
                            ],
                        }
                    ],
                    api_key=api_key,
                    **kwargs,
                )
            
            else:
                return llm_model_func(prompt, system_prompt, history_messages, **kwargs)

        # embedding_func 커스텀마이징 - Huggingface
        loop = asyncio.get_event_loop()
        hf_embeddings = await loop.run_in_executor(
            None,
            lambda: HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli")
        )

        async def local_embedding_func_wrapper(texts):
            embeddings = hf_embeddings.embed_documents(texts)
            return np.array(embeddings)
        
        embedding_func = EmbeddingFunc(
            embedding_dim=768,
            max_token_size=512,
            func=local_embedding_func_wrapper
        )

        # PostgresQL 연결 초기화
        postgres_db = PostgreSQLDB(config={
            "host": os.getenv("POSTGRES_HOST"),
            "port": int(os.getenv("POSTGRES_PORT", 5432)),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "database": os.getenv("POSTGRES_DATABASE"),
            "workspace": "rag",
            "max_connections": 10,
            "connection_retry_attempts": 3,
            "connection_retry_backoff": 1.5,
            "connection_retry_backoff_max": 10,
            "pool_close_timeout": 30,
            "enable_vector": True,
        })
        await postgres_db.initdb()

        lightrag_instance = LightRAG(
            working_dir=str(BASE_DIR / "rag_storage"),
            llm_model_func=llm_model_func,
            embedding_func=embedding_func,
            kv_storage="PGKVStorage",
            vector_storage="PGVectorStorage",
            graph_storage="NetworkXStorage",
            doc_status_storage="PGDocStatusStorage",
        )
        lightrag_instance.db = postgres_db
        
        rag = RAGAnything(
            lightrag=lightrag_instance,
            config=config,
            llm_model_func=llm_model_func,
            vision_model_func=vision_model_func,
            embedding_func=embedding_func,
        )

        await rag.lightrag.initialize_storages()
        app.state.rag = rag

        yield


    except Exception as e:
        print(f"Rag Anything 초기화 실패: {e}")

    finally:
        if hasattr(app.state, "rag"):
            del app.state.rag


def get_rag_engine(request: Request) -> RAGAnything:
    if not hasattr(request.app.state, "rag"):
        raise Exception("Rag 엔진이 초기화 되지 않았습니다.")
    
    return request.app.state.rag
