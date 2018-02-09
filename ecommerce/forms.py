from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ContactForm(forms.Form):
    fullname = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Fullname'}))
    email = forms.EmailField(max_length=50, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }
    ))
    message = forms.CharField(max_length=350, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Your message'

    }))

    def clean_email(self):
        email = self.cleaned_data['email']
        if 'gmail.com' not in email:
            raise forms.ValidationError('Email must be gmail.com')
        return email


