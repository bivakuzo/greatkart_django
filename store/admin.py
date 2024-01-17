from django.contrib import admin
from .models import Product

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'product_slug' : ('product_name',)        
    }

    list_display = ('product_name', 'price', 'stock', 'category', 'updated_at', 'is_available')

admin.site.register(Product, ProductAdmin)