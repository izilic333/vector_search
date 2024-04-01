from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, tag
from pymilvus import utility

from administration.factories import ArticleFactory
from administration.helpers.milvus_service import MilvusService
from administration.models import Article, ArticleChunk


class TestPopulateArticleChunksCommand(TestCase):
    @patch('administration.management.commands.populate_article_chunks.requests.get')
    def test_populate_article_chunks_single_article(self, mock_requests_get):
        article = ArticleFactory(status=Article.Status.NOT_PROCESSED)

        mock_response = MagicMock()
        mock_response.content = '<html><body>Example Content</body></html>'
        mock_requests_get.return_value = mock_response
        call_command('populate_article_chunks')

        article.refresh_from_db()

        self.assertEqual(article.status, Article.Status.PROCESSED)
        self.assertTrue(ArticleChunk.objects.filter(article=article).exists())

        mock_requests_get.assert_called_once_with(article.url, timeout=60)

    @patch('administration.management.commands.populate_article_chunks.requests.get')
    @patch('administration.management.commands.populate_article_chunks.send_article_update')
    def test_chunks_processing(self, mock_send_article_update, mock_requests_get):
        mock_response = MagicMock()
        mock_response.content = '<html><body>Example Content</body></html>'
        mock_requests_get.return_value = mock_response

        ArticleFactory.create_batch(2, status=Article.Status.NOT_PROCESSED)

        call_command('populate_article_chunks')

        self.assertEqual(mock_send_article_update.call_count, 10)
        self.assertEqual(mock_requests_get.call_count, 2)

        articles = Article.objects.all()

        for article in articles:
            self.assertEqual(article.status, Article.Status.PROCESSED)

        self.assertTrue(ArticleChunk.objects.exists())

    @patch('administration.management.commands.populate_article_chunks.requests.get')
    @tag("debug")
    def test_process_article_with_article_chunks_store_in_milvus_db_and_search_embeddings_and_text(
        self, mock_requests_get
    ):
        article = ArticleFactory(status=Article.Status.NOT_PROCESSED)

        mock_response = MagicMock()
        content = 'Django is a high-level Python web framework that encourages rapid development & clean design. \
        It was developed by experienced developers to take care of much of the hassle of web development, so you can \
        focus on writing your app without needing to reinvent the wheel. It’s free and open source.'
        mock_response.content = f"<html><body>{content}</body></html>"
        mock_requests_get.return_value = mock_response
        call_command('populate_article_chunks')

        article.refresh_from_db()

        # check postgres db not empty
        self.assertEqual(article.status, Article.Status.PROCESSED)
        self.assertTrue(ArticleChunk.objects.filter(article=article).exists())

        # check milvus db not empty
        collection_name = settings.MILVUS_COLLECTION_NAME
        milvus_service = MilvusService(collection_name=collection_name)
        collection = milvus_service.get_collection()
        collection.load()
        self.assertTrue(utility.has_collection(collection_name))

        # search by text
        embeddings = milvus_service.generate_embeddings_from_text(content)
        self.assertEqual(len(embeddings), 768)

        response = milvus_service.search(query_vector=embeddings, limit=1)
        self.assertEqual(len(response), 1)

        # search by embeddings
        embeddings = milvus_service.fetch_random_vectors(limit=1)[
            "embedding"
        ]  # fetch random vectors from our collection

        self.assertEqual(len(embeddings), 768)
        response = milvus_service.search(query_vector=embeddings, limit=1)

        self.assertEqual(len(response), 1)
        chunks = ArticleChunk.objects.filter(article=article).all()
        self.assertEqual(chunks.count(), 1)
