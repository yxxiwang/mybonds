from django import forms
from registration.forms import RegistrationForm
from django.contrib.auth.models import User

class Email(forms.EmailField): 
    def clean(self, value):
        super(Email, self).clean(value)
        try:
            User.objects.get(email=value)
            raise forms.ValidationError("This email is already registered. Use the 'forgot password' link on the login page")
        except User.DoesNotExist:
            return value


class UserRegistrationForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Repeat your password")
    # email will be become username
    email = Email()

    def clean_password(self):
        if self.data['password1'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password1']
    
class CustomerCreateNewLoginForm(forms.Form):
    """ 
    Form for creating new login
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    check_password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
      try:
        if self.cleaned_data['password'] != self.cleaned_data['check_password']:
          raise forms.ValidationError("Passwords entered do not match")
      except KeyError:
        # didn't find what we expected in data - fields are blank on front end.  Fields
        # are required by default so we don't need to worry about validation
        pass
      return self.cleaned_data

class CreateUserForm(forms.Form):
    username = forms.CharField(max_length=30)
#    first_name = forms.CharField()
#    last_name = forms.CharField()
    password1=forms.CharField(max_length=30,widget=forms.PasswordInput()) #render_value=False
    password2=forms.CharField(max_length=30,widget=forms.PasswordInput())
    email=forms.EmailField(required=False)
     
    def clean_username(self): # check if username dos not exist before
        try:
            User.objects.get(username=self.cleaned_data['username']) #get user from user model
        except User.DoesNotExist :
            return self.cleaned_data['username']
    
        raise forms.ValidationError("this user exist already")
    
    
    def clean(self): # check if password 1 and password2 match each other
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:#check if both pass first validation
            if self.cleaned_data['password1'] != self.cleaned_data['password2']: # check if they match each other
                raise forms.ValidationError("passwords dont match each other")
    
        return self.cleaned_data
    
    
    def save(self): # create new user
        new_user=User.objects.create_user(username=self.cleaned_data['username'],
                                        first_name=self.cleaned_data['first_name'],
                                        last_name=self.cleaned_data['last_name'],
                                        password=self.cleaned_data['password1'],
                                        email=self.cleaned_data['email'],
                                            )
    
        return new_user