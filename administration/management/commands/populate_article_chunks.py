import hashlib
import logging

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction

from administration.api.enums import ProcessingMessages
from administration.exceptions import ProcessChunkError
from administration.helpers.milvus_service import MilvusService
from administration.models import Article, ArticleChunk
from administration.utils import send_article_update

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate ArticleChunk instances by parsing articles and generate embeddings for these chunks to store in Milvus'

    def handle(self, *args, **options):
        milvus_service = MilvusService(collection_name="article_embeddings")
        milvus_service.connect()
        collection = milvus_service.create_collection()

        for article in Article.objects.filter(status=Article.Status.NOT_PROCESSED).iterator(chunk_size=100):
            with transaction.atomic():
                article.status = Article.Status.IN_PROGRESS
                article.processing_info = ProcessingMessages.PARSING_REMOTE_URL.value
                article.save(update_fields=["status", "processing_info"])
                send_article_update(article)

                # Parse article content and create chunks
                text = self.parse_article_content(article.url)

                self.update_database_with_chunks(article, text)
                send_article_update(article)

                # Process each chunk for the current article
                article.processing_info = ProcessingMessages.SUCCESSFULLY_CREATED_CHUNKS.value
                article.save(update_fields=["status", "processing_info"])
                send_article_update(article)
                for chunk in ArticleChunk.objects.filter(article=article, is_processed=False):
                    self.process_chunk(chunk, milvus_service, collection)

            article.processing_info = ProcessingMessages.SUCCESSFULLY_STORED_EMBEDDINGS.value
            article.status = Article.Status.PROCESSED
            article.save(update_fields=['status', 'processing_info'])
            send_article_update(article)
        logger.info(ProcessingMessages.SUCCESSFULLY_PROCESSED_ARTICLE.value)

    def parse_article_content(self, url):
        """
        Fetch and parse article content from URL using BeautifulSoup.
        """
        response = requests.get(url, timeout=60)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()

    def update_database_with_chunks(self, article, text, chunk_size=500):
        """
        Create or skip ArticleChunk instances based on the text content.
        The chunk_size parameter determines the maximum number of characters in each chunk.
        """
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
        for i, chunk_text in enumerate(chunks):
            text_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
            if not ArticleChunk.objects.filter(text_hash=text_hash).exists():
                chunk_order = i + 1
                word_count = len(chunk_text.split())
                article_chunk = ArticleChunk.objects.create(
                    article=article,
                    text=chunk_text,
                    chunk_order=chunk_order,
                    text_hash=text_hash,
                    word_count=word_count,
                )
                send_article_update(article)
                logger.info(
                    ProcessingMessages.SUCCESSFULLY_CREATED_ARTICLE_CHUNK.value.format(article_chunk.id, article.title)
                )
            else:
                logger.info(ProcessingMessages.SKIPPED_CREATING_DUPLICATE_CHUNK.value.format(article.title))

    def process_chunk(self, chunk, milvus_service, collection):
        """
        Generate embeddings for a single chunk and store in Milvus.
        """
        # Generate a single embedding for the chunk text
        embedding = milvus_service.generate_embeddings_from_text(chunk.text)
        article = chunk.article
        if embedding:
            # Construct the data to be inserted
            data = {"id": [chunk.id], "embedding": [embedding]}
            try:
                collection.insert([data["id"], data["embedding"]])
                chunk.is_processed = True
                chunk.save(update_fields=['is_processed'])
                logger.info(ProcessingMessages.PROCESSED_AND_STORED_EMBEDDING_CHUNK.value.format(chunk.id))

                article.status = Article.Status.IN_PROGRESS
                article.save(update_fields=['status'])
                send_article_update(article)

            except Exception as e:
                article.status = Article.Status.ERROR
                article.processing_info = ProcessingMessages.FAILED_TO_STORE_EMBEDDING_CHUNK.value
                article.save(update_fields=['status', 'processing_info'])
                send_article_update(article)
                raise ProcessChunkError(ProcessingMessages.FAILED_TO_STORE_EMBEDDING_CHUNK.value) from e
