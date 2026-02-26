from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Listing, WholesaleDetail, ServiceDetail, Profile

class BaseStyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs.update({'class': 'rounded text-indigo-600 focus:ring-indigo-500'})
            else:
                field.widget.attrs.update({
                    'class': 'w-full bg-slate-50 border-2 border-slate-100 rounded-2xl px-4 py-3 focus:border-indigo-500 focus:bg-white outline-none transition duration-200 font-medium text-slate-700 placeholder-slate-400'
                })

class SosoSignupForm(BaseStyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class ListingForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'category', 'title', 'description', 'media',
            'price', 'trade_type', 'condition', 'auction_end'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell the Wild West about your item...'}),
            'auction_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'media': forms.ClearableFileInput(attrs={'accept': 'image/*,video/*'}),
        }
        labels = {
            'trade_type': 'Mode of Trade',
            'auction_end': 'Auction End Time (If Auction)',
            'media': 'Upload Image or Video',
        }

class WholesaleForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = WholesaleDetail
        fields = ['min_order_qty', 'unit_name']
        labels = {
            'min_order_qty': 'Minimum Order Quantity',
            'unit_name': 'Measurement Unit (e.g. Bags, Tons, Crates)',
        }

class ServiceForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceDetail
        fields = ['vehicle_info', 'location_lat', 'location_lon']
        labels = {
            'vehicle_info': 'Vehicle/Provider Details',
            'location_lat': 'Current Latitude',
            'location_lon': 'Current Longitude',
        }
        widgets = {
            'location_lat': forms.HiddenInput(),
            'location_lon': forms.HiddenInput(),
        }

class ProfileUpdateForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'location_name', 'phone_number']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }