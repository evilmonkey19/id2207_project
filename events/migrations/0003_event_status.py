# Generated by Django 4.2.6 on 2023-10-28 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_remove_event_preferences_event_decorations_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('created', 'Created'), ('senior_approved', 'Senior Approved'), ('finance_approved', 'Finance Approved'), ('admin_approved', 'Admin Approved')], default=0, max_length=20),
            preserve_default=False,
        ),
    ]
