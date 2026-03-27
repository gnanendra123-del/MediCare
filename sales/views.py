from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Sale, SaleItem
from inventory.models import Medicine, Batch
from customers.models import Customer
from prescriptions.models import Prescription
import json, requests
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from django.conf import settings


@login_required
def pos(request):
    customers = Customer.objects.filter(is_active=True).order_by('name')
    verified_prescriptions = Prescription.objects.filter(
        status='verified'
    ).select_related('customer').order_by('-created_at')[:50]
    return render(request, 'sales/pos.html', {
        'customers': customers,
        'prescriptions': verified_prescriptions,
    })


@login_required
@require_POST
def create_sale(request):
    try:
        data = json.loads(request.body)
        with transaction.atomic():
            sale = Sale(
                customer_id=data.get('customer_id') or None,
                prescription_id=data.get('prescription_id') or None,
                payment_method=data.get('payment_method', 'cash'),
                notes=data.get('notes', ''),
                created_by=request.user,
                discount_amount=Decimal(str(data.get('discount_amount', 0))),
            )
            sale.save()

            subtotal = Decimal('0')
            cgst_total = Decimal('0')
            sgst_total = Decimal('0')

            for item in data.get('items', []):
                batch = Batch.objects.select_for_update().get(id=item['batch_id'])
                qty = int(item['quantity'])

                if batch.quantity < qty:
                    raise ValueError(
                        f"Insufficient stock for {batch.medicine.name}. "
                        f"Available: {batch.quantity}, Requested: {qty}"
                    )

                if batch.medicine.prescription_required and not data.get('prescription_id'):
                    raise ValueError(
                        f"{batch.medicine.name} requires a valid prescription "
                        f"(Schedule {batch.medicine.schedule})"
                    )

                unit_price   = Decimal(str(item['unit_price']))
                discount_pct = Decimal(str(item.get('discount_percent', 0)))
                gst_rate     = Decimal(str(item['gst_rate']))
                cgst_rate    = gst_rate / Decimal('2')
                sgst_rate    = gst_rate / Decimal('2')

                si = SaleItem(
                    sale=sale,
                    medicine=batch.medicine,
                    batch=batch,
                    quantity=qty,
                    unit_price=unit_price,
                    discount_percent=discount_pct,
                    gst_rate=gst_rate,
                    cgst_rate=cgst_rate,
                    sgst_rate=sgst_rate,
                )
                si.save()

                batch.quantity -= qty
                batch.save()

                subtotal += si.taxable_amount
                cgst_total += si.gst_amount / 2
                sgst_total += si.gst_amount / 2

            sale.subtotal = subtotal
            sale.cgst_amount = cgst_total
            sale.sgst_amount = sgst_total
            gross = subtotal + cgst_total + sgst_total
            sale.total_amount = max(Decimal('0'), gross - sale.discount_amount)

            points_earned = int(sale.total_amount / 10)
            sale.loyalty_points_earned = points_earned
            sale.save()

            if sale.customer:
                sale.customer.loyalty_points += points_earned
                sale.customer.total_purchases += sale.total_amount
                sale.customer.save()

            return JsonResponse({
                'success': True,
                'invoice_number': sale.invoice_number,
                'sale_id': sale.id,
                'total': float(sale.total_amount),
            })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def sale_list(request):
    sales = Sale.objects.filter(status='completed').select_related(
        'customer', 'created_by'
    ).prefetch_related('items').order_by('-created_at')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        sales = sales.filter(sale_date__date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__date__lte=date_to)
    total = sales.aggregate(t=Sum('total_amount'))['t'] or 0
    return render(request, 'sales/sale_list.html', {'sales': sales, 'total': total})


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sales/sale_detail.html', {'sale': sale})


