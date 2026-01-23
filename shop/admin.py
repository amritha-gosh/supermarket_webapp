from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Sum
from django.contrib.admin import AdminSite

from .models import (
    Brand, Category, Product, ProductImage, Review,
    DiscountCode, Banner, Address,
    Store, StoreStock, NewsletterSubscriber,
    Order, OrderItem
)

# --- Inlines ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'store_name', 'total_amount', 'paid', 'created_at']
    list_filter = ['store_name', 'paid', 'payment_method', 'created_at']  # This shows sidebar filters
    search_fields = ['email', 'first_name', 'last_name', 'store_name']

admin.site.register(Order, OrderAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False
    verbose_name = "Line item"
    verbose_name_plural = "Line items"

# --- Per-Model Admins ---
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display   = ('name', 'category', 'brand', 'price', 'stock', 'featured', 'is_offer')
    list_filter    = ('category', 'brand', 'featured', 'is_offer')
    search_fields  = ('name', 'category__name', 'brand__name')
    inlines        = (ProductImageInline,)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ('product', 'user', 'rating', 'created_at')
    search_fields = ('product__name', 'user__username')

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display   = ('code', 'discount_percent', 'active', 'expiry_date', 'usage_limit')
    list_editable  = ('active',)
    search_fields  = ('code',)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display   = ('title', 'order', 'active')
    list_editable  = ('order', 'active')
    search_fields  = ('title',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display   = ('user', 'name', 'city', 'postcode', 'default')
    search_fields  = ('user__username', 'name', 'city', 'postcode')

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display   = ('name', 'key', 'active', 'lat', 'lon')
    search_fields  = ('name', 'key')

@admin.register(StoreStock)
class StoreStockAdmin(admin.ModelAdmin):
    list_display   = ('store', 'product', 'qty')
    list_filter    = ('store',)
    search_fields  = ('product__name',)

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display   = ('email', 'subscribed_at', 'active')
    list_editable  = ('active',)
    search_fields  = ('email',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')

# --- Shared OrderAdmin for all sites ---
class BaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'first_name', 'last_name', 'email',
        'store_name', 'total_amount', 'paid', 'created_at'
    )
    readonly_fields = (
        'stripe_session_id', 'created_at',
        'first_name', 'last_name', 'email', 'phone',
        'address', 'address2', 'city', 'postcode', 'notes',
        'store_key', 'store_name'
    )
    list_filter = ('paid', 'store_key', 'created_at')
    search_fields = ('id', 'first_name', 'last_name', 'email', 'postcode')
    ordering = ('-created_at',)
    inlines = (OrderItemInline,)

# --- Per-store OrderAdmins ---
class WiganOrderAdmin(BaseOrderAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(store_key='wigan')

class SouthportOrderAdmin(BaseOrderAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(store_key='southport')

class WiganAdminSite(AdminSite):
    site_header = "Spicexpress — Wigan"

class SouthportAdminSite(AdminSite):
    site_header = "Spicexpress — Southport"

wigan_admin     = WiganAdminSite(name='wigan_admin')
southport_admin = SouthportAdminSite(name='southport_admin')

wigan_admin.register(Order, WiganOrderAdmin)
southport_admin.register(Order, SouthportOrderAdmin)

# --- Main AdminSite with Dashboard ---
class MyAdminSite(AdminSite):
    site_header = "Spicexpress Admin"
    site_title  = "Spicexpress"
    index_title = "Dashboard"
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('dashboard/', self.admin_view(self.dashboard_view), name="dashboard"),
        ]
        return custom + urls
    def dashboard_view(self, request):
        from django.utils import timezone
        today = timezone.now().date()
        orders_today = Order.objects.filter(created_at__date=today, paid=True)
        total_sales_today = orders_today.aggregate(total=Sum('total_amount'))['total'] or 0
        top_items = (
            OrderItem.objects
            .filter(order__created_at__date=today)
            .values('product__name')
            .annotate(qty=Sum('quantity'))
            .order_by('-qty')[:20]
        )
        low_stock = Product.objects.filter(stock__lt=10)[:20]
        return TemplateResponse(request, "admin/dashboard.html", {
            'orders_today': orders_today,
            'total_sales_today': total_sales_today,
            'top_items': top_items,
            'low_stock': low_stock,
        })

my_admin_site = MyAdminSite(name='myadmin')
my_admin_site.register(Brand, BrandAdmin)
my_admin_site.register(Category, CategoryAdmin)
my_admin_site.register(Product, ProductAdmin)
my_admin_site.register(ProductImage)
my_admin_site.register(Review, ReviewAdmin)
my_admin_site.register(DiscountCode, DiscountCodeAdmin)
my_admin_site.register(Banner, BannerAdmin)
my_admin_site.register(Address, AddressAdmin)
my_admin_site.register(Store, StoreAdmin)
my_admin_site.register(StoreStock, StoreStockAdmin)
my_admin_site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)
my_admin_site.register(Order, BaseOrderAdmin)
my_admin_site.register(OrderItem, OrderItemAdmin)
