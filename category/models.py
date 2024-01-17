from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length = 100, unique = True)

    # A Slug is basically a short label for something, containing only 
    # letters, numbers, underscores or hyphens. They’re generally used in URLs.
    category_slug = models.SlugField(max_length = 100, unique = True)
    category_description = models.TextField()
    category_image = models.ImageField(upload_to = 'photos/categories',blank = True)
    created_at = models.DateTimeField(auto_now = True)
    updated_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        # The reverse function allows retrieving url details from 
        # the url’s.py file through the name value provided.
        return reverse('products_by_category', args=[self.category_slug])

    def __str__(self):
        return self.category_name