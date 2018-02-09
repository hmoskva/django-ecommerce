from django.forms import ModelForm

from .models import Address


class AddressForm(ModelForm):
    class Meta:
        model = Address
        exclude = ['billing_profile', 'address_type']