from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from .models import BLOOD_GROUPS, DonorProfile


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })
    )

    # ---- New donor fields ----
    blood_group = forms.ChoiceField(
        choices=[('', 'Select your blood group')] + BLOOD_GROUPS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 01XXXXXXXXX',
            'autocomplete': 'tel',
        })
    )

    district = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your district',
        })
    )

    area = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your area / thana (optional)',
        })
    )
    # --------------------------

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password',
        })
    )

    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password again',
            'autocomplete': 'new-password',
        })
    )

    field_order = [
        'first_name', 'last_name', 'username', 'email',
        'blood_group', 'phone', 'district', 'area',
        'password1', 'password2',
    ]

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
        ]

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'An account with this email address already exists.'
            )

        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            DonorProfile.objects.create(
                user=user,
                blood_group=self.cleaned_data['blood_group'],
                phone=self.cleaned_data['phone'],
                district=self.cleaned_data['district'].strip(),
                area=self.cleaned_data['area'].strip(),
            )

        return user

from django.utils import timezone

class ProfileForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = ["blood_group", "phone", "district", "area", "last_donated_at", "is_active"]
        labels = {
            "last_donated_at": "Last donation date",
            "is_active": "Show me in donor search",
        }
        widgets = {
            "last_donated_at": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean_last_donated_at(self):
        d = self.cleaned_data.get("last_donated_at")
        if d and d > timezone.localdate():
            raise forms.ValidationError("The donation date can't be in the future.")
        return d