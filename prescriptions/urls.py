from django.urls import path
from . import views
urlpatterns = [
    path('', views.prescription_list, name='prescription_list'),
    path('add/', views.prescription_add, name='prescription_add'),
    path('<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('<int:pk>/verify/', views.prescription_verify, name='prescription_verify'),
]
