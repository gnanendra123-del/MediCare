# Automated Alerts — Cron Setup

## Available Management Commands

| Command | Purpose |
|---------|---------|
| `send_expiry_alerts` | Email alerts for expiring & expired medicines |
| `auto_reorder` | Auto-create draft POs for low-stock medicines |

## Usage

```bash
# Test without sending (dry run)
python manage.py send_expiry_alerts --dry-run
python manage.py auto_reorder --dry-run

# Send for 60-day threshold
python manage.py send_expiry_alerts --days 60

# Live run
python manage.py send_expiry_alerts
python manage.py auto_reorder
```

## Windows Task Scheduler (Recommended for Windows)

1. Open Task Scheduler → Create Basic Task
2. Set trigger: Daily at 8:00 AM
3. Action: Start a program
   - Program: `C:\Python39\python.exe`
   - Arguments: `C:\path\to\medishop\manage.py send_expiry_alerts`
   - Start in: `C:\path\to\medishop`

## Linux/Mac Cron

```bash
# Edit crontab
crontab -e

# Add these lines:
# Expiry alerts at 8 AM daily
0 8 * * * cd /path/to/medishop && python manage.py send_expiry_alerts >> /var/log/medishop_expiry.log 2>&1

# Auto-reorder check at 9 AM daily
0 9 * * * cd /path/to/medishop && python manage.py auto_reorder >> /var/log/medishop_reorder.log 2>&1
```

## SMTP Setup for Gmail

1. Enable 2-Step Verification in Google Account
2. Go to Google Account → Security → App Passwords
3. Generate password for "Mail" on "Windows Computer"
4. Copy the 16-character password

In `medishop/settings.py`:
```python
EMAIL_HOST_USER = 'yourshop@gmail.com'
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # App password
LOW_STOCK_ALERT_EMAIL = 'manager@yourshop.com'
```
