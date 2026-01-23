from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True, default=None)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, default=None)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=100, default="Unnamed Product")
    description = models.TextField(blank=True, null=True, default='')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=None)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, default=None)

    UNIT_CHOICES = (
        ('item', 'Per Item'),
        ('kg', 'Per Kilogram'),
        ('g', 'Per Gram'),
    )
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='item')

    stock = models.PositiveIntegerField(default=0)
    is_offer = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('name', 'category')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    # ✅ Updated to match your StoreStock.qty field
    def get_stock_for_store(self, store_key):
        """
        Returns the stock available for this product in a specific store.
        If not found, returns 0.
        """
        try:
            return self.stocks.get(store__key=store_key).qty
        except:
            return 0

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='product_images/gallery/', blank=True, null=True, default=None)
    def __str__(self):
        return f"{self.product.name} Gallery"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50, blank=True, null=True, default='', help_text="For guests, enter your name.")
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f'{self.user.username if self.user else self.name} - {self.product.name}'

class DiscountCode(models.Model):
    code = models.CharField(max_length=20, unique=True, default='DISCOUNT')
    discount_percent = models.PositiveSmallIntegerField(help_text="Value between 1 and 100", default=10)
    active = models.BooleanField(default=True)
    expiry_date = models.DateField(default='2030-12-31')
    usage_limit = models.PositiveIntegerField(default=1)
    def __str__(self):
        return self.code

class Banner(models.Model):
    title = models.CharField(max_length=100, default='Banner')
    description = models.TextField(blank=True, null=True, default='')
    image = models.ImageField(upload_to='banner_images/', blank=True, null=True, default=None)
    link = models.URLField(blank=True, null=True, default=None)
    cta_label = models.CharField(max_length=30, blank=True, null=True, default='')
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return self.title

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=255, default='Customer')
    phone = models.CharField(max_length=30, default='0000000000')
    address_line1 = models.CharField(max_length=255, default='Address line 1')
    address_line2 = models.CharField(max_length=255, blank=True, null=True, default='')
    city = models.CharField(max_length=100, default='City')
    postcode = models.CharField(max_length=20, default='000000')
    country = models.CharField(max_length=100, default='UK')
    default = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name}, {self.address_line1}, {self.city}"

class Store(models.Model):
    KEY_CHOICES = [
      ('wigan','Wigan'),
      ('southport','Southport'),
    ]
    key  = models.CharField(max_length=32, choices=KEY_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    lat  = models.FloatField(default=0)   # For postcode logic!
    lon  = models.FloatField(default=0)
    active = models.BooleanField(default=True)
    email = models.EmailField(blank=True, null=True)
    def __str__(self): return self.name

class StoreStock(models.Model):
    store   = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='stocks')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    qty     = models.PositiveIntegerField(default=0)
    class Meta:
       unique_together = ('store','product')
    def __str__(self):
       return f"{self.product.name} @ {self.store.key}: {self.qty}"

class Order(models.Model):
    PENDING           = 'pending'
    ACCEPTED          = 'accepted'
    OUT_FOR_DELIVERY  = 'out_for_delivery'
    DELIVERED         = 'delivered'

    STATUS_CHOICES = [
        (PENDING,          'Pending'),
        (ACCEPTED,         'Accepted'),
        (OUT_FOR_DELIVERY, 'Out for Delivery'),
        (DELIVERED,        'Delivered'),
    ]

    # ---- Payment Method choices ----
    CARD = 'card'
    COD = 'cod'
    PAYMENT_METHOD_CHOICES = [
        (CARD, 'Card / Apple Pay'),
        (COD, 'Cash on Delivery'),
    ]

    user  = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=32, blank=True, default='')
    first_name = models.CharField(max_length=64, blank=True, default='')
    last_name  = models.CharField(max_length=64, blank=True, default='')
    address    = models.CharField("Street address", max_length=255, blank=True, default='')
    address2   = models.CharField("Apartment, suite, etc.", max_length=255, blank=True, default='')
    city       = models.CharField(max_length=64, blank=True, default='')
    postcode   = models.CharField("Postcode", max_length=16,  blank=True, default='')
    notes      = models.TextField("Order notes", blank=True, default='')

    paid              = models.BooleanField(default=False)
    stripe_session_id = models.CharField(max_length=200, blank=True, default='')
    total_amount      = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status     = models.CharField(max_length=32, choices=STATUS_CHOICES, default=PENDING)
    store_key  = models.CharField("Store key",  max_length=64,  blank=True, default='')
    store_name = models.CharField("Store name", max_length=128, blank=True, default='')

    # NEW FIELD
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES, default=CARD
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def full_address(self):
        parts = []
        if self.address:
            parts.append(self.address)
        if self.address2:
            parts.append(self.address2)
        city_post = " ".join(filter(None, [self.city, self.postcode]))
        if city_post:
            parts.append(city_post)
        return ", ".join(parts)
    full_address.short_description = 'Address'

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip() or self.email
        return f"Order #{self.id} ({name})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    def __str__(self):
        return f"{self.product} (x{self.quantity})"

class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', blank=True)
    def __str__(self):
        return f"{self.user.username}'s wishlist"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, default='demo@email.com')
    subscribed_at = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.email
