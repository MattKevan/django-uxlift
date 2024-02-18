from django.utils.text import slugify
from django.db import models

# Slugify
class UniqueSlugMixin:
    """
    Mixin class to generate a unique slug for a model.
    """

    def generate_unique_slug(self, model_instance, name, slug_field_name='slug'):
        slug = slugify(name)
        original_slug = slug
        counter = 1

        while model_instance.objects.filter(**{slug_field_name: slug}).exclude(pk=self.pk).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        return slug

    def save(self, *args, **kwargs):
        if not getattr(self, 'slug', None):
            self.slug = self.generate_unique_slug(self.__class__, self.name)
        super().save(*args, **kwargs)
