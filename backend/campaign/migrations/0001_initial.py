# Generated by Django 5.1.4 on 2025-01-25 11:48

import campaign.models
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('goal_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('raised_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('deadline', models.DateTimeField(default=campaign.models.default_deadline)),
                (
                    'status',
                    models.CharField(
                        choices=[('AC', 'Active'), ('CO', 'Completed')], db_index=True, default='AC', max_length=10
                    )
                ),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
