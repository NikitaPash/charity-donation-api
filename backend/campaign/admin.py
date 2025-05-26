"""
Django admin customizations for Campaign model.
"""
import logging

from django.contrib import admin

from .models import Campaign, CampaignDocument

logger = logging.getLogger(__name__)


def approve_reject_campaigns(queryset, action):
    count, status_message = None, None
    qs = queryset.filter(status=Campaign.CampaignStatusChoice.ON_MODERATION)
    user_ids = list(qs.values_list('user_id', flat=True).distinct())

    if action == 'approve':
        count = qs.update(status=Campaign.CampaignStatusChoice.ACTIVE)
        status_message = 'approved'
    elif action == 'reject':
        count = qs.update(status=Campaign.CampaignStatusChoice.REJECTED)
        status_message = 'rejected'

    from main_app.utils import invalidate_cache
    for uid in user_ids:
        invalidate_cache(f'campaign_list_{uid}', f'my_campaigns_{uid}')

    logger.info(f'{count} campaign(s) {status_message}.')
    return f'{count} campaign(s) {status_message}.'


class CampaignDocumentInline(admin.TabularInline):
    model = CampaignDocument
    extra = 1
    readonly_fields = ('uploaded_at',)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at', 'deadline')
    list_filter = ('status',)
    inlines = [CampaignDocumentInline]
    actions = ['approve_campaigns', 'reject_campaigns']

    @admin.action(description='Approve selected campaigns')
    def approve_campaigns(self, request, queryset):
        message = approve_reject_campaigns(queryset, 'approve')
        self.message_user(request, message)

    @admin.action(description='Reject selected campaigns')
    def reject_campaigns(self, request, queryset):
        message = approve_reject_campaigns(queryset, 'reject')
        self.message_user(request, message)


@admin.register(CampaignDocument)
class CampaignDocumentAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'document', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
