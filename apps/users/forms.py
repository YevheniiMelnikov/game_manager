from django import forms
from django.contrib.auth import get_user_model

from apps.users.enums import UserRole

User = get_user_model()


class RegistrationForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=UserRole.choices())
    company_id = forms.IntegerField(required=False)

    def clean(self) -> dict:
        data = super().clean()
        if data.get("role") == UserRole.COMPANYADMIN.value and not data.get("company_id"):
            self.add_error("company_id", "Company ID is required for CompanyAdmin role")
        return data
