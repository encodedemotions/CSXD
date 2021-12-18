from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from mongodata.models import Data, SensitiveData
from users.decorators import lecturer_required
from .forms import DataForm
import rsa

public_key, private_key = rsa.newkeys(512)


@login_required
def view_data(request):
    return render(request, '../templates/data.html', {'data_name': "View all Public Data", 'data': Data.objects.all()})


@login_required
@lecturer_required
def view_private_data(request):
    data = SensitiveData.objects.all()
    for d in data:
        backup = d.data
        try:
            d.data = rsa.decrypt(d.data.encode('latin1'), private_key)
        except:
            d.data = backup

    return render(request, '../templates/data.html', {'data_name': "View all Private Data", 'data': data})


@login_required
@lecturer_required
def view_new_private_data(request):
    if request.method == "POST":
        form = DataForm(request.POST or None)
        if form.is_valid():
            string_data = form['data'].data
            encrypted_data = rsa.encrypt(string_data.encode(), public_key)
            obj = SensitiveData(data=encrypted_data.decode('latin1', errors="ignore"))
            SensitiveData.save(obj)

            return redirect('view_private_data')
    else:
        form = DataForm()
    return render(request, '../templates/add_data.html', {'form': form})


@login_required
def view_new_data(request):
    if request.method == "POST":
        form = DataForm(request.POST or None)
        if form.is_valid():
            string_data = form['data'].data
            obj = Data(data=string_data)
            Data.save(obj)
            return redirect('view_data')
    else:
        form = DataForm()
    return render(request, '../templates/add_data.html', {'form': form})
