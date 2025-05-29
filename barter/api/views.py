from rest_framework import filters, viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from api import (
    filters as api_filters,
    serializers as api_serializers,
)
from ads import (
    models as ads_models,
    utils as ads_utils
)


class AdViewSet(viewsets.ModelViewSet):
    queryset = ads_models.Ad.active_objects.all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = api_serializers.AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['category', 'condition', 'user']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']

    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
        """Возвращает список объявлений пользователя"""
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=['get'],
        url_path='can-make-prop',
        permission_classes=[permissions.IsAuthenticated])
    def can_make_prop(self, request):
        """Возвращает список объявлений к которым можно сделать предложение"""
        queryset = self.get_queryset().exclude(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='categories')
    def categories(self, request):
        """Возвращает список всех категорий"""
        return Response([c[0] for c in ads_models.Ad.CATEGORY_CHOICES])

    @action(detail=False, methods=['get'], url_path='conditions')
    def conditions(self, request):
        """Возвращает список всех состояний"""
        return Response([c[0] for c in ads_models.Ad.CONDITION_CHOICES])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        ad = self.get_object()
        try:
            ads_utils.can_edit_ad(ad, self.request.user)
        except PermissionDenied:
            raise DRFPermissionDenied()
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.user:
            raise DRFPermissionDenied()
        instance.deleted = True
        instance.save()


class ExchangeProposalViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    model = ads_models.ExchangeProposal
    serializer_class = api_serializers.ExchangeProposalSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = api_filters.ExchangeProposalFilter
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        return self.model.get_user_proposals(self.request.user)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return api_serializers.ExchangeProposalUpdateSerializer
        return self.serializer_class

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Возвращает список всех статусов"""
        return Response([c[0] for c in self.model.STATUS_CHOICES])

    @action(detail=False, methods=['get'])
    def role(self, request):
        """Возвращает список всех ролей"""
        return Response([c[0] for c in self.model.ROLE_CHOICES])

    @action(detail=True, methods=['get'], url_path='available-ads-exchange')
    def available_ads_for_exchange(self, request, pk=None):
        """
        Возвращает список объявлений которые
        можно предложить на обмен для данного ad_receiver
        """

        try:
            ad_receiver = ads_models.Ad.active_objects.get(pk=pk)
        except ads_models.Ad.DoesNotExist:
            return Response({'detail': 'Ad not found.'},
                            status=status.HTTP_404_NOT_FOUND
                            )
        ads = ads_models.Ad.get_available_ads_for_exchange(
            ad_receiver, request.user
        )
        serializer = api_serializers.AdSerializer(ads, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        is_sender = getattr(instance.ad_sender, 'user', None) == user
        is_receiver = getattr(instance.ad_receiver, 'user', None) == user
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=kwargs.get('partial', False),
            context={
                **self.get_serializer_context(),
                'is_sender': is_sender, 'is_receiver': is_receiver
            }
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
