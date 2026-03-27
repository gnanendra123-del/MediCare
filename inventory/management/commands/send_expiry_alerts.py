"""
Management command to send expiry and low-stock alerts via SMTP.
Run daily via cron:
    0 8 * * * python manage.py send_expiry_alerts
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from inventory.models import Batch, Medicine


class Command(BaseCommand):
    help = 'Send expiry and low-stock alert emails'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30,
                            help='Alert threshold in days (default: 30)')
        parser.add_argument('--dry-run', action='store_true',
                            help='Print alerts without sending emails')

    def handle(self, *args, **options):
        today = timezone.now().date()
        days = options['days']
        dry_run = options['dry_run']
        recipient = settings.LOW_STOCK_ALERT_EMAIL

        # ── Expiry alerts ───────────────────────────────────────────────
        expiring = Batch.objects.filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timezone.timedelta(days=days),
            quantity__gt=0,
            is_active=True,
        ).select_related('medicine').order_by('expiry_date')

        expired = Batch.objects.filter(
            expiry_date__lt=today,
            quantity__gt=0,
            is_active=True,
        ).select_related('medicine')

        # ── Low stock ───────────────────────────────────────────────────
        low_stock = [m for m in Medicine.objects.filter(is_active=True)
                     .select_related('default_supplier') if m.is_low_stock]

        if not expiring.exists() and not expired.exists() and not low_stock:
            self.stdout.write(self.style.SUCCESS('No alerts to send.'))
            return

        lines = [f"MediShop Daily Alert — {today.strftime('%d %b %Y')}", "=" * 50, ""]

        if expired.exists():
            lines.append(f"EXPIRED MEDICINES ({expired.count()}):")
            for b in expired:
                lines.append(f"  ✗ {b.medicine.name} | Batch: {b.batch_number} | "
                             f"Expired: {b.expiry_date} | Qty: {b.quantity}")
            lines.append("")

        if expiring.exists():
            lines.append(f"EXPIRING IN {days} DAYS ({expiring.count()}):")
            for b in expiring:
                lines.append(f"  ! {b.medicine.name} | Batch: {b.batch_number} | "
                             f"Expires: {b.expiry_date} ({b.days_to_expiry}d) | Qty: {b.quantity}")
            lines.append("")

        if low_stock:
            lines.append(f"LOW STOCK MEDICINES ({len(low_stock)}):")
            for m in low_stock:
                lines.append(f"  ↓ {m.name} ({m.brand}) | Stock: {m.total_stock} | "
                             f"Reorder level: {m.reorder_level} | "
                             f"Supplier: {m.default_supplier.name if m.default_supplier else 'N/A'}")
            lines.append("")

        lines.append("Please log in to MediShop to take action.")
        body = "\n".join(lines)

        if dry_run:
            self.stdout.write(body)
            self.stdout.write(self.style.WARNING('\n[DRY RUN] Email not sent.'))
        else:
            try:
                send_mail(
                    subject=f"MediShop Alert: {expired.count()} expired, "
                            f"{expiring.count()} expiring, {len(low_stock)} low stock",
                    message=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Alert email sent to {recipient}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Email failed: {e}'))
