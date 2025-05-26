"""
Django command to mark campaigns as expired once their deadline has passed.
"""
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from campaign.models import Campaign


class Command(BaseCommand):

    def handle(self, *args, **options):
        qs = Campaign.objects.filter(
            deadline__lt=now(),
            status__in=[
                Campaign.CampaignStatusChoice.ACTIVE,
                Campaign.CampaignStatusChoice.ON_MODERATION,
            ]
        )
        user_ids = list(qs.values_list('user_id', flat=True).distinct())
        count = qs.update(status=Campaign.CampaignStatusChoice.EXPIRED)
        from main_app.utils import invalidate_cache
        for uid in user_ids:
            invalidate_cache(f'campaign_list_{uid}', f'my_campaigns_{uid}')
        self.stdout.write(f'Expired {count} campaigns.')
