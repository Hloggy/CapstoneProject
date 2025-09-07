from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Task

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"placeholder": "Your username"})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Your password"})
    )

    def clean(self):
        cleaned = super().clean()
        user = authenticate(
            username=cleaned.get("username"),
            password=cleaned.get("password"),
        )
        if not user:
            raise forms.ValidationError("Invalid username or password.")
        cleaned["user"] = user
        return cleaned


class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = Task
        fields = ["title", "description", "priority", "due_date"]


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "your@email.com", "class": "form-control"})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Choose a username", "class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"placeholder": "Create a strong password", "class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"placeholder": "Confirm your password", "class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
