from django.urls import path
from . import views
urlpatterns = [
    path('', views.po_list, name='po_list'),
    path('create/', views.po_create, name='po_create'),
    path('<int:pk>/', views.po_detail, name='po_detail'),
    path('<int:po_pk>/grn/', views.grn_create, name='grn_create'),
    path('supplier/<int:supplier_pk>/ledger/', views.supplier_ledger, name='supplier_ledger'),
    path('supplier/<int:supplier_pk>/payment/', views.record_payment, name='record_payment'),
]
