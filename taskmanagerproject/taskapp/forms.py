from django import forms
from django.contrib.auth import authenticate, get_user_model
from .models import Task, PRIORITY_CHOICES

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={"placeholder": "Your username"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"placeholder": "Your password"}))
    def clean(self):
        cleaned = super().clean()
        user = authenticate(username=cleaned.get("username"), password=cleaned.get("password"))
        if not user:
            raise forms.ValidationError("Invalid username or password.")
        cleaned["user"] = user
        return cleaned

class SignupForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"placeholder": "Create a strong password"}), min_length=8)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={"placeholder": "Repeat your password"}), min_length=8)
    
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Choose a username"}),
            "email": forms.EmailInput(attrs={"placeholder": "your@email.com"}),
        }
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    
    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class TaskForm(forms.ModelForm):
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES)
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control",
            },
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"],
    )


    class Meta:
        model = Task
        fields = ["title", "priority", "description", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Task title"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional details", "class": "form-control"}),
        }

