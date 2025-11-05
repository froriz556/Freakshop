from cart.cart import Cart

def cart_counter(request):
    return {'cart': Cart(request)}