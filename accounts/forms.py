import re
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from django import forms


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("email", "full_name", "phone", "address", "password1", "password2")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        # Min length
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        # At least 2 digits
        if len(re.findall(r"\d", password1)) < 1:
            raise ValidationError("Password must contain at least one numbers.")

        # At least 1 symbol (non-alphanumeric)
        if not re.search(r"[^\w\s]", password1):
            raise ValidationError("Password must contain at least one symbol (!@#$%^&* etc.).")

        return password2






class CustomerLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
