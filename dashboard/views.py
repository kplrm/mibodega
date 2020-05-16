from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from main.models import Cliente

#@login_required(login_url='/accounts/login/')
def dashboard(request):
    if request.user.is_authenticated:
        print("user is authenticated")
        cliente = Cliente.objects.all().filter(cl_user=request.user).first()
        print(cliente)
        # Render only if it's bodega
        # To avoid any rendering or calculation if it's not a bodega
        if cliente.cl_is_bodega == False:
            print("first exit")
            return HttpResponseRedirect(reverse('main:homepage'))

        if cliente.cl_is_bodega:
            return render(request=request,
                  template_name="dashboard/index.html")
        else:
            print("second exit")
            return HttpResponseRedirect(reverse('main:homepage'))

    else:
        print("user is NOT authenticated")
        return HttpResponseRedirect(reverse('main:homepage'))
                  