from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ( # alll field names
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )
        
    email = forms.EmailField(required = True, max_length=254)
    first_name = forms.CharField(required = True, max_length=254)
    last_name = forms.CharField(required = True, max_length=254)

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

    cl_phone = forms.CharField(required=True,max_length=9)

    def save(self, commit): #commit saves data to database
        client = super(ClientForm, self).save(commit=False) # when finish edition, it will store the data
        client.cl_phone = self.cleaned_data['cl_phone']

        if commit:
            client.save() # saves the data
        return client