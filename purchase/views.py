from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GRNItem, SupplierLedger
from inventory.models import Medicine, Supplier, Batch
from .forms import PurchaseOrderForm, POItemFormSet, GRNForm, GRNItemFormSet
import json

@login_required
def po_list(request):
    orders = PurchaseOrder.objects.all().select_related('supplier').order_by('-created_at')
    return render(request, 'purchase/po_list.html', {'orders': orders})

@login_required
def po_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                po = form.save(commit=False)
                po.created_by = request.user
                po.save()
                items_data = json.loads(request.POST.get('items_json', '[]'))
                subtotal = 0
                for item in items_data:
                    if item.get('medicine_id') and item.get('quantity'):
                        poi = PurchaseOrderItem.objects.create(
                            purchase_order=po,
                            medicine_id=item['medicine_id'],
                            quantity_ordered=item['quantity'],
                            unit_price=item['unit_price'],
                            gst_rate=item.get('gst_rate', 12),
                        )
                        subtotal += float(poi.total_price)
                gst = subtotal * 0.12
                po.subtotal = subtotal
                po.gst_amount = gst
                po.total_amount = subtotal + gst
                po.save()
                # Supplier ledger
                SupplierLedger.objects.create(supplier=po.supplier, transaction_type='purchase',
                    amount=po.total_amount, reference=po.po_number, notes='Purchase Order raised')
                messages.success(request, f'Purchase Order {po.po_number} created.')
                return redirect('po_detail', pk=po.pk)
    else:
        form = PurchaseOrderForm()
    medicines = Medicine.objects.filter(is_active=True).values('id', 'name', 'brand')
    suppliers = Supplier.objects.filter(is_active=True)
    return render(request, 'purchase/po_form.html', {'form': form, 'medicines': list(medicines), 'suppliers': suppliers})

@login_required
def po_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'purchase/po_detail.html', {'po': po})

@login_required
def grn_create(request, po_pk):
    po = get_object_or_404(PurchaseOrder, pk=po_pk)
    if request.method == 'POST':
        with transaction.atomic():
            grn = GoodsReceiptNote.objects.create(
                purchase_order=po, created_by=request.user,
                invoice_number=request.POST.get('invoice_number', ''),
            )
            for poi in po.items.all():
                qty = int(request.POST.get(f'qty_{poi.id}', 0))
                batch_num = request.POST.get(f'batch_{poi.id}', '')
                expiry = request.POST.get(f'expiry_{poi.id}', '')
                selling_price = request.POST.get(f'selling_{poi.id}', poi.unit_price)
                mrp = request.POST.get(f'mrp_{poi.id}', poi.unit_price)
                if qty > 0 and batch_num and expiry:
                    GRNItem.objects.create(
                        grn=grn, po_item=poi, medicine=poi.medicine,
                        quantity_received=qty, batch_number=batch_num,
                        expiry_date=expiry, purchase_price=poi.unit_price,
                        selling_price=selling_price, mrp=mrp, gst_rate=poi.gst_rate,
                    )
                    # Update PO item received qty
                    poi.quantity_received += qty
                    poi.save()
                    # Add batch to inventory
                    Batch.objects.create(
                        medicine=poi.medicine, batch_number=batch_num,
                        expiry_date=expiry, quantity=qty,
                        purchase_price=poi.unit_price, selling_price=selling_price,
                        mrp=mrp, gst_rate=poi.gst_rate,
                    )
            # Update PO status
            all_received = all(i.quantity_received >= i.quantity_ordered for i in po.items.all())
            po.status = 'received' if all_received else 'partial'
            po.save()
            messages.success(request, f'GRN {grn.grn_number} created. Stock updated.')
            return redirect('po_detail', pk=po_pk)
    return render(request, 'purchase/grn_form.html', {'po': po})

@login_required
def supplier_ledger(request, supplier_pk):
    supplier = get_object_or_404(Supplier, pk=supplier_pk)
    ledger = supplier.ledger.all().order_by('-transaction_date')
    total_purchase = sum(l.amount for l in ledger.filter(transaction_type='purchase'))
    total_paid = sum(l.amount for l in ledger.filter(transaction_type='payment'))
    balance = total_purchase - total_paid
    return render(request, 'purchase/supplier_ledger.html', {'supplier': supplier, 'ledger': ledger, 'balance': balance})

@login_required
def record_payment(request, supplier_pk):
    supplier = get_object_or_404(Supplier, pk=supplier_pk)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        reference = request.POST.get('reference', '')
        SupplierLedger.objects.create(supplier=supplier, transaction_type='payment',
            amount=amount, reference=reference)
        messages.success(request, f'Payment of Rs.{amount} recorded for {supplier.name}.')
        return redirect('supplier_ledger', supplier_pk=supplier_pk)
    return render(request, 'purchase/record_payment.html', {'supplier': supplier})
