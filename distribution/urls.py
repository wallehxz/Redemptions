from django.urls import path
from . import views

urlpatterns = [
    path('complete_store', views.complete_store, name='complete_store'),
    path('create_staff_store', views.create_staff_store, name='create_staff_store'),
    path('exchange_history', views.exchange_history, name='exchange_history'),
    path('redemption_detail/<int:redemption_id>', views.redemption_detail, name='redemption_detail'),
    path('withdrawal/<int:redemption_id>', views.withdrawal, name='withdrawal'),
    path('manual_openid/<int:redemption_id>', views.manual_openid, name='manual_openid'),
    path('confirm_transfer/<int:redemption_id>', views.confirm_transfer, name='confirm_transfer'),
]