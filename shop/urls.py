from django.urls import path, include
from rest_framework import routers
from .views import CartViewSet, CartItemViewSet
from rest_framework.authtoken.views import obtain_auth_token
from . import views
router = routers.DefaultRouter()
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
urlpatterns = [
    path('product', views.products, name="products"), 
    path('product/<id>', views.product_detail, name="product_detail"), 
    path('category', views.categories, name="categories"),    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.registration_view, name='registration'),
    path('cart/',include(router.urls)),
    path('user-cart/', CartViewSet.as_view({'get': 'get_user_cart'}), name='user-cart'),
    path('cart-items/<int:cart_id>/', CartItemViewSet.as_view({'get': 'get_cart_items'}), name='cart-items'),
]