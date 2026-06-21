from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from .models import CustomUser

from django import forms
from .models import CustomUser

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'mobile_number', 'age', 'gender', 
                  'height', 'weight', 'fitness_goal', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]'}),
            'mobile_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]'}),
            'age': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]'}),
            'gender': forms.Select(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]'}),
            'height': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]', 'step': '0.1'}),
            'weight': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]', 'step': '0.1'}),
            'fitness_goal': forms.Select(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]'}),
            'profile_picture': forms.FileInput(attrs={'class': 'w-full px-3 py-2 bg-[#0F0F1A] border border-[#E94560]/30 rounded-lg text-white focus:outline-none focus:border-[#E94560]', 'accept': 'image/*'}),
        }


class UserSettingsForm(forms.ModelForm):
    """Form for user settings"""
    
    class Meta:
        model = CustomUser
        fields = ['email_verified', 'is_verified']
        widgets = {
            'email_verified': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#E94560] rounded'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#E94560] rounded'}),
        }

class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'mobile_number', 'age', 
                 'gender', 'height', 'weight', 'fitness_goal']
    
    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError('Passwords do not match')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        first_name = self.cleaned_data.get('first_name', '').strip()
        last_name = self.cleaned_data.get('last_name', '').strip()
        user.full_name = " ".join(part for part in [first_name, last_name] if part)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user