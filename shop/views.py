from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .forms import AddressForm, CheckoutForm
from .models import (
    Category, Product, Brand, Banner, Review,
    Order, OrderItem, DiscountCode, Wishlist, Store, StoreStock
)
from .utils import get_store_for_postcode
import stripe
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

MINIMUM_ORDER_TOTAL = 40.00

# HOMEPAGE

def home(request):
    store_key = request.session.get('store_key')
    store = Store.objects.filter(key=store_key).first()

    if store:
        in_stock_products = StoreStock.objects.filter(store=store, qty__gt=0).values_list('product_id', flat=True)
        featured_products = Product.objects.filter(id__in=in_stock_products, featured=True)[:10]
        most_popular_products = Product.objects.filter(id__in=in_stock_products, featured=True)[:10]
        starter_products = Product.objects.filter(id__in=in_stock_products)[:10]
    else:
        featured_products = Product.objects.filter(featured=True)[:10]
        most_popular_products = Product.objects.filter(featured=True)[:10]
        starter_products = Product.objects.all()[:10]

    banners = Banner.objects.filter(active=True).order_by('order')[:4]
    categories = Category.objects.all()[:12]
    brands = Brand.objects.all()[:8]
    reviews = Review.objects.order_by('-created_at')[:6]
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    cart_total = sum(Product.objects.filter(id=pid).first().price * qty for pid, qty in cart.items() if Product.objects.filter(id=pid).exists())

    return render(request, 'shop/home.html', {
        'banners': banners,
        'categories': categories,
        'featured_products': featured_products,
        'most_popular_products': most_popular_products,
        'starter_products': starter_products,
        'brands': brands,
        'reviews': reviews,
        'cart_count': cart_count,
        'cart_total': cart_total,
    })


def about_us(request):
    return render(request, "shop/about_us.html")


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    store_key = request.session.get('store_key')
    store = Store.objects.filter(key=store_key).first()

    if store:
        in_stock_products = StoreStock.objects.filter(store=store, qty__gt=0).values_list('product_id', flat=True)
        products = category.products.filter(id__in=in_stock_products)
    else:
        products = category.products.all()

    return render(request, 'shop/category_products.html', {
        'category': category,
        'products': products
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, "Product added to cart!")
    return redirect(request.META.get('HTTP_REFERER', '/'))


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    messages.info(request, "Product removed from cart.")
    return redirect('cart')


def update_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart[str(product_id)] = quantity
        else:
            cart.pop(str(product_id), None)
        request.session['cart'] = cart
    return redirect('cart')

def cart(request):
    cart_data = request.session.get('cart', {})
    store_key = request.session.get('store_key')
    selected_store = Store.objects.filter(key=store_key).first()

    products = Product.objects.filter(id__in=cart_data.keys())
    cart_items = []
    subtotal = Decimal("0.00")
    stock_errors = []
    discount = Decimal("0.00")
    code = ''

    for product in products:
        qty = cart_data.get(str(product.id), 0)
        stock_qty = 0
        stock_msg = ""

        if selected_store:
            stock_obj = StoreStock.objects.filter(store=selected_store, product=product).first()
            if stock_obj:
                stock_qty = stock_obj.qty

        if stock_qty == 0:
            stock_msg = "Out of stock"
        elif qty > stock_qty:
            stock_msg = f"Only {stock_qty} left"

        if stock_msg:
            stock_errors.append({'product_id': product.id, 'message': stock_msg})

        line_total = product.price * qty
        subtotal += line_total

        cart_items.append({
            'product': product,
            'quantity': qty,
            'subtotal': line_total,
        })

    if request.method == 'POST':
        code = request.POST.get('discount_code', '').strip()
        if code:
            try:
                dc = DiscountCode.objects.get(code__iexact=code, active=True)
                discount = subtotal * (Decimal(dc.discount_percent) / Decimal("100"))
                messages.success(request, f"Discount applied: {dc.discount_percent}% off (−£{discount:.2f})!")
            except DiscountCode.DoesNotExist:
                messages.error(request, "That discount code is invalid or expired.")

    total = subtotal - discount
    out_of_stock = len(stock_errors) > 0

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'code': code,
        'min_order': MINIMUM_ORDER_TOTAL,
        'stock_errors': stock_errors,
        'out_of_stock': out_of_stock,
        'store_key': store_key,
    })

