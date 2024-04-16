from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.

# getting cart_id by session key using this provate function


def _cart_id(request):
    cart = request.session.session_key

    # if there is no cart_id then creating a new one
    if not cart:
        cart = request.session.create()

    # returning the cart
    return cart


def add_to_cart(request, product_id):

    # getting the current user
    current_user = request.user

    # GETTING THE PRODUCT
    # getting the product by its id
    product = Product.objects.get(id=product_id)

    # GETTING THE PRODUCT VARIATION
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    # GETTING THE CART
    # getting the cart by using the _cart_id() using the session key
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    # if cart does not exists then creating a new one
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    # saving the cart
    cart.save()

    # GETTING THE CART-ITEM FOR AUTHENTICATED USER
    if current_user.is_authenticated:
        # checking if cart item is already present in cart or not
        is_cart_item_exists = CartItem.objects.filter(
            product=product, user=current_user).exists()
        
    # GETTING THE CART-ITEM FOR NOT AUTHENTICATED USER
    else:
         # checking if cart item is already present in cart or not
        is_cart_item_exists = CartItem.objects.filter(
            product=product, cart=cart).exists()
        
    # if already present
    if is_cart_item_exists:
        # for authenticated user
        if current_user.is_authenticated:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
        # for not authenticated user
        else:
            cart_item = CartItem.objects.filter(product=product, cart=cart)

        existing_variation_list = []
        id_list = []
        # getting all the existing variations
        for item in cart_item:
            existing_variation = item.variations.all()
            existing_variation_list.append(list(existing_variation))
            id_list.append(item.id)

        # if variation is in the exsiting variation list
        if product_variation in existing_variation_list:
            # getting current variation in existing list
            curr_item_inex = existing_variation_list.index(product_variation)
            curr_item_id = id_list[curr_item_inex]
            # getting item
            item = CartItem.objects.get(product=product, id=curr_item_id)
            item.quantity += 1
            item.save()

        # if variation is not in the exsiting variation list
        else:
            # for authenticated user
            if current_user.is_authenticated:
                item = CartItem.objects.create(
                product=product, quantity=1, user=current_user)
            # for not authenticated user
            else:
                item = CartItem.objects.create(
                product=product, quantity=1, cart=cart)
            
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()

    # if no cart is there then creating a new one
    else:
         # for authenticated user
        if current_user.is_authenticated:
            cart_item = CartItem.objects.create(
                product=product,
                user=current_user,
                quantity=1
            )
        # for not authenticated user
        else:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )
        
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')

# decrementing the cart item count
def remove_from_cart(request, product_id, cart_item_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        # if user is logged in then
        if request.user.is_authenticated:
            # finding the cart item with the basis of logged in user
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)

        # if the user is not logged in then
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            # finding the cart item with the basis of cart
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        # if more than one items then decrease the count
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()

        # if only one item then delete
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

# Remove whole item from cart
def remove_cart_item(request, product_id,  cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    # if user is logged in then
    if request.user.is_authenticated:
        # finding the cart item with the basis of logged in user
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)

    # if user is not authenticated then
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        # finding the cart item with the basis of cart
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    tax = grand_total = 0

    try:
        if request.user.is_authenticated:
            # getting the cart items depending on the logged in user
            cart_items = CartItem.objects.filter(user = request.user, is_active=True)
        else:
            # getting the cart objects from the session key with the private function
            cart = Cart.objects.get(cart_id=_cart_id(request))
            # getting all the cart items depending on the cart
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            # calculating the total price and quantity by looping over the cart items

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = total * 0.02   # tax is 2%
        grand_total = total + tax

    except Cart.DoesNotExist:
        # simply do nothing
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = grand_total = 0
    
    try:
        if request.user.is_authenticated:
            # getting the cart items depending on the logged in user
            cart_items = CartItem.objects.filter(user = request.user, is_active=True)
        else:
            # getting the cart objects from the session key with the private function
            cart = Cart.objects.get(cart_id=_cart_id(request))
            # getting all the cart items depending on the cart
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            # calculating the total price and quantity by looping over the cart items

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = total * 0.02   # tax is 2%
        grand_total = total + tax

    except Cart.DoesNotExist:
        # simply do nothing
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/checkout.html', context)
