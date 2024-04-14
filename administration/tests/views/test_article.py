from django.test import TestCase
from django.urls import reverse

from administration.models import Article, ArticleChunk
from administration.api.enums import ProcessingMessages
from administration.helpers.milvus_service import MilvusService
from pymilvus import utility
from django.test import override_settings

class ArticleViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article = Article.objects.create(title="Test Article")
        cls.edit_url = reverse('edit_article', args=[cls.article.id])

        ArticleChunk.objects.create(text="Test Article 1", article=cls.article)
        ArticleChunk.objects.create(text="Test Article 2", article=cls.article)

    def test_delete_article(self):
        response = self.client.post(reverse('delete_article', args=[self.article.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())
        self.assertFalse(ArticleChunk.objects.filter(article=self.article).exists())

    @override_settings(MILVUS_COLLECTION_NAME="article_embeddings_test")
    def test_drop_milvus_collection_which_does_not_exist(self):
        response = self.client.get(reverse('drop_milvus_collection'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], ProcessingMessages.MILVUS_COLLECTION_DOES_NOT_EXIST.value)

    @override_settings(MILVUS_COLLECTION_NAME="article_embeddings_test")
    def test_drop_milvus_collection(self):
        ArticleChunk.objects.create(text="Test Article 1", article=self.article)
        ArticleChunk.objects.create(text="Test Article 2", article=self.article)
        collection_name = "article_embeddings_test"

        milvus_service = MilvusService(collection_name=collection_name)
        milvus_service.connect()
        collection = milvus_service.create_collection()
        collection.load()
        self.assertTrue(utility.has_collection(collection_name))

        response = self.client.get(reverse('drop_milvus_collection'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], ProcessingMessages.MILVUS_COLLECTION_DROPPED_SUCCESSFULLY.value)
        self.assertFalse(ArticleChunk.objects.filter(article=self.article).exists())
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_list_articles(self):
        response = self.client.get(reverse('add_article'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['articles']), 1)
        self.assertEqual(response.context['articles'][0], self.article)
        self.assertEqual(response.context['articles'][0].chunks.count(), 2)
        self.assertEqual(response.context['articles'][0].chunks.first().article, self.article)


