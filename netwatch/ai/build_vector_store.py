import chromadb

from netwatch.ai.embeddings import build_text_embeddings
from netwatch.ai.knowledge_base import load_knowledge_documents
from netwatch.config import CHROMA_DATABASE_DIR


COLLECTION_NAME = "netwatch_knowledge"


def get_chroma_collection():
    CHROMA_DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DATABASE_DIR))

    return chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def rebuild_vector_store():
    knowledge_documents = load_knowledge_documents()
    chroma_collection = get_chroma_collection()

    chroma_collection.upsert(
        ids=[knowledge_document["id"] for knowledge_document in knowledge_documents],
        documents=[
            knowledge_document["text"] for knowledge_document in knowledge_documents
        ],
        embeddings=build_text_embeddings(
            [knowledge_document["text"] for knowledge_document in knowledge_documents]
        ),
        metadatas=[
            knowledge_document["metadata"] for knowledge_document in knowledge_documents
        ],
    )

    return len(knowledge_documents)


def main():
    document_count = rebuild_vector_store()
    print(f"Indexed {document_count} NetWatch knowledge documents")
    print(f"Chroma database path: {CHROMA_DATABASE_DIR}")


if __name__ == "__main__":
    main()
