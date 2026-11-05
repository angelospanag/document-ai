from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import config, crud, database
from app.config import get_settings
from app.ingest import read_docx, read_pdf
from app.llm import answer_question, summarize_text
from app.models import DocumentChunk

embed_model = OllamaEmbeddings(model="nomic-embed-text")  # or "mxbai-embed-large"

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_documents(db: Session = Depends(database.get_db)):  # noqa: B008
    return crud.list_documents(db=db)


class SummaryOutput(BaseModel):
    summary: str


@router.post("/")
async def upload_document(
    db: Session = Depends(database.get_db),  # noqa: B008
    file: UploadFile = File(...),  # noqa: B008
):
    filename = file.filename or ""
    try:
        if filename.endswith(".pdf"):
            file_contents = await file.read()
            text = read_pdf(file_contents)
        elif filename.endswith(".docx"):
            file_contents = await file.read()
            text = read_docx(file_contents)
        else:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=(
                    f"Unsupported file type: {filename}. "
                    "Only PDF and DOCX are supported."
                ),
            )

        created_doc = crud.create_document(
            db=db, document_content=text, document_name=filename
        )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
        )

        chunks = splitter.split_text(text)
        embeddings = embed_model.embed_documents(chunks)

        for chunk_text, embedding in zip(chunks, embeddings, strict=False):
            chunk_entry = DocumentChunk(
                document_id=created_doc.id, chunk=chunk_text, embedding=embedding
            )
            db.add(chunk_entry)

        db.commit()
        db.close()
        return {"message": "Document created"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {e!s} ",
        ) from e


class AskQuestionOutput(BaseModel):
    answer: str


class AskQuestionInput(BaseModel):
    question: str


@router.post("/{document_id}/question")
async def ask_question(
    settings: Annotated[config.Settings, Depends(get_settings)],
    document_id: int,
    ask_question_input: AskQuestionInput,
    db: Session = Depends(database.get_db),  # noqa: B008
) -> AskQuestionOutput:
    try:
        document = crud.get_document(db=db, document_id=document_id)

        if document is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Document not found",
            )

        answer = answer_question(
            settings.generation_model_name,
            ask_question_input.question,
            document.text_content,
        )
        return AskQuestionOutput(answer=answer)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {e!s} ",
        ) from e


@router.get("/{document_id}/summarise")
async def summarise(
    settings: Annotated[config.Settings, Depends(get_settings)],
    document_id: int,
    db: Session = Depends(database.get_db),  # noqa: B008
) -> SummaryOutput:
    try:
        document = crud.get_document(db=db, document_id=document_id)

        if document is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Document not found",
            )

        summary = summarize_text(settings.generation_model_name, document.text_content)
        return SummaryOutput(summary=summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {e!s} ",
        ) from e
