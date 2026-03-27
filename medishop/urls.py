from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from inventory.views import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('purchase/', include('purchase.urls')),
    path('prescriptions/', include('prescriptions.urls')),
    path('customers/', include('customers.urls')),
    path('analytics/', include('analytics.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
