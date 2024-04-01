from django.urls import include, path
from rest_framework import routers

from administration.api.views.article import (
    AddArticleView,
    DeleteArticleView,
    EditArticleView,
    RandomVectorsPageView,
    RandomVectorsView,
)
from administration.api.views.milvus_collection import DropMilvusCollectionView
from administration.api.views.search import SearchView

router = routers.SimpleRouter(trailing_slash=False)


urlpatterns = [
    path('add_article/', AddArticleView.as_view(), name='add_article'),
    path('edit_article/<int:article_id>/', EditArticleView.as_view(), name='edit_article'),
    path('delete_article/<int:pk>/', DeleteArticleView.as_view(), name='delete_article'),
    path('search/', SearchView.as_view(), name='search'),
    path('drop_milvus_collection/', DropMilvusCollectionView.as_view(), name='drop_milvus_collection'),
    path('embeddings_example/', RandomVectorsPageView.as_view(), name='embeddings_example_page'),
    path('random_example_embeddings/', RandomVectorsView.as_view(), name='random_example_embeddings'),
    path('', include(router.urls)),
]
