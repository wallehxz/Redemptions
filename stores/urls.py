from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    # 前端页面
    path('', views.store_list, name='store_list'),

    path('api/geocode/', views.geocode_address, name='geocode_address'),
    path('api/reverse-geocode/', views.reverse_geocode, name='reverse_geocode'),

    path('api/search_store/', views.search_store, name='search_store'),
]