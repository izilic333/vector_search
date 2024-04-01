from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from administration.models import Article, ArticleChunk


class MockSearchResult:
    def __init__(self, id, distance):
        self.id = id
        self.distance = distance


class SearchViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        article = Article.objects.create(title="Test Article")
        ArticleChunk.objects.create(text="Test Article 1", article=article)
        ArticleChunk.objects.create(text="Test Article 2", article=article)

    @patch('administration.helpers.milvus_service.MilvusService.connect')
    @patch('administration.helpers.milvus_service.MilvusService.is_chunks_empty')
    @patch('administration.helpers.milvus_service.MilvusService.search')
    @patch('administration.helpers.milvus_service.MilvusService.generate_embeddings_from_text')
    def test_search_with_query_vector(self, mock_generate_embeddings, mock_search, mock_is_chunks_empty, mock_connect):
        mock_connect.return_value = None
        mock_is_chunks_empty.return_value = False
        mock_search.return_value = [
            [MockSearchResult(id=1, distance=0.1), MockSearchResult(id=2, distance=0.2)],
            [MockSearchResult(id=3, distance=0.3), MockSearchResult(id=4, distance=0.4)],
        ]
        mock_generate_embeddings.return_value = [0.1, 0.2, 0.3]  # Assuming this is how embeddings are generated

        # Simulate POST request with direct query vector input
        response = self.client.post(
            reverse('search'), {'embeddings': "[0.1, 0.2, 0.3]"}, content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context_data)
        self.assertNotIn('error', response.context_data)
        mock_search.assert_called_once_with([0.1, 0.2, 0.3])

        actual_results = response.context_data['results']
        self.assertEqual(len(actual_results), 2)
        self.assertIn('chunk_id', actual_results[0])
        self.assertAlmostEqual(actual_results[0]['similarity'], 0.9090909090909091)
        self.assertAlmostEqual(actual_results[1]['similarity'], 0.8333333333333334)

        self.assertIn('nearest_neighbor_chunks', response.context_data)

    @patch('administration.helpers.milvus_service.MilvusService.connect')
    @patch('administration.helpers.milvus_service.MilvusService.is_chunks_empty')
    @patch('administration.helpers.milvus_service.MilvusService.search')
    @patch('administration.helpers.milvus_service.MilvusService.generate_embeddings_from_text')
    def test_search_with_text_input(self, mock_generate_embeddings, mock_search, mock_is_chunks_empty, mock_connect):
        # Mock the MilvusService responses
        mock_connect.return_value = None
        mock_is_chunks_empty.return_value = False
        mock_generate_embeddings.return_value = [0.1, 0.2, 0.3]
        mock_search.return_value = [[MockSearchResult(id=1, distance=0.1)]]

        # Perform a POST request to the view with text input
        response = self.client.post(reverse('search'), {'query': 'Example search text'})

        # Check the response status and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/search.html')

        expected_results = [{'chunk_id': '1', 'similarity': 1 / (1 + 0.1)}]
        self.assertEqual(response.context['results'], expected_results)
        self.assertIn('query', response.context)
        self.assertEqual(response.context['query'], 'Example search text')
