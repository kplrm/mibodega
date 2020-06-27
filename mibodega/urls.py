from django.contrib import admin
from django.urls import path, include

#DG
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
#

reset_subject = "main/password_reset_subject.txt"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('main.urls')),

    # Password Reset View
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="main/password_reset.html", subject_template_name=reset_subject), name='password_reset'),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="main/password_reset_done.html"), name='password_reset_done'),
    path("password_reset_confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="main/password_reset_confirm.html"), name='password_reset_confirm'),
    path("password_reset_complete/done/", auth_views.PasswordResetCompleteView.as_view(template_name="main/password_reset_complete.html"), name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
