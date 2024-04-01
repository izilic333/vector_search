import factory

from administration.models import Article, ArticleChunk


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Faker('sentence', nb_words=6)
    url = factory.Faker('url')
    status = Article.Status.NOT_PROCESSED
    summary = factory.Faker('text', max_nb_chars=200)


class ArticleChunkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArticleChunk

    article = factory.SubFactory(ArticleFactory)
    text = factory.Faker('text', max_nb_chars=1000)
    chunk_order = factory.Faker('random_int', min=1)
    text_hash = factory.Faker('sha256')
    word_count = factory.Faker('random_int', min=100, max=1000)
    is_processed = factory.Faker('boolean')
