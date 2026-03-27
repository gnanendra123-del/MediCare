from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Customer, MedicineReminder
from .forms import CustomerForm, ReminderForm

@login_required
def customer_list(request):
    customers = Customer.objects.filter(is_active=True).order_by('name')
    query = request.GET.get('q', '')
    if query:
        from django.db.models import Q
        customers = customers.filter(Q(name__icontains=query) | Q(phone__icontains=query))
    return render(request, 'customers/customer_list.html', {'customers': customers, 'query': query})

@login_required
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.name}" added successfully.')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Add Customer'})

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated.')
            return redirect('customer_detail', pk=pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Edit Customer'})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    sales = customer.sales.filter(status='completed').order_by('-created_at')[:10]
    prescriptions = customer.prescriptions.order_by('-created_at')[:5]
    reminders = customer.reminders.order_by('reminder_date')
    return render(request, 'customers/customer_detail.html', {
        'customer': customer, 'sales': sales, 'prescriptions': prescriptions, 'reminders': reminders
    })

@login_required
def add_reminder(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.customer = customer
            reminder.save()
            messages.success(request, 'Reminder set.')
            return redirect('customer_detail', pk=pk)
    else:
        form = ReminderForm()
    return render(request, 'customers/reminder_form.html', {'form': form, 'customer': customer})

@login_required
def send_reminder_email(request, reminder_pk):
    reminder = get_object_or_404(MedicineReminder, pk=reminder_pk)
    if reminder.customer.email:
        try:
            send_mail(
                f"Medicine Refill Reminder - {reminder.medicine_name}",
                f"Dear {reminder.customer.name},\n\nThis is a reminder to refill your medicine: {reminder.medicine_name}.\n\nPlease visit MediShop at your earliest convenience.\n\nNotes: {reminder.notes}\n\nRegards,\nMediShop Team",
                settings.DEFAULT_FROM_EMAIL,
                [reminder.customer.email],
            )
            reminder.is_sent = True
            reminder.save()
            messages.success(request, 'Reminder email sent.')
        except Exception as e:
            messages.error(request, f'Email failed: {e}')
    else:
        messages.warning(request, 'Customer has no email on file.')
    return redirect('customer_detail', pk=reminder.customer.pk)
