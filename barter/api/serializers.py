from rest_framework import serializers
from ads import models as ads_models


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ads_models.Ad
        fields = [
            'id', 'user', 'title', 'description', 'image_url',
            'category', 'condition', 'created_at', 'updated_at', 'deleted'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'deleted']


class ExchangeProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ads_models.ExchangeProposal
        fields = [
            'id', 'ad_sender', 'ad_receiver', 'comment_sender',
            'comment_receiver', 'status', 'created_at', 'updated_at', 'deleted'
        ]
        read_only_fields = ['created_at', 'updated_at', 'deleted']
