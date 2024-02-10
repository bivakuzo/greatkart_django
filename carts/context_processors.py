from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    # if admin login then nothing
    if 'admin' in request.path:
        return {}
    # if customer page then
    else:
        try:
            # getting the cart
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            # getting all the cart items
            cart_items = CartItem.objects.all()
            # looping through the items in cart
            for cart_item in cart_items:
                # incrementing the counter
                cart_count += cart_item.quantity
        # if no cart is there
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count = cart_count)