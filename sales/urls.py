from django.urls import path
from . import views
urlpatterns = [
    path('pos/', views.pos, name='pos'),
    path('create/', views.create_sale, name='create_sale'),
    path('', views.sale_list, name='sale_list'),
    path('<int:pk>/', views.sale_detail, name='sale_detail'),
    path('<int:pk>/invoice/', views.invoice_pdf, name='invoice_pdf'),
    path('api/drug-interaction/', views.check_drug_interaction, name='drug_interaction'),
]
