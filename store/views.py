from django.shortcuts import get_object_or_404, render
from category.models import Category
from .models import Product
from carts.models import CartItem
from carts.views import _cart_id

# imporing paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# Importing Q
from django.db.models import Q

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
         # we are showing 1 product in one page
        paginator = Paginator(products, 1)
        # getting the page from url using GET request, like, page_url/?page=2
        page = request.GET.get('page')
        # with the page number showing the products
        paged_products = paginator.get_page(page)
        products_count = products.count()

    # if category_slug is None    
    else:
        products = Product.objects.all().filter(is_available = True)
        # we are showing 3 products in one page
        paginator = Paginator(products, 3)
        # getting the page from url using GET request, like, page_url/?page=2
        page = request.GET.get('page')
        # with the page number showing the products
        paged_products = paginator.get_page(page)
        products_count = products.count()

    context = {
        # 'products' : products,
        # instead of all products we are only passing the specified number of products
        'products' : paged_products,
        'products_count' : products_count,
    }
    return render(request, 'store/store.html', context)

def product_details(request, category_slug, product_slug):
    try:
        # category__category_slug means we are refering cate_slug of category model.
        # double unserscore __ means accessing models propoerty directly.
        product = Product.objects.get(category__category_slug = category_slug, product_slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = product).exists()
    
    except Exception as e:
        raise e
    
    context = {
        'product' : product,
        'in_cart' : in_cart,
    }
    return render(request, 'store/product_details.html', context)

def search(request):
    # if keyword is in the url
    if 'keyword' in request.GET:
        # storing the keyword
        keyword = request.GET['keyword']
        # if keyword is not blank
        if keyword:
            # here description__icontains means it will find the keyword in the full description
            # products = Product.objects.filter(description__icontains = keyword)

            # in django filter , means AND operation and for OR in we need to use QuerySet Q like below
            products = Product.objects.filter(Q(description__icontains = keyword) | Q(product_name__icontains = keyword))
            products_count = products.count()

    context = {
        'products' : products,
        'products_count' : products_count,
    }
    return render(request, 'store/store.html', context)