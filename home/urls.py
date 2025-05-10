from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home'),  # 首页
    path('sign_in', views.sign_in, name='sign_in'),
    path('get_prizes', views.get_prizes, name='get_prizes'),
    path('redemption', views.redemption, name='redemption'),
    path('redemptions', views.redemptions, name='redemptions'),
    path('shipping', views.shipping, name='shipping'),
    path('all_history', views.all_history, name='all_history'),
    path('region_children', views.region_children, name='region_children'),
    path('create_shipping', views.create_shipping, name='create_shipping'),
    path('set_default_shipping', views.set_default_shipping, name='set_default_shipping'),
    path('delete_shipping', views.delete_shipping, name='delete_shipping'),
    path('set_redemption_shipping', views.set_redemption_shipping, name='set_redemption_shipping'),
    path('redemptions/show/<int:id>', views.show_redemption, name='show_redemption'),
    path('shipping/new', views.new_shipping, name='new_shipping'),
]