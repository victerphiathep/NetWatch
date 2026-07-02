# NetWatch AI / RAG

RAG means retrieval-augmented generation.

Instead of asking an LLM to guess from memory, NetWatch first retrieves relevant project facts and then sends those facts to the model as context.

## Local Flow

```text
SQLite Gold/Silver tables + project docs
        |
        v
knowledge documents
        |
        v
ChromaDB vector store
        |
        v
retrieve relevant context for a question
        |
        v
Claude answer using retrieved context
```

The first NetWatch version uses a small deterministic local embedding function for learning. In production, this would usually be replaced by a stronger embedding model or embedding API.

## Build The Vector Store

```powershell
python -m netwatch.ai.build_vector_store
```

## Ask A Question Without Calling Claude

This tests retrieval only:

```powershell
python -m netwatch.ai.rag_query "Which nodes are forecast high risk?" --context-only
```

## Ask Claude

Set an Anthropic API key first:

```powershell
$env:ANTHROPIC_API_KEY="your-api-key"
python -m netwatch.ai.rag_query "Which nodes are forecast high risk and why?"
```

Optional model override:

```powershell
$env:ANTHROPIC_MODEL="claude-sonnet-4-5"
```

## FastAPI Endpoint

The dashboard uses the backend AI endpoint:

```text
POST /ai/ask
```

Request body:

```json
{
  "question": "Which nodes are forecast high risk and why?",
  "result_count": 5
}
```

Response body:

```json
{
  "question": "Which nodes are forecast high risk and why?",
  "answer": "...",
  "retrieved_context": [
    {
      "text": "...",
      "metadata": {
        "source": "gold_node_forecast",
        "document_type": "forecast_risk_summary"
      }
    }
  ]
}
```

If `ANTHROPIC_API_KEY` is not set, the endpoint returns a clear service error instead of pretending to answer.

## Production Mapping

In a Comcast-like system:

```text
Gold planning tables -> retrievable business facts
Silver anomaly data -> operational evidence
Metric docs -> definitions and business rules
Vector DB -> semantic search layer
LLM -> explanation and analysis layer
```

The LLM should not be the source of truth. The warehouse/lakehouse tables remain the source of truth.
