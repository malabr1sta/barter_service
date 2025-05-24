from django import forms
from django.db.models import Q
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
        fields = ['ad_sender', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, ad_receiver=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            # Исключаем объявления с "pending" предложением к ad_receiver
            exclude_received = Q(
                received_proposals__status=ads_models.ExchangeProposal.PENDING,
                received_proposals__ad_sender=ad_receiver
            )
            # Исключаем объявления с "pending" предложением от ad_receiver
            exclude_sent = Q(
                sent_proposals__status=ads_models.ExchangeProposal.PENDING,
                sent_proposals__ad_receiver=ad_receiver
            )

            self.fields['ad_sender'].queryset = (
                ads_models.Ad.active_objects
                .filter(user=user)
                # Исключаем объявления самому себе
                .exclude(user=ad_receiver.user)
                .exclude(exclude_received)
                .exclude(exclude_sent)
            )
