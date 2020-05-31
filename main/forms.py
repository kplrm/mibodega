from django import forms
from django.contrib.auth.models import User
#from django.contrib.auth.forms import UserCreationForm
from .models import Cliente, Bodega #Cart

from django import forms
from django.db import models
from django.contrib.auth import password_validation #authenticate, get_user_model, 
from django.utils.translation import gettext, gettext_lazy as _

################################################# IMPORTANT COMMENT #################################################
#
# TO CHANGE label AND help_text ON USERNAME FIELD THE FOLLOWING FILES WERE DIRECTLY EDITED FROM THE DJANGO REPOSITORY
# from ~/[YOUR ENVIRONMENT]/lib/python3.6/site-packages/django/contrib/auth
# in models.py 
# in class AbstractUser(AbstractBaseUser, PermissionsMixin)
# in username = models.CharField()
# change:       _('username'),          to:     _('Usuario*'),
# change:       help_text=_( ... ),     to:     help_text=_('Sólo se permite letras y números.'),
# change:       'unique': _( ... ),     to:     'unique': _("Este usuario ya lo está usando."),
################################################# IMPORTANT COMMENT #################################################

######################## FROM django.contrib.auth ########################
class UsernameField(forms.CharField):
    def to_python(self, value):
        return unicodedata.normalize('NFKC', super().to_python(value))

    def widget_attrs(self, widget):
        return {
            **super().widget_attrs(widget),
            'autocapitalize': 'none',
            'autocomplete': 'username',
        }

class UserCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _('Ambos campos de contraseña no coinciden. Revise que haya colocado repetido bien la contraseña.'),
    }
    password1 = forms.CharField(
        label=_("Contraseña*"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        #help_text=password_validation.password_validators_help_text_html(),
        help_text=_("Debe tener mínimo 8 caracteres entre números y letras."),
    )
    password2 = forms.CharField(
        label=_("Repita su contraseña*"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Verificamos que ambos campos coincidan."),
    )

    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
######################## FROM django.contrib.auth ########################

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )

    email = forms.EmailField(label=_("E-mail*"), max_length=254, required = True)
    first_name = forms.CharField(label=_("Nombre"), strip=False, max_length=254, required = False) # False = do not strip white spaces
    last_name = forms.CharField(label=_("Apellido"), strip=False, max_length=254, required = False) # False = do not strip white spaces

    def save(self, commit=True): #commit saves data to database
        user = super(RegistrationForm, self).save(commit=False) # when finish edition, it will store the data
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save() # saves the data

        return user

class ClientForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = (
            'cl_phone',
        )

    cl_phone = forms.CharField(label=_("Celular*"),strip=False,max_length=9,required = True)

    def save(self, commit): #commit saves data to database
        client = super(ClientForm, self).save(commit=False) # when finish edition, it will store the data
        client.cl_phone = self.cleaned_data['cl_phone']

        if commit:
            client.save() # saves the data
        return client

class BodegaForm(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = (
            'bd_name',
            'bd_ruc',
        )

    bd_name = forms.CharField(label=_("Nombre comercial*"),strip=False,max_length=100,required=True)
    bd_ruc = forms.CharField(label=_("RUC o DNI"),strip=False,max_length=100,required=True)

    def save(self, client, commit): #commit saves data to database
        bodega = super(BodegaForm, self).save(commit=False) # when finish edition, it will store the data
        bodega.bd_user = client.cl_user
        bodega.bd_name = self.cleaned_data['bd_name']
        bodega.bd_ruc = self.cleaned_data['bd_ruc']
        bodega.bd_email = client.cl_email
        bodega.bd_phone = client.cl_phone

        if commit:
            bodega.save() # saves the data
        return bodega






#########################################
#class CartForm(forms.ModelForm):
#    class Meta:
#        model = Cart
#        fields = (
#        )
#
#    #cl_phone = forms.CharField(required=True,max_length=9)
#
#    def save(self, commit): #commit saves data to database
#        cart = super(CartForm, self).save(commit=False) # when finish edition, it will store the data
#        #client.cl_phone = self.cleaned_data['cl_phone']
#
#        if commit:
#            cart.save() # saves the data
#        return cart