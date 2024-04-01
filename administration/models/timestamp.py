from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_('Created At'), auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name=_('Last modified'), auto_now=True)

    # This is an abstract model, so it won't create a separate table in the database
    class Meta:
        abstract = True