def cart_drawer(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items, total = [], 0
    for product in products:
        quantity = cart.get(str(product.id), 0)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    html = render_to_string('shop/cart_drawer.html', {'cart_items': cart_items, 'total': total}, request=request)
    return JsonResponse({'html': html})

def checkout(request):
    if request.method == "GET":
        # Don't allow GET requests directly
        messages.error(request, "Please check your cart before proceeding to checkout.")
        return redirect("cart")
    cart = request.session.get('cart', {})
    store_key = request.session.get('store_key')

    if not store_key:
        messages.error(request, "Please select your store first.")
        return redirect('select_store')

    try:
        store = Store.objects.get(key=store_key)
    except Store.DoesNotExist:
        messages.error(request, "Invalid store selection.")
        return redirect('select_store')

    # Build cart items
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0

    for product in products:
        qty = cart[str(product.id)]
        subtotal = product.price * qty
        total += subtotal
        cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})

    # Minimum order check
    if total < MINIMUM_ORDER_TOTAL:
        messages.error(request, f"Minimum order is £{MINIMUM_ORDER_TOTAL:.2f}. Your total is £{total:.2f}.")
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data

            # Check stock for each product
            out_of_stock = []
            for item in cart_items:
                product = item['product']
                qty_needed = item['quantity']
                stock = StoreStock.objects.filter(store=store, product=product).first()
                available = stock.qty if stock else 0
                if available < qty_needed:
                    out_of_stock.append(f"{product.name} (Only {available} left)")

            if out_of_stock:
                for msg in out_of_stock:
                    messages.error(request, msg)
                return redirect('cart')

            # Create order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                first_name=cleaned['first_name'],
                last_name=cleaned['last_name'],
                email=cleaned['email'],
                phone=cleaned['phone'],
                address=cleaned['address'],
                address2=cleaned['address2'],
                city=cleaned['city'],
                postcode=cleaned['postcode'],
                notes=cleaned['notes'],
                total_amount=total,
                paid=False,
                payment_method=cleaned['payment_method'],
                store_key=store.key,
                store_name=store.name,
            )

            # Create order items & reduce stock
            for item in cart_items:
                p = item['product']
                qty = item['quantity']
                OrderItem.objects.create(order=order, product=p, quantity=qty, price=p.price)
                ss = StoreStock.objects.get(store=store, product=p)
                ss.qty -= qty
                ss.save()

            # Notify store admin
            if store.email:
                subject = f"🛒 New Order #{order.id} from {order.first_name}"
                message = render_to_string('shop/emails/store_notification.txt', {'order': order})
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [store.email],
                    fail_silently=True
                )

            if cleaned['payment_method'] == 'card':
                # Stripe payment session
                stripe.api_key = settings.STRIPE_SECRET_KEY
                try:
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[
                            {
                                'price_data': {
                                    'currency': 'gbp',
                                    'unit_amount': int(item['product'].price * 100),
                                    'product_data': {'name': item['product'].name},
                                },
                                'quantity': item['quantity'],
                            } for item in cart_items
                        ],
                        mode='payment',
                        success_url=request.build_absolute_uri('/checkout-success/?session_id={CHECKOUT_SESSION_ID}'),
                        cancel_url=request.build_absolute_uri('/cart/'),
                        customer_email=cleaned['email'],
                    )
                    order.stripe_session_id = session.id
                    order.save()
                    return redirect(session.url)
                except Exception as e:
                    messages.error(request, f"Stripe error: {e}")
                    return redirect('cart')

            else:  # Cash on Delivery
                request.session['cart'] = {}
                return render(request, 'shop/checkout_success.html', {
                    'cod_success': True,
                    'order': order
                })

        else:
            messages.error(request, "Please fix the form errors below.")
    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'form': form,
        'store_key': store.key
    })

def checkout_success(request):
    session_id = request.GET.get("session_id")
    if session_id:
        try:
            order = Order.objects.get(stripe_session_id=session_id)
            order.paid = True
            order.save()
            for item in order.items.all():
                item.product.stock -= item.quantity
                item.product.save()
            subject = f"Order #{order.id} Confirmation"
            message = render_to_string('shop/emails/order_confirmation.txt', {'order': order})
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email])
            request.session['cart'] = {}
        except Order.DoesNotExist:
            pass
    return render(request, 'shop/checkout_success.html')

