from django.contrib import admin
from .models import Category

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'category_slug' : ('category_name',)        
    }

    # displaying category_name and category_slug
    list_display = ('category_name', 'category_slug')

admin.site.register(Category, CategoryAdmin)