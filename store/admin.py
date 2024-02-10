from django.contrib import admin
from .models import Product, Variation

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'product_slug' : ('product_name',)        
    }

    list_display = ('product_name', 'price', 'stock', 'category', 'updated_at', 'is_available')

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    
    # making is_active field editable directly from admin interface
    list_editable = ('is_active',)
    
    # Adding filer on the admin pannel
    list_filter = ('product', 'variation_category', 'variation_value')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)