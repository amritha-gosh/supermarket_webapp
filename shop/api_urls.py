from rest_framework import routers
from . import api_views

router = routers.DefaultRouter()
router.register(r'categories', api_views.CategoryViewSet)
router.register(r'products', api_views.ProductViewSet)
router.register(r'brands', api_views.BrandViewSet)
router.register(r'orders', api_views.OrderViewSet)

urlpatterns = router.urls
