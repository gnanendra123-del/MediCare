import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medishop.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User, Group
from inventory.models import Category, Supplier, Medicine, Batch
from customers.models import Customer
from datetime import date, timedelta
from decimal import Decimal

print("Creating superuser...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@medishop.com', 'admin123')
    print("  admin / admin123")

print("Creating roles...")
for role in ['Pharmacist', 'StoreManager', 'Accountant']:
    Group.objects.get_or_create(name=role)

print("Creating categories...")
cats = {}
for name in ['Antibiotics', 'Analgesics', 'Antacids', 'Vitamins', 'Antidiabetic', 'Antihypertensive', 'Antiallergic', 'Cardiac']:
    c, _ = Category.objects.get_or_create(name=name)
    cats[name] = c

print("Creating suppliers...")
s1, _ = Supplier.objects.get_or_create(name='Sun Pharma Distributors', defaults={'phone':'9876543210','email':'sun@pharma.com','gstin':'33AABCS1429B1Z9','drug_license':'DL-TN-001'})
s2, _ = Supplier.objects.get_or_create(name='Cipla Wholesale', defaults={'phone':'9876543211','email':'cipla@wholesale.com','gstin':'33AACCC0396G1ZO','drug_license':'DL-TN-002'})
s3, _ = Supplier.objects.get_or_create(name='Abbott India Dist.', defaults={'phone':'9876543212','email':'abbott@dist.com','gstin':'33AABCA3964P1Z8','drug_license':'DL-TN-003'})

print("Creating medicines and batches...")
medicines_data = [
    {'name':'Amoxicillin 500mg','brand':'Mox','generic_name':'Amoxicillin','category':'Antibiotics','form':'capsule','strength':'500mg','unit':'strip','hsn_code':'30041011','barcode':'8901234567890','schedule':'H','prescription_required':True,'rack_location':'A-01','reorder_level':20,'supplier':s1,
     'batches':[{'batch':'AMX2024A','expiry':date.today()+timedelta(days=365),'qty':100,'pp':45,'sp':65,'mrp':75,'gst':12},{'batch':'AMX2024B','expiry':date.today()+timedelta(days=25),'qty':30,'pp':45,'sp':65,'mrp':75,'gst':12}]},
    {'name':'Paracetamol 500mg','brand':'Calpol','generic_name':'Paracetamol','category':'Analgesics','form':'tablet','strength':'500mg','unit':'strip','hsn_code':'30049099','barcode':'8901234567891','schedule':'OTC','prescription_required':False,'rack_location':'B-01','reorder_level':50,'supplier':s2,
     'batches':[{'batch':'CAL2024A','expiry':date.today()+timedelta(days=400),'qty':200,'pp':12,'sp':22,'mrp':28,'gst':12}]},
    {'name':'Metformin 500mg','brand':'Glycomet','generic_name':'Metformin HCl','category':'Antidiabetic','form':'tablet','strength':'500mg','unit':'strip','hsn_code':'30049041','barcode':'8901234567892','schedule':'H','prescription_required':True,'rack_location':'C-01','reorder_level':30,'supplier':s3,
     'batches':[{'batch':'GLY2024A','expiry':date.today()+timedelta(days=500),'qty':150,'pp':38,'sp':58,'mrp':65,'gst':12}]},
    {'name':'Omeprazole 20mg','brand':'Omez','generic_name':'Omeprazole','category':'Antacids','form':'capsule','strength':'20mg','unit':'strip','hsn_code':'30049099','barcode':'8901234567893','schedule':'H','prescription_required':False,'rack_location':'D-01','reorder_level':25,'supplier':s2,
     'batches':[{'batch':'OMZ2024A','expiry':date.today()+timedelta(days=300),'qty':80,'pp':55,'sp':85,'mrp':95,'gst':12}]},
    {'name':'Amlodipine 5mg','brand':'Amlong','generic_name':'Amlodipine Besylate','category':'Antihypertensive','form':'tablet','strength':'5mg','unit':'strip','hsn_code':'30049099','barcode':'8901234567894','schedule':'H','prescription_required':True,'rack_location':'E-01','reorder_level':20,'supplier':s3,
     'batches':[{'batch':'AML2024A','expiry':date.today()+timedelta(days=550),'qty':120,'pp':42,'sp':68,'mrp':78,'gst':12}]},
    {'name':'Cetirizine 10mg','brand':'Zyrtec','generic_name':'Cetirizine HCl','category':'Antiallergic','form':'tablet','strength':'10mg','unit':'strip','hsn_code':'30049099','barcode':'8901234567895','schedule':'OTC','prescription_required':False,'rack_location':'F-01','reorder_level':30,'supplier':s1,
     'batches':[{'batch':'ZYR2024A','expiry':date.today()+timedelta(days=450),'qty':90,'pp':28,'sp':45,'mrp':55,'gst':12}]},
    {'name':'Vitamin D3 1000IU','brand':'Uprise D3','generic_name':'Cholecalciferol','category':'Vitamins','form':'tablet','strength':'1000IU','unit':'strip','hsn_code':'30049099','barcode':'8901234567896','schedule':'OTC','prescription_required':False,'rack_location':'G-01','reorder_level':15,'supplier':s2,
     'batches':[{'batch':'VIT2024A','expiry':date.today()+timedelta(days=600),'qty':5,'pp':65,'sp':95,'mrp':120,'gst':12}]},  # low stock
    {'name':'Atorvastatin 10mg','brand':'Lipitor','generic_name':'Atorvastatin Calcium','category':'Cardiac','form':'tablet','strength':'10mg','unit':'strip','hsn_code':'30049099','barcode':'8901234567897','schedule':'H','prescription_required':True,'rack_location':'H-01','reorder_level':20,'supplier':s3,
     'batches':[{'batch':'LIP2024A','expiry':date.today()+timedelta(days=365),'qty':60,'pp':95,'sp':145,'mrp':165,'gst':12}]},
]

for md in medicines_data:
    m, created = Medicine.objects.get_or_create(name=md['name'], defaults={
        'brand':md['brand'],'generic_name':md['generic_name'],'category':cats[md['category']],
        'form':md['form'],'strength':md['strength'],'unit':md['unit'],'hsn_code':md['hsn_code'],
        'barcode':md['barcode'],'schedule':md['schedule'],'prescription_required':md['prescription_required'],
        'rack_location':md['rack_location'],'reorder_level':md['reorder_level'],'default_supplier':md['supplier'],
    })
    if created:
        for b in md['batches']:
            Batch.objects.create(medicine=m, batch_number=b['batch'], expiry_date=b['expiry'], quantity=b['qty'],
                purchase_price=b['pp'], selling_price=b['sp'], mrp=b['mrp'], gst_rate=b['gst'])
        print(f"  + {m.name}")

print("Creating customers...")
customers = [
    ('Ravi Kumar','9944112233','ravi@gmail.com'),
    ('Priya Sharma','9944112244','priya@gmail.com'),
    ('Anand Raj','9944112255','anand@gmail.com'),
    ('Meena Devi','9944112266','meena@gmail.com'),
    ('Suresh Babu','9944112277','suresh@gmail.com'),
]
for name, phone, email in customers:
    c, _ = Customer.objects.get_or_create(phone=phone, defaults={'name':name,'email':email})
    print(f"  + {c.name}")

print("\n=== Seed Complete! ===")
print("Login: admin / admin123")
print("Run: python manage.py runserver")


# ── Create a sample sale so analytics / GST / P&L have data ──────────────────
print("Creating sample sale...")
from django.utils import timezone
from django.contrib.auth.models import User
from sales.models import Sale, SaleItem
from inventory.models import Batch
from customers.models import Customer as Cust
from decimal import Decimal

admin_user = User.objects.filter(is_superuser=True).first()
para = Medicine.objects.filter(name='Paracetamol 500mg').first()
if para:
    batch = para.batches.filter(is_active=True, quantity__gt=0).first()
    cust_obj  = Cust.objects.first()
    if batch and batch.quantity >= 3:
        sale = Sale(
            customer=cust_obj,
            payment_method='cash',
            notes='Sample sale',
            created_by=admin_user,
            discount_amount=Decimal('0'),
        )
        sale.save()
        unit_price = batch.selling_price
        gst_rate   = batch.gst_rate
        si = SaleItem(
            sale=sale, medicine=para, batch=batch,
            quantity=3, unit_price=unit_price,
            discount_percent=0, gst_rate=gst_rate,
            cgst_rate=gst_rate/2, sgst_rate=gst_rate/2,
        )
        si.save()
        batch.quantity -= 3
        batch.save()
        subtotal = si.taxable_amount
        cgst     = si.gst_amount / 2
        sgst     = si.gst_amount / 2
        sale.subtotal      = subtotal
        sale.cgst_amount   = cgst
        sale.sgst_amount   = sgst
        sale.total_amount  = subtotal + cgst + sgst
        sale.loyalty_points_earned = int(sale.total_amount / 10)
        sale.save()
        if cust_obj:
            cust_obj.loyalty_points   += sale.loyalty_points_earned
            cust_obj.total_purchases  += sale.total_amount
            cust_obj.save()
        print(f"  Sample sale: {sale.invoice_number} = Rs.{sale.total_amount}")
