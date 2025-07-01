from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    # 前端页面
    path('', views.store_list, name='store_list'),
    path('api/geocode/', views.geocode_address, name='geocode_address'),
    path('api/reverse_geocode/', views.reverse_geocode, name='reverse_geocode'),
    path('api/nearest_stores/', views.get_nearest_stores, name='get_nearest_stores'),
    path('api/search_store/', views.search_store, name='search_store'),
    path('introduction/', views.introduction, name='introduction'),
    path('tutorials/', views.tutorials, name='tutorials'),
    path('trophy/', views.trophy, name='trophy'),
]