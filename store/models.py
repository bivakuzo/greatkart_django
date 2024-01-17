from django.db import models
from django.urls import reverse
from category.models import Category

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length = 200, unique = True)
    product_slug = models.SlugField(max_length = 200, unique = True)
    description = models.TextField(blank = True)
    price = models.IntegerField()
    image = models.ImageField(upload_to = 'photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default = True)
    # CASCADE means if the category is deleted then
    # all products of that category will also be deleted
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now = True)
    updated_at = models.DateTimeField(auto_now_add = True)

    
    def get_url(self):
        return reverse('product_details', args=[self.category.category_slug, self.product_slug])
    
    def __str__(self):
        return self.product_name
