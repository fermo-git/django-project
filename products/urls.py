from django.urls import path, include
from .views import CategoryViewSet, ProductViewSet, precio_final
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('precio-final/', precio_final, name='precio-final'),
    path('', include(router.urls)),
]