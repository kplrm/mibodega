from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

#from accounts.models import 

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ( # alll field names
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )

    def save(self, commit=True): #commit saves data to database
        user = super(RegistrationForm, self).save(commit=False) # when finish edition, it will store the data
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name'] # this is already in django model therefore user.
        user.email = self.cleaned_data['email']

        if commit:
            user.save() # saves the data

        return user

#class EditProfileForm(UserChangeForm):
#    template_name='/something/else'
#
#    class Meta:
#        model = User
#        fields = (
#            'email',
#            'first_name',
#            'last_name',
#            'password'
#        )
