from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from main.models import Cliente

def dashboard(request):
    if request.user.is_authenticated:
        print("user is authenticated")
        cliente = Cliente.objects.all().filter(cl_user=request.user).first()
        print(cliente)
        # Render only if it's bodega
        if cliente.cl_is_bodega:
            return render(request=request,
                  template_name="dashboard/index.html")
    else:
        print("user is NOT authenticated")
        #return render(request=request,
        #          template_name="main/index.html")
        return HttpResponseRedirect(reverse('main:homepage'))
                  