from django.shortcuts import get_object_or_404, render
from category.models import Category
from .models import Product
# Create your views here.
def store(request, category_slug = None):
    
    categories = None
    products = None

    # if category_slug is not None
    if category_slug != None:
        # getting category by category_slug
        categories = get_object_or_404(Category, category_slug = category_slug)
        # getting products by category_slug
        products = Product.objects.filter(category = categories, is_available = True)
        products_count = products.count()

    # if category_slug is None    
    else:
        products = Product.objects.all().filter(is_available = True)
        products_count = products.count()

    context = {
        'products' : products,
        'products_count' : products_count,
    }
    return render(request, 'store/store.html', context)

def product_details(request, category_slug, product_slug):
    try:
        # category__category_slug means we are refering cate_slug of category model.
        # double unserscore __ means accessing models propoerty directly.
        product = Product.objects.get(category__category_slug = category_slug, product_slug = product_slug)
    
    except Exception as e:
        raise e
    
    context = {
        'product' : product,
    }
    return render(request, 'store/product_details.html', context)