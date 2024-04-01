from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pymilvus import utility

from administration.api.enums import ProcessingMessages
from administration.helpers.milvus_service import MilvusService


@method_decorator(csrf_exempt, name='dispatch')
class DropMilvusCollectionView(View):
    def truncate_tables(self, table_names: list) -> None:
        with connection.cursor() as cursor:
            for table_name in table_names:
                cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE;')

    def get(self, request, *args, **kwargs):
        collection_name = settings.MILVUS_COLLECTION_NAME
        milvus_service = MilvusService(collection_name=collection_name)
        milvus_service.connect()

        self.truncate_tables(['administration_article', 'administration_articlechunk'])

        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
            return JsonResponse({'message': ProcessingMessages.MILVUS_COLLECTION_DROPPED_SUCCESSFULLY.value})
        return JsonResponse({'message': ProcessingMessages.MILVUS_COLLECTION_DOES_NOT_EXIST.value})
