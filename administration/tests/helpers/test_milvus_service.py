from unittest.mock import MagicMock, patch

from django.test import TestCase

from administration.helpers.milvus_service import MilvusService


class TestMilvusService(TestCase):
    @patch('administration.helpers.milvus_service.Collection')
    def test_get_collection(self, mock_collection):
        mock_collection.side_effect = [MagicMock(name="ExistingCollection"), Exception("Collection does not exist")]

        service = MilvusService(collection_name="existing_collection")

        # Test existing collection retrieval
        collection = service.get_collection()
        self.assertIsNotNone(collection)

        # Test handling for non-existing collection
        service.collection_name = "non_existing_collection"
        with self.assertRaises(Exception) as context:
            service.get_collection()
        self.assertTrue("Collection does not exist" in str(context.exception))

    @patch('administration.helpers.milvus_service.Collection')
    def test_search(self, mock_collection_class):
        # Setup a mock collection instance
        mock_collection_instance = MagicMock()
        mock_collection_class.return_value = mock_collection_instance

        # Mocking the search method's return value to simulate Milvus search results
        # Assume the search method returns a list of (lists of) SearchResult objects or similar structure
        # Here, we simulate this with a simplified structure: a list of lists of strings
        mock_search_results = [[MagicMock()]]
        mock_search_results[0][0].id = "mock_result"
        mock_collection_instance.search.return_value = mock_search_results

        service = MilvusService(collection_name="test_collection")
        query_vector = [0.1, 0.2, 0.3]  # Example query vector
        results = service.search(query_vector=query_vector, limit=5)

        self.assertEqual(results[0][0].id, "mock_result")
        mock_collection_instance.search.assert_called_once()

    @patch('administration.helpers.milvus_service.connections')
    def test_connect_to_milvus(self, mock_connections):
        service = MilvusService(collection_name="test_collection")
        service.connect()
        mock_connections.connect.assert_called_once_with(alias='default', host='milvus-standalone', port=19530)

    @patch('administration.helpers.milvus_service.Collection')
    def test_create_index_on_collection(self, mock_collection):
        mock_collection_instance = MagicMock()
        mock_collection.return_value = mock_collection_instance

        service = MilvusService(collection_name="test_collection")
        service.create_index()

        # Verify that an index is created on the collection with the specified parameters
        mock_collection_instance.create_index.assert_called_once_with(
            "embedding", {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 100}}
        )
