from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.core.deps import get_current_user
from app.core.logging import get_logger
from app.core.embeddings import get_embedding_service
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.schemas.documents import UploadResponse
from app.schemas.documents import UploadResponse, DocumentItem, DocumentListResponse

import io

import pypdf

from langchain_text_splitters import RecursiveCharacterTextSplitter

router = APIRouter(prefix="/documents", tags=["documents"])
logger = get_logger(__name__)

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


def extract_text(file_bytes: bytes, filename: str) -> str:
    if filename.endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
    return text.replace("\x00", "")  # strip null bytes

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    content = await file.read()
    text = extract_text(content, file.filename)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    chunks = splitter.split_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text chunks could be created from this file")

    embeddings = get_embedding_service()
    vectors = embeddings.embed_documents(chunks)

    document = await Document.create(user=current_user, filename=file.filename, enabled=True)
    await DocumentChunk.bulk_create([
    DocumentChunk(document=document, chunk_index=i, chunk_text=chunk, embedding=vector)
    for i, (chunk, vector) in enumerate(zip(chunks, vectors))
])

    logger.info("Uploaded %s: %d chunks for user %s", file.filename, len(chunks), current_user.id)
    return UploadResponse(filename=file.filename, chunk_count=len(chunks))





@router.get("", response_model=DocumentListResponse)
async def list_documents(current_user: User = Depends(get_current_user)):
    docs = await Document.filter(user=current_user).order_by("-created_at")
    return DocumentListResponse(documents=[DocumentItem.model_validate(d) for d in docs])


@router.patch("/{document_id}/enabled")
async def toggle_document(document_id: str, enabled: bool, current_user: User = Depends(get_current_user)):
    doc = await Document.get_or_none(id=document_id, user=current_user)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.enabled = enabled
    await doc.save()
    return {"id": str(doc.id), "enabled": doc.enabled}

@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: str, current_user: User = Depends(get_current_user)):
    doc = await Document.get_or_none(id=document_id, user=current_user)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await doc.delete()
