from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from typing import Iterable

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        self._backend = None
        self._backend_name = None

    def _load_backend(self):
        if self._backend is not None:
            return self._backend

        try:
            from fastembed import TextEmbedding

            self._backend = TextEmbedding(model_name=settings.FASTEMBED_MODEL)
            self._backend_name = "fastembed"
            logger.info("Loaded embedding backend fastembed with model=%s", settings.FASTEMBED_MODEL)
            return self._backend
        except Exception as exc:
            logger.warning("FastEmbed backend unavailable, using hashed fallback embeddings")
            logger.debug("FastEmbed load error", exc_info=exc)
            self._backend = None
            self._backend_name = "hashed"
            return self

    def embed_documents(self, texts: Iterable[str]) -> list[list[float]]:
        backend = self._load_backend()
        text_list = list(texts)
        logger.debug("Embedding %s document chunk(s) using backend=%s", len(text_list), self._backend_name)

        if self._backend_name == "fastembed":
            return [list(vector) for vector in backend.embed(text_list)]

        return [self._hash_embedding(text) for text in text_list]

    def embed_query(self, text: str) -> list[float]:
        logger.debug("Embedding query text length=%s using backend=%s", len(text), self._backend_name)
        return self.embed_documents([text])[0]

    @staticmethod
    def _hash_embedding(text: str, dimensions: int = 384) -> list[float]:
        vector = [0.0] * dimensions
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimensions
            weight = 1.0 + (digest[4] / 255.0)
            vector[index] += weight

        norm = sum(value * value for value in vector) ** 0.5 or 1.0
        return [value / norm for value in vector]


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()