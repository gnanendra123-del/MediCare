from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Prescription
from customers.models import Customer
from .forms import PrescriptionForm

@login_required
def prescription_list(request):
    prescriptions = Prescription.objects.select_related('customer').order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        prescriptions = prescriptions.filter(status=status)
    return render(request, 'prescriptions/prescription_list.html', {'prescriptions': prescriptions, 'status': status})

@login_required
def prescription_add(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save()
            messages.success(request, f'Prescription #{prescription.id} uploaded successfully.')
            return redirect('prescription_list')
    else:
        form = PrescriptionForm()
    return render(request, 'prescriptions/prescription_form.html', {'form': form})

@login_required
def prescription_verify(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        prescription.status = 'verified' if action == 'verify' else 'rejected'
        prescription.verified_by = request.user
        prescription.save()
        messages.success(request, f'Prescription {prescription.status}.')
        return redirect('prescription_list')
    return render(request, 'prescriptions/prescription_verify.html', {'prescription': prescription})

@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    return render(request, 'prescriptions/prescription_detail.html', {'prescription': prescription})
