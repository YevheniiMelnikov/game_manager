from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    company_id = forms.IntegerField(required=False)

    def clean(self):
        data = super().clean()
        role = data.get("role")
        company_id = data.get("company_id")
        if role == "CompanyAdmin" and not company_id:
            self.add_error("company_id", "Company ID is required for CompanyAdmin role.")
        return data
