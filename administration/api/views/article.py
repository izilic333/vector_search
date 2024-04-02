from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, TemplateView,
                                  UpdateView, View)
from pymilvus import Collection, connections, utility

from administration.forms import ArticleForm
from administration.helpers.milvus_service import MilvusService
from administration.models import Article
from administration.tasks import task_populate_article_chunks


class AddArticleView(CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'administration/add_article.html'
    success_url = reverse_lazy('add_article')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.all()  #
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        task_populate_article_chunks.apply_async()

        return response


class EditArticleView(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'administration/edit_article.html'
    pk_url_kwarg = 'article_id'
    success_url = reverse_lazy('add_article')


class DeleteArticleView(DeleteView):
    model = Article
    template_name = 'administration/confirm_delete.html'
    success_url = reverse_lazy('add_article')

    def post(self, *args, **kwargs):
        connections.connect(alias="default", host="milvus-standalone", port="19530")
        collection_name = "article_embeddings"
        article = self.get_object()
        chunk_ids = list(article.chunks.values_list('id', flat=True))
        if utility.has_collection(collection_name):
            collection = Collection(name=collection_name)
            expr = f"id in {chunk_ids}"
            collection.delete(expr)

        super().delete(*args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())


class RandomVectorsPageView(TemplateView):
    template_name = 'administration/fetch_example_vectors.html'


class RandomVectorsView(View):
    milvus_service = MilvusService(collection_name="article_embeddings")

    def get(self, request, *args, **kwargs):
        random_vectors = self.milvus_service.fetch_random_vectors()
        return JsonResponse(random_vectors)
