from django.shortcuts import render, redirect # to redirect the user
from .models import ProductosAprobados, ListaDeProductos

from .forms import RegistrationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages # to send unique messages to the users

# Create your views here.
def homepage(request):
    #DG
    for product in ListaDeProductos.objects.all():
        print(product.discount_rate)
    #
    return render(request=request, # to reference request
                  template_name="main/index.html", # where to find the specifix template
                  context={"ProductosAprobados": ProductosAprobados.objects.all()}) # variable name 'pa'

def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = user.username # normalize to a standard format
            # Messages are stored only once. When they are delivered, they also are deleted.
            messages.success(request,f"Cuenta creada exitosamente") # (request, exact message)
            auth_login(request, user)
            messages.info(request,f"Bienvenido: {username}")
            return redirect('main:homepage')
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
            
    form = RegistrationForm() # Rerender form
    return render(request, 'main/register.html', context={"form":form})

def logout_request(request):
    auth_logout(request)
    messages.info(request, "Sessión cerrada. Vuelve pronto.")
    return redirect("main:homepage")

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.clean()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                print("exito")
                auth_login(request, user)
                messages.info(request,f"Bienvenido: {username}")
                return redirect('main:homepage')
            else:
                messages.error(request,f"Usuario o contraseña incorrecta")
        # in case the form is invalid
        messages.error(request,f"Usuario o contraseña incorrecta")

    form = AuthenticationForm()
    return render(request, "main/login.html", {"form":form})