def ajax_validate_postcode(request):
    postcode = request.GET.get('postcode', '').strip().replace(' ', '').upper()
    if not postcode:
        return JsonResponse({'valid': False, 'message': 'Please enter a postcode.'})

    store_key = request.session.get('store_key')
    if not store_key:
        return JsonResponse({'valid': False, 'message': 'Please select your store first.'})

    store, distance = get_store_for_postcode(postcode)

    if not store:
        return JsonResponse({
            'valid': False,
            'message': "❌ Sorry, we do not deliver to this postcode."
        })

    if store['key'] != store_key:
        return JsonResponse({
            'valid': False,
            'message': f"❌ This postcode is outside the delivery area for {store_key.title()}. Please change your store."
        })

    return JsonResponse({
        'valid': True,
        'store': store['name'],
        'distance': round(distance, 2),
        'message': f"✅ Delivery available from {store['name']}.",
        'store_key': store['key']
    })


def postcode_check(request):
    postcode = request.GET.get('postcode', '').replace(' ', '').upper()
    if not postcode:
        return JsonResponse({"deliverable": False, "message": "Please enter a postcode."})

    store_key = request.session.get('store_key')
    if not store_key:
        return JsonResponse({"deliverable": False, "message": "Please select your store first."})

    store, distance = get_store_for_postcode(postcode)

    if not store:
        return JsonResponse({
            "deliverable": False,
            "message": "❌ This postcode is outside the delivery area for any store.",
        })

    if store['key'] != store_key:
        return JsonResponse({
            "deliverable": False,
            "message": f"❌ This postcode is outside the delivery area for {store_key.title()}. Please change your store.",
        })

    return JsonResponse({
        "deliverable": True,
        "store_name": store['name'],
        "store_key": store['key'],
        "distance": round(distance, 2),
        "message": f"✅ Delivery available from {store['name']}."
    })

# ----------- OTHER VIEWS -----------
def wishlist(request):
    return render(request, 'shop/wishlist.html')

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    messages.success(request, "Added to your wishlist!")
    return redirect('product_detail', product_id=product_id)

def deals(request):
    return render(request, 'shop/deals.html')

def best_sellers(request):
    return render(request, 'shop/best_sellers.html')

def help_page(request):
    return render(request, 'shop/help.html')

def search(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'shop/search.html', {'results': results, 'query': query})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment,
        )
        messages.success(request, "Review submitted!")
        return redirect('product_detail', product_id=product.id)
    return redirect('product_detail', product_id=product.id)

def test_postcode_view(request):
    postcode = request.GET.get('postcode', 'WN13DG')  # Default Wigan area
    store, dist = get_store_for_postcode(postcode)
    if store:
        return HttpResponse(f"✅ Deliverable to {postcode} — Store: {store['name']} ({dist:.2f} miles)")
    return HttpResponse(f"❌ Not deliverable to {postcode}")

def test_stripe_checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'gbp',
                        'product_data': {'name': 'Test Product'},
                        'unit_amount': 1000,  # £10.00
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/checkout-success/'),
            cancel_url=request.build_absolute_uri('/cart/'),
            customer_email='test@example.com',
        )
        return redirect(session.url)
    except Exception as e:
        return HttpResponse(f"❌ Stripe error: {e}")

def select_store(request):
    stores = Store.objects.all()

    if request.method == 'POST':
        selected_store = request.POST.get('store_key')
        if selected_store:
            request.session['store_key'] = selected_store
            request.session['cart'] = {}  # Clear cart
            return redirect('home')

    return render(request, 'shop/select_store.html', {'stores': stores})

from django.views.decorators.http import require_POST

@require_POST
def change_store_in_nav(request):
    store_key = request.POST.get('store_key')
    if Store.objects.filter(key=store_key).exists():
        request.session['store_key'] = store_key
        request.session['cart'] = {}  # Clear cart when store changes
        messages.success(request, "Store changed successfully. Cart has been reset.")
    else:
        messages.error(request, "Invalid store selection.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))



