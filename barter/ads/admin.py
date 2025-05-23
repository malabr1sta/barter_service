from django.contrib import admin
from ads import models as ads_models


admin.site.disable_action("delete_selected")

@admin.register(ads_models.Ad)
class AdAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'user', 'title' , 'category', 'condition',
        'created_at', 'updated_at',
    )
    list_display_links = ('id',)
    list_filter = ('category', 'condition', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_deleted']

    def mark_deleted(self, request, queryset):
        queryset.update(deleted=True)
    mark_deleted.short_description = "Удалить"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(deleted=False)


@admin.register(ads_models.DeletedAd)
class DeletedAdAdmin(AdAdmin):

    actions = ['mark_undeleted']

    def mark_undeleted(self, request, queryset):
        queryset.update(deleted=False)
    mark_undeleted.short_description = "Восстановить"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(deleted=True)


@admin.register(ads_models.ExchangeProposal)
class ExchangeProposalAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'ad_sender', 'ad_receiver', 'status',
        'created_at', 'updated_at'
    )
    list_display_links = ('id',)
    list_filter = ('status', 'created_at')
    search_fields = (
        'ad_sender__title', 'ad_receiver__title',
    )
    readonly_fields = ('created_at', 'updated_at')
