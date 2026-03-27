from django.urls import path
from . import views
urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('add/', views.customer_add, name='customer_add'),
    path('<int:pk>/', views.customer_detail, name='customer_detail'),
    path('<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:pk>/reminder/', views.add_reminder, name='add_reminder'),
    path('reminder/<int:reminder_pk>/send/', views.send_reminder_email, name='send_reminder_email'),
]
