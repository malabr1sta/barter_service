from django import forms
from ads import models as ads_models


class AdForm(forms.ModelForm):
    class Meta:
        model = ads_models.Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'ad-input',
                'placeholder': 'Заголовок'
            }),
            'description': forms.Textarea(attrs={
                'class': 'ad-input',
                'placeholder': 'Описание',
                'rows': 4
            }),
            'image_url': forms.ClearableFileInput(attrs={
                'class': 'ad-input'
            }),
            'category': forms.Select(attrs={
                'class': 'ad-input'
            }),
            'condition': forms.Select(attrs={
                'class': 'ad-input'
            }),
        }

class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ads_models.ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'comment']
