# Possibly in administration/utils.py or within your views.py

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_article_update(article):
    article.refresh_from_db()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'articles',
        {
            'type': 'article_update',
            'message': {
                'action': 'update',
                'article': {
                    'id': article.id,
                    'title': article.title,
                    'url': article.url,
                    'status': article.status,
                    'num_chunks': article.chunks.count(),
                    'progress': article.progress(),
                    'processing_info': article.processing_info,
                },
            },
        },
    )
