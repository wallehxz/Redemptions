from django.urls import path
from . import views

urlpatterns = [
    path('redeem_points', views.redeem_points, name='redeem_points'),
    path('redeem_history', views.redeem_history, name='redeem_history'),
    path('transactions', views.transactions, name='transactions'),
    path('harvest', views.harvest, name='harvest'),
    path('product_detail/<int:product_id>', views.product_detail, name='product_detail'),
    path('exchange_product', views.exchange_product, name='exchange_product'),
]