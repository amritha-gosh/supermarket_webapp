from .models import Category, Product

def global_vars(request):
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    cart_total = 0
    cart_items_drawer = []
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(id=pid)
            subtotal = product.price * qty
            cart_total += subtotal
            cart_items_drawer.append({
                'product': product,
                'quantity': qty,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            pass
    return {
        'categories': categories,
        'cart_count': cart_count,
        'cart_total': cart_total,
        'cart_items_drawer': cart_items_drawer,  # <-- for the cart drawer in base.html
        # Add 'wishlist_count' if you like
    }

from .models import Store

def selected_store(request):
    store_key = request.session.get('store_key')
    store = Store.objects.filter(key=store_key).first() if store_key else None
    all_stores = Store.objects.all()
    return {
        'selected_store': store,
        'all_stores': all_stores,
    }

