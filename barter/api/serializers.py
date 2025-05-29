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
    comment = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ads_models.ExchangeProposal
        fields = [
            'id', 'ad_sender', 'ad_receiver', 'comment', 'comment_sender',
            'comment_receiver', 'status', 'created_at', 'updated_at', 'deleted'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'deleted', 'status',
            'comment_sender', 'comment_receiver'
        ]

    def validate(self, attrs):
        ad_sender = attrs.get('ad_sender')
        ad_receiver = attrs.get('ad_receiver')
        user = self.context['request'].user

        if ad_receiver:
            valid_receivers = ads_models.Ad.active_objects.exclude(user=user)
            if ad_receiver not in valid_receivers:
                raise serializers.ValidationError(
                    {
                        'ad_receiver': (
                            'This ad_receiver is not available for exchange.'
                        )
                    }
                )
        if ad_sender and ad_receiver:
            available_ads = ads_models.Ad.get_available_ads_for_exchange(
                ad_receiver, user
            )
            if ad_sender not in available_ads:
                raise serializers.ValidationError(
                    {
                        'ad_sender': (
                            'This ad cannot be proposed for exchange with the '
                            'selected ad_receiver.'
                        )
                    }
                )
        return attrs

    def create(self, validated_data):
        comment = validated_data.pop('comment', None)
        if comment is not None:
            validated_data['comment_sender'] = comment
        return super().create(validated_data)


class ExchangeProposalUpdateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ads_models.ExchangeProposal
        fields = [
            'id', 'ad_sender', 'ad_receiver', 'comment', 'comment_sender',
            'comment_receiver', 'status', 'created_at', 'updated_at', 'deleted'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'deleted',
            'ad_sender', 'ad_receiver',
            'comment_sender', 'comment_receiver'
        ]

    def validate(self, attrs):
        is_sender = self.context.get('is_sender', False)
        is_receiver = self.context.get('is_receiver', False)
        instance = self.instance

        if not (is_sender or is_receiver):
            raise serializers.ValidationError(
                {
                    'detail': (
                        'You do not have permission to update this proposal.'
                    )
                }
            )

        if instance.status != ads_models.ExchangeProposal.PENDING:
                raise serializers.ValidationError(
                    {
                        'detail': (
                            f'You can only edit proposals with status '
                            f'{ads_models.ExchangeProposal.PENDING}.'
                        )
                    }
                )

        if is_sender:
            status = attrs.get('status', instance.status)
            allowed_statuses = [
                ads_models.ExchangeProposal.PENDING,
                ads_models.ExchangeProposal.DECLINED
            ]
            if status not in allowed_statuses:
                raise serializers.ValidationError(
                    {
                        'status': (
                            f'Sender can set status to '
                            f'{ads_models.ExchangeProposal.PENDING} or '
                            f'{ads_models.ExchangeProposal.DECLINED}.'
                        )
                    }
                )
        return attrs

    def update(self, instance, validated_data):
        is_sender = self.context.get('is_sender', False)
        is_receiver = self.context.get('is_receiver', False)

        comment = validated_data.pop('comment', None)
        if comment is not None:
            if is_sender:
                validated_data['comment_sender'] = comment
            elif is_receiver:
                validated_data['comment_receiver'] = comment

        return super().update(instance, validated_data)
