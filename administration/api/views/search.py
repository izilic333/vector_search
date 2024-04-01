import json
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from administration.api.enums import ProcessingMessages
from administration.helpers.milvus_service import MilvusService
from administration.models import ArticleChunk

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class SearchView(TemplateView):
    """
    View for searching the Milvus collection for similar article chunks based on a query vector or text input.

    returns: Renders the search.html template with the search results.
    """

    template_name = 'administration/search.html'
    milvus_service = MilvusService(collection_name="article_embeddings")

    def post(self, request, *args, **kwargs):
        context = {'query': '', 'results': []}
        top_n_results = request.POST.get("topN", 10)

        self.milvus_service.connect()
        if self.milvus_service.is_chunks_empty():
            context.update({'error': ProcessingMessages.MILVUS_DATABASE_EMPTY.value})
            return self.render_to_response(context)
        query_input = request.POST.get('query', '')
        if self.is_valid_json_object_or_array(query_input):
            query = json.loads(query_input)
            if query and len(query) != self.milvus_service.dim:
                message = ProcessingMessages.MILVUS_QUERY_VECTOR_MISMATCH.value.format(
                    self.milvus_service.dim, len(query)
                )
                logger.error(message)
                context.update({'error': message})
                return self.render_to_response(context)
        else:
            query = self.milvus_service.generate_embeddings_from_text(query_input)

        search_results = self.milvus_service.search(query, limit=int(top_n_results))
        self.update_context_with_results(context, search_results, request)
        return self.render_to_response(context)

    def is_valid_json_object_or_array(self, string: str) -> bool:
        try:
            parsed = json.loads(string)
        except ValueError:
            return False
        return isinstance(parsed, dict | list)

    def update_context_with_results(self, context, search_results, request):
        results = [
            {'chunk_id': str(result.id), 'similarity': 1 / (1 + result.distance), 'distance': result.distance}
            for result in search_results[0]
        ]
        results.sort(key=lambda x: x['similarity'], reverse=True)

        nearest_neighbor_ids = [result['chunk_id'] for result in results]

        # Fetch chunks matching the IDs with additional info
        chunks_query = ArticleChunk.objects.filter(id__in=nearest_neighbor_ids).values(
            'id', 'text', 'article__title', 'article__url'
        )

        chunks_dict = {str(chunk['id']): chunk for chunk in chunks_query}

        for result in results:
            chunk = chunks_dict.get(result['chunk_id'])
            if chunk:
                result.update(
                    {
                        'text': chunk['text'],
                        'article_title': chunk['article__title'],
                        'article_url': chunk['article__url'],
                    }
                )

        context.update(
            {
                'query': request.POST.get('query', ''),
                'results': results,
                'topN': request.POST.get('topN', '10'),
            }
        )
