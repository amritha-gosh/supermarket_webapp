from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'address_line1', 'address_line2', 'city', 'postcode', 'phone']

class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    address = forms.CharField(max_length=255, required=True)
    address2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=True)
    postcode = forms.CharField(max_length=12, required=True)
    phone = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card / Apple Pay'),
        ('cod', 'Cash on Delivery'),
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        initial='card',
        required=True,
        label="Payment method"
    )



