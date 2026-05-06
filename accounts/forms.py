from django import forms
from django.contrib.auth import get_user_model

from .models import CandidateProfile


class SignupForm(forms.Form):
    USER_TYPE_CHOICES = CandidateProfile.USER_TYPE_CHOICES
    DISABILITY_CHOICES = [
        ("", "Select disability type"),
        ("prefer_not_to_say", "Prefer not to say"),
        ("visual", "Visual impairment"),
        ("hearing", "Hearing impairment"),
        ("physical", "Physical disability"),
        ("speech", "Speech impairment"),
        ("learning", "Learning disability"),
        ("mental_health", "Mental health condition"),
        ("multiple", "Multiple disabilities"),
        ("other", "Other"),
    ]

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)
    first_name = forms.CharField(max_length=80)
    last_name = forms.CharField(max_length=80, required=False)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    profile_photo = forms.FileField(required=False)
    disability = forms.ChoiceField(choices=DISABILITY_CHOICES, required=False)
    current_location = forms.CharField(max_length=120, required=False)
    preferred_location = forms.CharField(max_length=120, required=False)
    education = forms.CharField(required=False, widget=forms.Textarea)
    employment_history = forms.CharField(required=False, widget=forms.Textarea)
    skills = forms.CharField(required=False, widget=forms.Textarea)
    resume = forms.FileField(required=False)
    hide_from_recruiters = forms.BooleanField(required=False)
    job_alerts = forms.BooleanField(required=False)
    terms = forms.BooleanField()

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if CandidateProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("An account with this mobile number already exists.")
        return phone

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm_password = cleaned.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        if password and len(password) < 6:
            self.add_error("password", "Password must be at least 6 characters.")
        if cleaned.get("user_type") == CandidateProfile.EXPERIENCED and not cleaned.get("employment_history"):
            self.add_error("employment_history", "Employment history is required for experienced candidates.")
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember = forms.BooleanField(required=False)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = get_user_model().objects.filter(email__iexact=email.lower()).first()
            if user is None or not user.check_password(password):
                raise forms.ValidationError("Invalid email or password.")
            cleaned["user"] = user
        return cleaned


class ProfileEditForm(forms.Form):
    USER_TYPE_CHOICES = CandidateProfile.USER_TYPE_CHOICES
    DISABILITY_CHOICES = SignupForm.DISABILITY_CHOICES

    first_name = forms.CharField(max_length=80)
    last_name = forms.CharField(max_length=80, required=False)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)
    profile_photo = forms.FileField(required=False)
    disability = forms.ChoiceField(choices=DISABILITY_CHOICES, required=False)
    current_location = forms.CharField(max_length=120, required=False)
    preferred_location = forms.CharField(max_length=120, required=False)
    education = forms.CharField(required=False, widget=forms.Textarea)
    employment_history = forms.CharField(required=False, widget=forms.Textarea)
    skills = forms.CharField(required=False, widget=forms.Textarea)
    resume = forms.FileField(required=False)
    hide_from_recruiters = forms.BooleanField(required=False)
    job_alerts = forms.BooleanField(required=False)

    def __init__(self, *args, user=None, profile=None, **kwargs):
        self.user = user
        self.profile = profile
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        existing = get_user_model().objects.filter(email__iexact=email)
        if self.user:
            existing = existing.exclude(pk=self.user.pk)
        if existing.exists():
            raise forms.ValidationError("Another account already uses this email.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        existing = CandidateProfile.objects.filter(phone=phone)
        if self.profile:
            existing = existing.exclude(pk=self.profile.pk)
        if existing.exists():
            raise forms.ValidationError("Another account already uses this mobile number.")
        return phone


class OTPForm(forms.Form):
    otp = forms.CharField(min_length=6, max_length=6)


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if not get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("No account found with this email.")
        return email


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm_password = cleaned.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        if password and len(password) < 6:
            self.add_error("password", "Password must be at least 6 characters.")
        return cleaned
