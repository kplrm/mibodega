from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

#from accounts.models import 

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True, max_length=254)
    first_name = forms.CharField(required = False)
    last_name = forms.CharField(required = False)
    
    is_staff =  forms.BooleanField(required = False, widget=forms.HiddenInput())
    is_active = forms.BooleanField(initial=True, required = False, widget=forms.HiddenInput())
    is_bodega = forms.BooleanField(initial=False, required = False, widget=forms.HiddenInput())

    phone = forms.IntegerField(required = True)
    geolocation = forms.CharField(required = False, widget=forms.HiddenInput())
    ID_listado = forms.IntegerField(required = False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ( # alll field names
            'username',
            'email',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'is_bodega',
            'phone',
            'geolocation',
            'ID_listado',
        )
        widgets = {'geolocation': forms.HiddenInput()}

    def save(self, commit=True): #commit saves data to database
        user = super(RegistrationForm, self).save(commit=False) # when finish edition, it will store the data
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name'] # this is already in django model therefore user.

        user.is_staff = self.cleaned_data['is_staff']
        user.is_active = self.cleaned_data['is_active']
        user.is_bodega = self.cleaned_data['is_bodega']
        user.phone = self.cleaned_data['phone']
        user.geolocation = self.cleaned_data['geolocation']
        user.ID_listado = self.cleaned_data['ID_listado']

        if commit:
            user.save() # saves the data

        return user