# MediCare — Pharmacy Management System
Django 5.1 · Python 3.13+ · SQLite3 · Bootstrap 5

## Quick Start

```
pip install django==5.1 pillow reportlab openpyxl requests django-auditlog
cd medishop
python manage.py migrate
python seed_data.py
python manage.py runserver
```

Open: http://127.0.0.1:8000
Login: admin / admin123

---

## Configure Email (Expiry Alerts & Reminders)

Edit medishop/settings.py:
  EMAIL_HOST_USER     = 'yourname@gmail.com'
  EMAIL_HOST_PASSWORD = 'your-16-char-app-password'
  LOW_STOCK_ALERT_EMAIL = 'yourname@gmail.com'

Gmail App Password: myaccount.google.com → Security → App Passwords

---

## Configure Shop Details

Edit medishop/settings.py:
  SHOP_NAME    = 'MediCare Pharmacy'
  SHOP_ADDRESS = 'Your Address'
  SHOP_GSTIN   = 'Your GSTIN'
  SHOP_PHONE   = 'Your Phone'
  SHOP_LICENSE = 'Your Drug License No.'

---

## Features

  Inventory       — Medicines, Batches, Categories, Suppliers
                    Expiry alerts (30/60/90 days), Low stock alerts
  Point of Sale   — Live search, Camera barcode scanner, Drug interaction check
                    GST auto-calculation, Loyalty points, Invoice PDF
  Purchases       — Purchase Orders, GRN (auto-updates stock), Supplier Ledger
  Prescriptions   — Upload image, Verify, Link to sale
  Customers       — CRM, Loyalty tiers, Reminders, Email
  Reports         — Analytics, GST report + Excel export, P&L

---

## URL Reference

  /                          Dashboard
  /inventory/                Medicines
  /inventory/suppliers/      Suppliers
  /inventory/categories/     Categories
  /inventory/expiry-alerts/  Expiry Alerts
  /inventory/low-stock/      Low Stock
  /sales/pos/                Point of Sale
  /sales/                    Sales History
  /purchase/                 Purchase Orders
  /prescriptions/            Prescriptions
  /customers/                Customers
  /analytics/                Analytics
  /analytics/gst-report/     GST Report
  /analytics/profit-loss/    P&L Report
  /accounts/users/           User Management

---

## Fixed in This Version (v4)

  1. Medicine Add — now redirects to detail page (was: list page)
  2. Supplier Add — now redirects to detail page (was: list page)
  3. New items appear at TOP of lists (newest-first ordering added)
  4. Django Admin completely removed from sidebar and URLs
  5. seed_data.py path fixed for Windows compatibility
