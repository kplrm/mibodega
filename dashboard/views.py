from django.shortcuts import render

def dashboard(request):
    if request.user.is_authenticated:
        print("user is authenticated")
    else:
        print("user is NOT authenticated")
    return render(request=request,
                  template_name="dashboard/index.html")
                  