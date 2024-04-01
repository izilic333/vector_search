from django.db import models

from administration.models.timestamp import TimestampedModel


class Article(TimestampedModel):
    class Status(models.TextChoices):
        NOT_PROCESSED = 'not_processed', 'Not Processed'
        IN_PROGRESS = 'in_progress', 'In Progress'
        PROCESSED = 'processed', 'Processed'
        ERROR = 'error'

    title = models.CharField(max_length=255, unique=True)
    url = models.URLField(unique=True)
    summary = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status, default=Status.NOT_PROCESSED)
    processing_info = models.CharField(max_length=255, blank=True)

    def progress(self):
        total_chunks = self.chunks.count()
        processed_chunks = self.chunks.filter(is_processed=True).count()
        return (processed_chunks / total_chunks) * 100 if total_chunks > 0 else 0

    def __str__(self):
        return self.title


class ArticleChunk(models.Model):
    article = models.ForeignKey(Article, related_name='chunks', on_delete=models.CASCADE)
    text = models.TextField()
    chunk_order = models.IntegerField(default=0)
    text_hash = models.CharField(max_length=64, unique=True, blank=True, null=True)
    word_count = models.IntegerField(default=0)
    is_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['chunk_order']

    def __str__(self):
        return f"Chunk {self.chunk_order} of {self.article.title}"
