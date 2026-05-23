from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Iterable

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.core.embeddings import get_embedding_service
from app.core.logging import get_logger
from app.models.document import Document, DocumentChunk

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
logger = get_logger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> list[tuple[int, str]]:
    reader = PdfReader(BytesIO(file_bytes))
    logger.debug("Extracting text from PDF with %s page(s)", len(reader.pages))
    pages: list[tuple[int, str]] = []
    for index, page in enumerate(reader.pages, start=1):
        pages.append((index, page.extract_text() or ""))
    return pages


def extract_text_from_txt(file_bytes: bytes) -> list[tuple[int, str]]:
    text = file_bytes.decode("utf-8", errors="ignore")
    logger.debug("Extracting text from TXT payload length=%s", len(text))
    return [(1, text)]


def load_document_pages(filename: str, file_bytes: bytes) -> list[tuple[int, str]]:
    suffix = Path(filename).suffix.lower()
    logger.info("Loading document filename=%s suffix=%s", filename, suffix)
    if suffix == ".pdf":
        return extract_text_from_pdf(file_bytes)
    if suffix in {".txt", ".md"}:
        return extract_text_from_txt(file_bytes)
    logger.error("Unsupported document type filename=%s suffix=%s", filename, suffix)
    raise ValueError("Only PDF and text files are supported.")


async def ingest_document(user_id, filename: str, file_bytes: bytes) -> tuple[Document, int]:
    pages = load_document_pages(filename, file_bytes)
    document = await Document.create(user_id=user_id, filename=filename)
    logger.info("Created document id=%s user_id=%s filename=%s", document.id, user_id, filename)

    embedding_service = get_embedding_service()
    chunks_to_create: list[DocumentChunk] = []
    chunk_counter = 0

    for page_number, page_text in pages:
        if not page_text.strip():
            continue
        logger.debug("Splitting page_number=%s filename=%s", page_number, filename)
        for chunk in splitter.split_text(page_text):
            chunk_counter += 1
            vector = embedding_service.embed_query(chunk)
            chunks_to_create.append(
                DocumentChunk(
                    document=document,
                    chunk_index=chunk_counter,
                    page_number=page_number,
                    chunk_text=chunk,
                    embedding=vector,
                )
            )

    if chunks_to_create:
        await DocumentChunk.bulk_create(chunks_to_create)
        logger.info(
            "Indexed document id=%s filename=%s chunk_count=%s",
            document.id,
            filename,
            len(chunks_to_create),
        )
    else:
        logger.warning("Document id=%s filename=%s produced no searchable chunks", document.id, filename)

    return document, len(chunks_to_create)


async def list_user_documents(user_id):
    return await Document.filter(user_id=user_id).order_by("-created_at")


async def toggle_document_enabled(user_id, document_id, enabled: bool) -> Document:
    document = await Document.get_or_none(id=document_id, user_id=user_id)
    if document is None:
        raise ValueError("Document not found")

    document.enabled = enabled
    await document.save(update_fields=["enabled"])
    logger.info("Document enabled state updated id=%s enabled=%s", document.id, enabled)
    return document
