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
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email") # Password fields are handled by UserCreationForm

class ListingForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['category', 'title', 'description', 'media', 'price', 'trade_type', 'condition', 'auction_end']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell the Wild West about your item...'}),
            'auction_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'media': forms.ClearableFileInput(attrs={'accept': 'image/*,video/*'}),
        }

class WholesaleForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = WholesaleDetail
        fields = ['min_order_qty', 'unit_name']

class ServiceForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceDetail
        fields = ['vehicle_info', 'location_lat', 'location_lon']
        widgets = {
            'location_lat': forms.HiddenInput(),
            'location_lon': forms.HiddenInput(),
        }