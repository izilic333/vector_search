import logging
import random
import re

import numpy as np
import torch
from django.conf import settings
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, exceptions, utility
from transformers import BertModel, BertTokenizer

from administration.api.enums import ProcessingMessages
from administration.models.article import ArticleChunk

logger = logging.getLogger(__name__)


tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-uncased')
model = BertModel.from_pretrained('bert-base-multilingual-uncased')


class MilvusService:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.dim = 768  # Dimension for BERT embeddings

    def connect(self):
        try:
            connections.connect(alias="default", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)
        except exceptions.ConnectError as err:
            raise exceptions.ConnectError from err

    def get_collection(self):
        self.connect()
        try:
            return Collection(name=self.collection_name)
        except exceptions.CollectionNotExistException as err:
            raise exceptions.CollectionNotExistException from err
        except exceptions.SchemaNotReadyException:
            return self.create_collection()

    def is_chunks_empty(self):
        return not ArticleChunk.objects.exists()

    def create_index(self, field_name="embedding", index_type="IVF_FLAT", metric_type="L2", params=None):
        collection = self.get_collection()
        if params is None:
            params = {"nlist": 100}

        index = {"index_type": index_type, "metric_type": metric_type, "params": params}

        try:
            collection.create_index(field_name, index)
            logger.info(ProcessingMessages.MILVUS_CREATED_INDEX_SUCCESSFULLY.value.format(field_name))
        except exceptions.MilvusException as e:
            logger.error(ProcessingMessages.MILVUS_CREATE_INDEX_ERROR.value.format(field_name, e))
            raise exceptions.MilvusException from e

    def search(self, query_vector, limit=10, search_params=None):
        if search_params is None:
            search_params = {
                "data": [query_vector],
                "anns_field": "embedding",
                "param": {"metric_type": "L2", "offset": 1},
                "limit": limit,
            }

        collection = self.get_collection()
        collection.load()
        return collection.search(**search_params)

    def generate_embeddings_from_text(self, text_query):
        logger.info("Starting embedding generation for text")
        if not text_query:
            logger.info("Empty query received.")
            return None

        try:
            inputs = tokenizer(text_query, return_tensors="pt", padding=True, truncation=True, max_length=512)
            logger.info("Text tokenized")
            with torch.no_grad():
                outputs = model(**inputs)
                logger.info("Model inference completed")
                query_embedding = outputs.last_hidden_state.mean(1).numpy()[0]
        except Exception as e:
            logger.exception(ProcessingMessages.MILVUS_ERROR_DURING_EMBEDDING_GENERATION.value.format(e))
            raise exceptions.MilvusException from e

        query_embedding_norm = query_embedding / np.linalg.norm(query_embedding)
        logger.info("Embedding generated successfully")
        return query_embedding_norm.flatten().tolist()

    def create_collection(self):
        if utility.has_collection(self.collection_name):
            logger.info("Collection '%s' already exists.", self.collection_name)
            collection = Collection(name=self.collection_name)
        else:
            schema = CollectionSchema(
                fields=[
                    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
                    FieldSchema(
                        name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim, description="Embedding Vector"
                    ),
                ],
                description="Article Embeddings",
            )

            collection = Collection(name=self.collection_name, schema=schema)
            logger.info("Created new collection '%s'.", self.collection_name)
        has_index = collection.has_index()
        if not has_index:
            self.create_index()
        collection.load()

        return collection

    def fetch_random_vectors(self, limit=1):
        article_random_text = ArticleChunk.objects.order_by('?').values_list('text', flat=True).first()
        if not article_random_text:
            return {
                "embedding": None,
                "word": None,
                "message": ProcessingMessages.MILVUS_EMPTY_CHUNKS.value,
            }
        words = re.findall(r'\b[a-zA-Z]{2,}\b', article_random_text)
        if not words:
            return {
                "embedding": None,
                "word": None,
                "message": ProcessingMessages.MILVUS_NO_VALID_WORDS_FOUND.value,
            }
        random_word = random.choice(words)
        return {
            "embedding": self.generate_embeddings_from_text(random_word),
            "word": random_word,
            "message": ProcessingMessages.MILVUS_SUCCESSFULLY_FETCH_RANDOM_WORD_AND_CORRESPONDING_VECTOR.value,
        }
