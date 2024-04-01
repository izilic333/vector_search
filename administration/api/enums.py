from enum import Enum


class ProcessingMessages(Enum):
    MILVUS_COLLECTION_DROPPED_SUCCESSFULLY = "Milvus collection dropped successfully"
    MILVUS_COLLECTION_DOES_NOT_EXIST = "Milvus collection does not exist"
    MILVUS_QUERY_VECTOR_MISMATCH = (
        "Query vector dimension does not match the dimension of the vectors in the collection. Expected: {0}, Got: {1}"
    )
    MILVUS_DATABASE_EMPTY = "The database is empty. Please add some article first"
    MILVUS_CREATED_INDEX_SUCCESSFULLY = "Milvus index created successfully for the field: {0}"
    MILVUS_CREATE_INDEX_ERROR = "Failed to create index for the field: {0}, errors: {1}"
    MILVUS_ERROR_DURING_EMBEDDING_GENERATION = "Error during embedding generation, error: {0}"

    MILVUS_EMPTY_CHUNKS = "Empty article chunks. Please add some article first."
    MILVUS_NO_VALID_WORDS_FOUND = "No valid words found in the article chunks. Try again!"
    MILVUS_SUCCESSFULLY_FETCH_RANDOM_WORD_AND_CORRESPONDING_VECTOR = (
        "Successfully fetched random words and corresponding vectors"
    )

    PARSING_REMOTE_URL = "Parsing remote URL to extract article content"
    SUCCESSFULLY_CREATED_CHUNKS = (
        "Successfully created chunks for the article, starting to process each chunk and store embeddings"
    )
    SUCCESSFULLY_STORED_EMBEDDINGS = "Successfully stored embeddings for the article"
    SUCCESSFULLY_PROCESSED_ARTICLE = "Successfully processed the article"
    SUCCESSFULLY_CREATED_ARTICLE_CHUNK = "Successfully created ArticleChunk {0} for article {1}"
    SKIPPED_CREATING_DUPLICATE_CHUNK = (
        "Skipped creating duplicate ArticleChunk for article {0}. A chunk with the same text_hash already exists"
    )
    PROCESSED_AND_STORED_EMBEDDING_CHUNK = "Processed and stored embedding for chunk: {0}"
    FAILED_TO_STORE_EMBEDDING_CHUNK = "Failed to insert chunk into Milvus collection"