@login_required
def invoice_pdf(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Invoice-{sale.invoice_number}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    w, h = A4

    # ── Header ──────────────────────────────────────────────────────────
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(w / 2, h - 18 * mm, settings.SHOP_NAME)
    p.setFont("Helvetica", 9)
    p.drawCentredString(w / 2, h - 25 * mm, settings.SHOP_ADDRESS)
    p.drawCentredString(
        w / 2, h - 30 * mm,
        f"Ph: {settings.SHOP_PHONE}  |  GSTIN: {settings.SHOP_GSTIN}  |  DL: {settings.SHOP_LICENSE}"
    )
    p.setLineWidth(0.5)
    p.line(10 * mm, h - 33 * mm, w - 10 * mm, h - 33 * mm)

    # ── Invoice meta ────────────────────────────────────────────────────
    p.setFont("Helvetica-Bold", 11)
    p.drawString(10 * mm, h - 40 * mm, f"TAX INVOICE  #{sale.invoice_number}")
    p.setFont("Helvetica", 9)
    p.drawString(10 * mm, h - 47 * mm, f"Date: {sale.sale_date.strftime('%d-%m-%Y  %H:%M')}")
    p.drawString(10 * mm, h - 53 * mm, f"Payment: {sale.get_payment_method_display()}")
    if sale.customer:
        p.drawString(110 * mm, h - 47 * mm, f"Customer: {sale.customer.name}")
        p.drawString(110 * mm, h - 53 * mm, f"Phone: {sale.customer.phone}")
    p.line(10 * mm, h - 56 * mm, w - 10 * mm, h - 56 * mm)

    # ── Table header ────────────────────────────────────────────────────
    y = h - 63 * mm
    p.setFont("Helvetica-Bold", 8)
    cols = [(10, "Medicine"), (80, "Batch"), (108, "Expiry"),
            (128, "Qty"), (140, "Rate"), (158, "GST%"), (172, "Amount")]
    for x_mm, label in cols:
        p.drawString(x_mm * mm, y, label)
    p.line(10 * mm, y - 2 * mm, w - 10 * mm, y - 2 * mm)
    y -= 8 * mm

    p.setFont("Helvetica", 8)
    for item in sale.items.select_related('medicine', 'batch'):
        p.drawString(10 * mm, y, item.medicine.name[:32])
        p.drawString(80 * mm, y, item.batch.batch_number[:14])
        p.drawString(108 * mm, y, item.batch.expiry_date.strftime('%m/%y'))
        p.drawString(128 * mm, y, str(item.quantity))
        p.drawString(140 * mm, y, f"{item.unit_price:.2f}")
        p.drawString(158 * mm, y, f"{item.gst_rate}%")
        p.drawRightString(w - 10 * mm, y, f"{item.total_price:.2f}")
        y -= 6 * mm
        if y < 50 * mm:
            p.showPage()
            y = h - 20 * mm
            p.setFont("Helvetica", 8)

    # ── Totals ──────────────────────────────────────────────────────────
    p.line(10 * mm, y, w - 10 * mm, y)
    y -= 6 * mm
    totals_rows = [
        ("Subtotal:", f"Rs. {sale.subtotal:.2f}"),
        ("CGST:", f"Rs. {sale.cgst_amount:.2f}"),
        ("SGST:", f"Rs. {sale.sgst_amount:.2f}"),
    ]
    if sale.discount_amount:
        totals_rows.append(("Discount:", f"- Rs. {sale.discount_amount:.2f}"))

    p.setFont("Helvetica", 9)
    for label, value in totals_rows:
        p.drawString(130 * mm, y, label)
        p.drawRightString(w - 10 * mm, y, value)
        y -= 5 * mm

    p.setFont("Helvetica-Bold", 11)
    p.drawString(130 * mm, y, "TOTAL:")
    p.drawRightString(w - 10 * mm, y, f"Rs. {sale.total_amount:.2f}")

    y -= 10 * mm
    p.setFont("Helvetica", 8)
    if sale.loyalty_points_earned:
        p.drawCentredString(w / 2, y, f"You earned {sale.loyalty_points_earned} loyalty points on this purchase!")
        y -= 6 * mm
    p.drawCentredString(w / 2, y, f"Thank you for visiting {settings.SHOP_NAME}!")

    p.save()
    return response


@login_required
def check_drug_interaction(request):
    """Live drug interaction check via OpenFDA."""
    drug_names = request.GET.getlist('drugs[]')
    interactions = []
    if len(drug_names) >= 2:
        for drug in drug_names:
            try:
                url = (
                    f"https://api.fda.gov/drug/label.json"
                    f"?search=drug_interactions:{drug}&limit=1"
                )
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    results = resp.json().get('results', [])
                    if results:
                        text = results[0].get('drug_interactions', [''])[0]
                        if text and len(text) > 20:
                            interactions.append({
                                'drug': drug,
                                'warning': text[:400],
                            })
            except Exception:
                pass
    return JsonResponse({'interactions': interactions})
