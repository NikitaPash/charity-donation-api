# Generated by Django 5.1.5 on 2025-05-29 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0005_alter_campaign_goal_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='created_at',
            field=models.DateField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='goal_amount',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='campaigndocument',
            name='uploaded_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]
