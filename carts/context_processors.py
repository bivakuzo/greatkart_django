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
            
            # if any user is logged in then,
            if request.user.is_authenticated:
                # show the cart counter for the looged in user's cart
                cart_items = CartItem.objects.all().filter(user = request.user)

            # if no user is logged in then,
            else:
                # getting the latest cart item from all the cart items
                cart_items = CartItem.objects.all().filter(cart = cart[:1])

            # looping through the items in cart
            for cart_item in cart_items:
                # incrementing the counter
                cart_count += cart_item.quantity

        # if no cart is there
        except Cart.DoesNotExist:
            cart_count = 0

    return dict(cart_count = cart_count)