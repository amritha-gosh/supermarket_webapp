from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    # Cart URLs
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-success/', views.checkout_success, name='checkout_success'),
    # Orders
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    # Miscellaneous
    path('help/', views.help_page, name='help'),
    path('search/', views.search, name='search'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('deals/', views.deals, name='deals'),
    path('best-sellers/', views.best_sellers, name='best_sellers'),
    # Reviews
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
   path('cart/drawer/', views.cart_drawer, name='cart_drawer'),
   path('ajax/validate-postcode/', views.ajax_validate_postcode, name='ajax_validate_postcode'),
    path('ajax/postcode-check/', views.postcode_check, name='postcode_check'),
   path('test-postcode/', views.test_postcode_view, name='test_postcode'),
 path('test-stripe/', views.test_stripe_checkout, name='test_stripe'),
  path('select-store/', views.select_store, name='select_store'),
path('change-store/', views.change_store_in_nav, name='change_store_in_nav'),




]
