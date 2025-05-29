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
        fields = ['ad_sender', 'comment_sender']
        widgets = {
            'comment_sender': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, ad_receiver=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['ad_sender'].queryset = (
                ads_models.Ad.get_available_ads_for_exchange(
                    ad_receiver,
                    user,
                )
            )


class ExchangeProposalUpdateForm(forms.ModelForm):
    class Meta:
        model = ads_models.ExchangeProposal
        fields = []

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        proposal = self.instance

        # Определяем роль пользователя
        is_sender = proposal.ad_sender.user_id == user.id
        is_receiver = proposal.ad_receiver.user_id == user.id

        # Для отправителя
        if is_sender:
            self.fields['comment_sender'] = forms.CharField(
                label="Комментарий",
                required=False,
                widget=forms.Textarea(attrs={'rows': 3}),
                initial=proposal.comment_sender
            )
            self.fields['status'] = forms.ChoiceField(
                label="Статус",
                choices=[
                    (ads_models.ExchangeProposal.PENDING, 'Ожидает'),
                    (ads_models.ExchangeProposal.DECLINED, 'Отклонен')
                ],
                required=True
            )

        # Для получателя
        if is_receiver:
            self.fields['comment_receiver'] = forms.CharField(
                label="Комментарий",
                required=False,
                widget=forms.Textarea(attrs={'rows': 3}),
                initial=proposal.comment_receiver
            )
            self.fields['status'] = forms.ChoiceField(
                label="Статус",
                choices=ads_models.ExchangeProposal.STATUS_CHOICES,
                required=True
            )

    def save(self, commit=True):
        proposal = super().save(commit=False)
        for field in ('comment_sender', 'comment_receiver', 'status'):
            if field in self.cleaned_data:
                setattr(proposal, field, self.cleaned_data[field])
        if commit:
            proposal.save()
        return proposal
