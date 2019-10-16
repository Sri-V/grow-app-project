from django.urls import path
from orders import views

urlpatterns = [
    path('shop', views.shop, name="shop"),
    path('create_account', views.create_account, name="create_account"),
    path('', views.orders_home, name="orders_home"),
    path('account', views.account, name="account"),
    path('schedule', views.schedule, name="customer_schedule"),
    path('cart', views.cart, name="cart"),
    path('create_order', views.create_order, name="create_order"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('orders', views.orders, name="orders"),
    path('customers', views.customers, name="customers"),
    path('add_product', views.add_product, name="add_product"),
    path('products', views.products, name="products"),
    path('orders_settings', views.orders_settings, name="orders_settings"),
    path('product_details/<str:product_name>/', views.product_details, name="product_details"),
]
