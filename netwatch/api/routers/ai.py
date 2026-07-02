from fastapi import APIRouter, HTTPException

from netwatch.ai.rag_query import answer_with_anthropic, retrieve_relevant_context
from netwatch.api.schemas import AskAiRequest, AskAiResponse


router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/ask", response_model=AskAiResponse)
def ask_netwatch_ai(ask_ai_request: AskAiRequest):
    retrieved_context_documents = retrieve_relevant_context(
        ask_ai_request.question,
        ask_ai_request.result_count,
    )

    try:
        answer = answer_with_anthropic(
            ask_ai_request.question,
            retrieved_context_documents,
        )
    except RuntimeError as runtime_error:
        raise HTTPException(status_code=503, detail=str(runtime_error)) from runtime_error

    return {
        "question": ask_ai_request.question,
        "answer": answer,
        "retrieved_context": retrieved_context_documents,
    }
