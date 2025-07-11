"""
URL configuration for mydb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('customer_login/', views.customer_login, name='customer_login'),
    path('seller_login/', views.seller_login, name='seller_login'),
path('seller_signup/', views.seller_signup, name='seller_signup'),
    path('customer_signup/', views.customer_signup, name='customer_signup'),
    path('customer_product/', views.customer_product, name='customer_product'),
path('place_order/<int:product_id>/', views.place_order, name='place_order'),
path('add_cust_phone_number/', views.add_cust_phone_number, name='add_cust_phone_number'),
path('add_seller_phone_number/', views.add_seller_phone_number, name='add_seller_phone_number'),
path('add_address/', views.add_address, name='add_address'),
path('add_product/', views.add_product, name='add_product'),
path('seller_home/', views.seller_home, name='seller_home'),
path('my_details/', views.my_details, name='my_details'),
path('seller_details/', views.seller_details, name='seller_details'),path('update_stock/', views.update_stock, name='update_stock'),
path('choose_delivery_partner/', views.choose_delivery_partner, name='choose_delivery_partner'),

]

