"""
Auto-creates draft Purchase Orders for low-stock medicines.
Run daily via cron:
    0 9 * * * python manage.py auto_reorder
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from inventory.models import Medicine
from purchase.models import PurchaseOrder, PurchaseOrderItem


class Command(BaseCommand):
    help = 'Auto-generate draft Purchase Orders for low-stock medicines'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Show what would be ordered without creating POs')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        low_stock = [m for m in Medicine.objects.filter(
            is_active=True, default_supplier__isnull=False
        ).select_related('default_supplier') if m.is_low_stock]

        if not low_stock:
            self.stdout.write(self.style.SUCCESS('All medicines above reorder level.'))
            return

        # Group by supplier
        by_supplier = {}
        for m in low_stock:
            sid = m.default_supplier.id
            by_supplier.setdefault(sid, {'supplier': m.default_supplier, 'medicines': []})
            by_supplier[sid]['medicines'].append(m)

        system_user = User.objects.filter(is_superuser=True).first()

        for sid, data in by_supplier.items():
            supplier = data['supplier']
            medicines = data['medicines']

            self.stdout.write(f"\nSupplier: {supplier.name}")
            for m in medicines:
                qty = max(m.reorder_level * 2, 50)
                self.stdout.write(f"  → {m.name} | Stock: {m.total_stock} | "
                                  f"Reorder: {m.reorder_level} | Order qty: {qty}")

            if not dry_run:
                po = PurchaseOrder.objects.create(
                    supplier=supplier,
                    order_date=timezone.now().date(),
                    status='draft',
                    notes=f'Auto-generated on {timezone.now().strftime("%d %b %Y")} '
                          f'for {len(medicines)} low-stock medicines',
                    created_by=system_user,
                    is_auto_generated=True,
                )
                subtotal = 0
                for m in medicines:
                    qty = max(m.reorder_level * 2, 50)
                    last_batch = m.batches.order_by('-created_at').first()
                    price = last_batch.purchase_price if last_batch else 50
                    poi = PurchaseOrderItem.objects.create(
                        purchase_order=po,
                        medicine=m,
                        quantity_ordered=qty,
                        unit_price=price,
                        gst_rate=12,
                    )
                    subtotal += float(poi.total_price)

                po.subtotal = subtotal
                po.gst_amount = subtotal * 0.12
                po.total_amount = subtotal * 1.12
                po.save()
                self.stdout.write(self.style.SUCCESS(
                    f'  Created PO {po.po_number} | Total: Rs.{po.total_amount:.2f}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] No POs created.'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\nCreated {len(by_supplier)} draft PO(s).'))
