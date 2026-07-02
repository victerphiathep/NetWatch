import hashlib
import math
import re


EMBEDDING_DIMENSION_COUNT = 384
TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_%-]+")


def tokenize_text(text):
    return TOKEN_PATTERN.findall(text.lower())


def build_text_embedding(text, dimension_count=EMBEDDING_DIMENSION_COUNT):
    embedding = [0.0] * dimension_count

    for token in tokenize_text(text):
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        embedding_index = int(token_hash[:8], 16) % dimension_count
        embedding[embedding_index] += 1.0

    embedding_length = math.sqrt(sum(value * value for value in embedding))

    if embedding_length == 0:
        return embedding

    return [value / embedding_length for value in embedding]


def build_text_embeddings(texts):
    return [build_text_embedding(text) for text in texts]
