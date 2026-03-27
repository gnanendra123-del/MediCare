from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Medicine, Batch, Category, Supplier
from .forms import MedicineForm, BatchForm, CategoryForm, SupplierForm

@login_required
def dashboard(request):
    from sales.models import Sale
    today = timezone.now().date()
    medicines = Medicine.objects.filter(is_active=True)
    batches = Batch.objects.filter(is_active=True, quantity__gt=0)
    low_stock = [m for m in medicines if m.is_low_stock]
    expiring_30 = batches.filter(expiry_date__lte=today + timedelta(days=30), expiry_date__gte=today)
    expired = batches.filter(expiry_date__lt=today)
    today_sales = Sale.objects.filter(sale_date__date=today, status='completed')
    today_revenue = today_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    context = {
        'total_medicines': medicines.count(),
        'low_stock_count': len(low_stock),
        'expiring_30_count': expiring_30.count(),
        'expired_count': expired.count(),
        'today_revenue': today_revenue,
        'today_sales_count': today_sales.count(),
        'low_stock_items': low_stock[:10],
        'expiring_soon': expiring_30[:10],
    }
    return render(request, 'inventory/dashboard.html', context)

@login_required
def medicine_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    schedule = request.GET.get('schedule', '')
    medicines = Medicine.objects.filter(is_active=True).select_related('category', 'default_supplier')
    if query:
        medicines = medicines.filter(Q(name__icontains=query) | Q(brand__icontains=query) | Q(generic_name__icontains=query) | Q(barcode__icontains=query))
    if category:
        medicines = medicines.filter(category_id=category)
    if schedule:
        medicines = medicines.filter(schedule=schedule)
    categories = Category.objects.all()
    return render(request, 'inventory/medicine_list.html', {'medicines': medicines, 'categories': categories, 'query': query})

@login_required
def medicine_add(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save()
            messages.success(request, f'Medicine "{medicine.name}" added successfully.')
            return redirect('medicine_detail', pk=medicine.pk)
    else:
        form = MedicineForm()
    return render(request, 'inventory/medicine_form.html', {'form': form, 'title': 'Add Medicine'})

@login_required
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully.')
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'inventory/medicine_form.html', {'form': form, 'title': 'Edit Medicine', 'medicine': medicine})

@login_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    batches = medicine.batches.filter(is_active=True).order_by('expiry_date')
    return render(request, 'inventory/medicine_detail.html', {'medicine': medicine, 'batches': batches})

@login_required
def batch_add(request, medicine_pk):
    medicine = get_object_or_404(Medicine, pk=medicine_pk)
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.medicine = medicine
            batch.save()
            messages.success(request, f'Batch added for {medicine.name}.')
            return redirect('medicine_detail', pk=medicine_pk)
    else:
        form = BatchForm()
    return render(request, 'inventory/batch_form.html', {'form': form, 'medicine': medicine})

@login_required
def expiry_alerts(request):
    today = timezone.now().date()
    expired = Batch.objects.filter(expiry_date__lt=today, quantity__gt=0, is_active=True).select_related('medicine')
    exp_30 = Batch.objects.filter(expiry_date__gte=today, expiry_date__lte=today+timedelta(days=30), quantity__gt=0, is_active=True).select_related('medicine')
    exp_60 = Batch.objects.filter(expiry_date__gt=today+timedelta(days=30), expiry_date__lte=today+timedelta(days=60), quantity__gt=0, is_active=True).select_related('medicine')
    exp_90 = Batch.objects.filter(expiry_date__gt=today+timedelta(days=60), expiry_date__lte=today+timedelta(days=90), quantity__gt=0, is_active=True).select_related('medicine')
    return render(request, 'inventory/expiry_alerts.html', {'expired': expired, 'exp_30': exp_30, 'exp_60': exp_60, 'exp_90': exp_90})

@login_required
def send_expiry_alert_email(request):
    today = timezone.now().date()
    expiring = Batch.objects.filter(expiry_date__gte=today, expiry_date__lte=today+timedelta(days=30), quantity__gt=0, is_active=True).select_related('medicine')
    if expiring.exists():
        lines = [f"- {b.medicine.name} | Batch: {b.batch_number} | Expiry: {b.expiry_date} | Qty: {b.quantity}" for b in expiring]
        body = "The following medicines are expiring within 30 days:\n\n" + "\n".join(lines)
        try:
            send_mail("Expiry Alert - MediShop", body, settings.DEFAULT_FROM_EMAIL, [settings.LOW_STOCK_ALERT_EMAIL])
            messages.success(request, f'Expiry alert email sent for {expiring.count()} batches.')
        except Exception as e:
            messages.error(request, f'Email failed: {e}')
    else:
        messages.info(request, 'No medicines expiring in the next 30 days.')
    return redirect('expiry_alerts')

@login_required
def low_stock_list(request):
    medicines = [m for m in Medicine.objects.filter(is_active=True).select_related('default_supplier') if m.is_low_stock]
    return render(request, 'inventory/low_stock.html', {'medicines': medicines})

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.filter(is_active=True)
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.name}" added successfully.')
            return redirect('supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm()
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Add Supplier'})

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    ledger = supplier.ledger.all().order_by('-transaction_date')[:10]
    total_purchase = sum(l.amount for l in supplier.ledger.filter(transaction_type='purchase'))
    total_paid = sum(l.amount for l in supplier.ledger.filter(transaction_type='payment'))
    balance = total_purchase - total_paid
    medicines = Medicine.objects.filter(default_supplier=supplier, is_active=True)
    return render(request, 'inventory/supplier_detail.html', {
        'supplier': supplier, 'ledger': ledger,
        'total_purchase': total_purchase, 'total_paid': total_paid,
        'balance': balance, 'medicines': medicines,
    })

@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated.')
            return redirect('supplier_detail', pk=pk)
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})

def medicine_search_api(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) | Q(barcode=query) | Q(generic_name__icontains=query),
            is_active=True
        )[:10]
        for m in medicines:
            batches = m.batches.filter(quantity__gt=0, expiry_date__gte=timezone.now().date(), is_active=True).order_by('expiry_date')
            if batches.exists():
                b = batches.first()
                results.append({
                    'id': m.id, 'name': m.name, 'brand': m.brand, 'form': m.form,
                    'strength': m.strength, 'barcode': m.barcode or '',
                    'schedule': m.schedule, 'prescription_required': m.prescription_required,
                    'batch_id': b.id, 'batch_number': b.batch_number,
                    'expiry_date': str(b.expiry_date), 'selling_price': float(b.selling_price),
                    'mrp': float(b.mrp), 'gst_rate': float(b.gst_rate), 'available_qty': b.quantity
                })
    return JsonResponse({'results': results})


@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'inventory/category_list.html', {'categories': categories})

@login_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {'form': form, 'title': 'Add Category'})

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})
