from django.urls import path
from . import views

urlpatterns = [
    path('', views.medicine_list, name='medicine_list'),
    path('add/', views.medicine_add, name='medicine_add'),
    path('<int:pk>/', views.medicine_detail, name='medicine_detail'),
    path('<int:pk>/edit/', views.medicine_edit, name='medicine_edit'),
    path('<int:medicine_pk>/batch/add/', views.batch_add, name='batch_add'),
    path('expiry-alerts/', views.expiry_alerts, name='expiry_alerts'),
    path('expiry-alerts/send-email/', views.send_expiry_alert_email, name='send_expiry_email'),
    path('low-stock/', views.low_stock_list, name='low_stock_list'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('api/search/', views.medicine_search_api, name='medicine_search_api'),
]
