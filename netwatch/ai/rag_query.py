import argparse
import os

from netwatch.ai.build_vector_store import get_chroma_collection
from netwatch.ai.embeddings import build_text_embedding


DEFAULT_MODEL = "claude-sonnet-4-5"


def retrieve_relevant_context(question, result_count=5):
    chroma_collection = get_chroma_collection()

    query_results = chroma_collection.query(
        query_embeddings=[build_text_embedding(question)],
        n_results=result_count,
    )

    documents = query_results.get("documents", [[]])[0]
    metadatas = query_results.get("metadatas", [[]])[0]

    return [
        {
            "text": document,
            "metadata": metadata,
        }
        for document, metadata in zip(documents, metadatas)
    ]


def build_rag_prompt(question, retrieved_context_documents):
    context_text = "\n\n---\n\n".join(
        retrieved_context_document["text"]
        for retrieved_context_document in retrieved_context_documents
    )

    return f"""
You are NetWatch AI, an assistant for a network capacity management dashboard.
Answer using only the provided NetWatch context.
If the context is not enough, say what is missing.

NetWatch context:
{context_text}

User question:
{question}
""".strip()


def answer_with_anthropic(question, retrieved_context_documents):
    try:
        import anthropic
    except ImportError as import_error:
        raise RuntimeError(
            "The anthropic package is not installed. Run: pip install -r requirements.txt"
        ) from import_error

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Set it before asking Claude for an answer."
        )

    anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
    model_name = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
    rag_prompt = build_rag_prompt(question, retrieved_context_documents)

    message = anthropic_client.messages.create(
        model=model_name,
        max_tokens=700,
        messages=[
            {
                "role": "user",
                "content": rag_prompt,
            }
        ],
    )

    return message.content[0].text


def print_retrieved_context(retrieved_context_documents):
    print("\nRetrieved context")
    print("-----------------")

    for context_index, retrieved_context_document in enumerate(
        retrieved_context_documents,
        start=1,
    ):
        metadata = retrieved_context_document["metadata"]
        print(f"\n[{context_index}] {metadata}")
        print(retrieved_context_document["text"])


def main():
    parser = argparse.ArgumentParser(description="Ask NetWatch AI a question.")
    parser.add_argument("question", help="Natural-language question about NetWatch data")
    parser.add_argument(
        "--context-only",
        action="store_true",
        help="Only print retrieved context without calling Anthropic",
    )
    parser.add_argument(
        "--results",
        type=int,
        default=5,
        help="Number of context documents to retrieve",
    )
    parsed_arguments = parser.parse_args()

    retrieved_context_documents = retrieve_relevant_context(
        parsed_arguments.question,
        parsed_arguments.results,
    )

    if parsed_arguments.context_only:
        print_retrieved_context(retrieved_context_documents)
        return

    try:
        answer = answer_with_anthropic(
            parsed_arguments.question,
            retrieved_context_documents,
        )
    except RuntimeError as runtime_error:
        print(runtime_error)
        print_retrieved_context(retrieved_context_documents)
        return

    print(answer)


if __name__ == "__main__":
    main()
