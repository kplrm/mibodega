from django.shortcuts import render, redirect # to redirect the user
#from django.http import HttpResponse
from .models import productos_aprobados

from .forms import RegistrationForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate

#from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def homepage(request):
    #return HttpResponse("pythonprogramming.net homepage! Wow so #amaze.")
    return render(request=request, # to reference request
                  template_name="main/index.html", # where to find the specifix template
                  context={"productos_aprobados": productos_aprobados.objects.all()}) # variable name 'pa'

def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('main:homepage'))
    else:
        form = RegistrationForm()

        args = {'form': form}
        return render(request, 'main/register.html', args)