import re
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from django import forms

import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("email", "full_name", "phone", "address", "password1", "password2")

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name")

        # Only alphabets and spaces allowed
        if not re.match(r"^[A-Za-z\s]+$", full_name):
            raise ValidationError("Name must contain only alphabets (no digits or symbols).")

        # Max length 20 chars
        if len(full_name.replace(" ", "")) > 20:
            raise ValidationError("Name cannot exceed 20 characters (excluding spaces).")

        return full_name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        # Must be exactly 10 digits
        if not re.fullmatch(r"\d{10}", phone):
            raise ValidationError("Phone number must be exactly 10 digits and contain no letters.")

        return phone

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # Basic email pattern validation
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            raise ValidationError("Please enter a valid email address.")

        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        # Password length must be exactly 10 chars (as per your test case)
        if len(password1) != 10:
            raise ValidationError("Password must be exactly 10 characters long.")

        # At least 1 number
        if len(re.findall(r"\d", password1)) < 1:
            raise ValidationError("Password must contain at least one number.")

        # At least 1 symbol
        if not re.search(r"[^\w\s]", password1):
            raise ValidationError("Password must contain at least one symbol (!@#$%^&* etc.).")

        return password2






class CustomerLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
