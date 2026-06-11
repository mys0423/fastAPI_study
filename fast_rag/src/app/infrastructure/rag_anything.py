import asyncio
import os
from collections import OrderedDict
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


# LLM / Vision / Embedding 함수 (전역 분리)
def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    return openai_complete_if_cache(
        "gpt-5.4-nano", prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=api_key, **kwargs,
    )

def vision_model_func(prompt, system_prompt=None, history_messages=[], image_data=None, messages=None, **kwargs):
    if messages:
        return openai_complete_if_cache("gpt-5.4-mini", "", messages=messages, api_key=api_key, **kwargs)
    elif image_data:
        return openai_complete_if_cache(
            "gpt-5.4-mini", "",
            messages=[
                {"role": "system", "content": system_prompt} if system_prompt else None,
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]}
            ],
            api_key=api_key, **kwargs,
        )
    else:
        return llm_model_func(prompt, system_prompt, history_messages, **kwargs)


def get_postgres_config(workspace: str) -> dict:
    return {
        "host": os.getenv("POSTGRES_HOST"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "database": os.getenv("POSTGRES_DATABASE"),
        "workspace": workspace,
        "max_connections": 10,
        "connection_retry_attempts": 3,
        "connection_retry_backoff": 1.5,
        "connection_retry_backoff_max": 10,
        "pool_close_timeout": 30,
        "enable_vector": True,
    }


# RagEngine (document_id별 인스턴스 캐싱)
class RagEngine:
    def __init__(self, embedding_func, max_instances: int = 10):
        self.embedding_func = embedding_func
        self._rag_instances: OrderedDict[int, RAGAnything] = OrderedDict()
        self._max_instances = max_instances


    async def get_rag(self, document_id: int) -> RAGAnything:
        if document_id in self._rag_instances:
            self._rag_instances.move_to_end(document_id)
            return self._rag_instances[document_id]

        rag = await self._create_rag_instance(document_id)
        self._rag_instances[document_id] = rag

        if len(self._rag_instances) > self._max_instances:
            self._rag_instances.popitem(last=False)

        return rag


    async def _create_rag_instance(self, document_id: int) -> RAGAnything:
        postgres_db = PostgreSQLDB(config=get_postgres_config(str(document_id)))
        await postgres_db.initdb()

        working_dir = str(BASE_DIR / f"rag_storage/{document_id}")
        os.makedirs(working_dir, exist_ok=True)

        lightrag_instance = LightRAG(
            working_dir=working_dir,
            llm_model_func=llm_model_func,
            embedding_func=self.embedding_func,
            kv_storage="PGKVStorage",
            vector_storage="PGVectorStorage",
            graph_storage="NetworkXStorage",
            doc_status_storage="PGDocStatusStorage",
            workspace=str(document_id),
        )
        lightrag_instance.db = postgres_db

        config = RAGAnythingConfig(
            working_dir=working_dir,
            parser="docling",
            parse_method="auto",
            enable_image_processing=True,
            enable_table_processing=True,
            enable_equation_processing=True,
        )

        rag = RAGAnything(
            lightrag=lightrag_instance,
            config=config,
            llm_model_func=llm_model_func,
            vision_model_func=vision_model_func,
            embedding_func=self.embedding_func,
        )
        await rag.lightrag.initialize_storages()

        return rag


# FastAPI Lifespan
@asynccontextmanager
async def init_rag_anything(app: FastAPI):
    try:
        # 1. 임베딩 먼저 초기화
        loop = asyncio.get_event_loop()
        hf_embeddings = await loop.run_in_executor(
            None, lambda: HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli")
        )

        async def local_embedding_func_wrapper(texts):
            embeddings = hf_embeddings.embed_documents(texts)
            return np.array(embeddings)

        embedding_func = EmbeddingFunc(
            embedding_dim=768,
            max_token_size=512,
            func=local_embedding_func_wrapper,
        )

        # 2. 테이블 생성 (LightRAG 인스턴스까지 생성해야 테이블이 만들어짐)
        init_db = PostgreSQLDB(config=get_postgres_config("default"))
        await init_db.initdb()

        init_lightrag = LightRAG(
            working_dir=str(BASE_DIR / "rag_storage"),
            llm_model_func=llm_model_func,
            embedding_func=embedding_func,
            kv_storage="PGKVStorage",
            vector_storage="PGVectorStorage",
            graph_storage="NetworkXStorage",
            doc_status_storage="PGDocStatusStorage",
        )
        init_lightrag.db = init_db
        await init_lightrag.initialize_storages()

        # 3. RagEngine 초기화
        app.state.rag_engine = RagEngine(embedding_func=embedding_func)
        yield

    except Exception as e:
        print(f"Rag Anything 초기화 실패: {e}")

    finally:
        if hasattr(app.state, "rag_engine"):
            del app.state.rag_engine


def get_rag_engine(request: Request) -> RagEngine:
    if not hasattr(request.app.state, "rag_engine"):
        raise Exception("Rag 엔진이 초기화 되지 않았습니다.")
    return request.app.state.rag_engine