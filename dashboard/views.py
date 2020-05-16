from django.shortcuts import render

def dashboard(request):
    if request.user.is_authenticated:
        print("user is authenticated")
        cliente = Cliente.objects.all().filter(cl_user=request.user).first()
        print("cliente")
    else:
        print("user is NOT authenticated")
    return render(request=request,
                  template_name="dashboard/index.html")
                  