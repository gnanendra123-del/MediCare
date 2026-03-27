from django.urls import path
from . import views
urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('gst-report/', views.gst_report, name='gst_report'),
    path('gst-report/export/', views.export_gst_excel, name='export_gst_excel'),
    path('profit-loss/', views.profit_loss_report, name='profit_loss_report'),
]
