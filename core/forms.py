from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from .models import UserProfile

class SignUpForm(UserCreationForm):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("tutor", "Tutor"),
    ]

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

# NEW: Profile Update Form
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'school', 'bio']  # Removed 'role'
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'phone': forms.TextInput(attrs={'placeholder': '+263...'}),
            'school': forms.TextInput(attrs={'placeholder': 'Your school name'}),
        }

# NEW: Custom Password Reset Form with Security Questions (Optional)
class SecurityQuestionPasswordResetForm(forms.Form):
    email = forms.EmailField(required=True)
    security_answer = forms.CharField(
        max_length=100, 
        required=True,
        label="What was your first pet's name?"  # Customize question
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        answer = cleaned_data.get('security_answer')
        
        try:
            user = User.objects.get(email=email)
            profile = user.userprofile
            # Check if security answer matches (stored hashed)
            if not profile.check_security_answer(answer):
                raise ValidationError("Security answer is incorrect.")
        except User.DoesNotExist:
            raise ValidationError("No account found with this email.")
        
        return cleaned_data