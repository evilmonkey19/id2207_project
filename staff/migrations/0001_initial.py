# Generated by Django 4.2.6 on 2023-10-29 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recruitment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_type', models.CharField(choices=[('full', 'Full-time'), ('part', 'Part-time')], default='full', max_length=5)),
                ('requesting_department', models.CharField(choices=[('admin', 'Administration'), ('services', 'Services'), ('production', 'Production'), ('financial', 'Financial')], max_length=20)),
                ('years_of_experience', models.IntegerField()),
                ('job_title', models.CharField(max_length=255)),
                ('job_description', models.TextField()),
                ('_status', models.CharField(choices=[('pending_hr_approval', 'Pending HR Approval'), ('pending_manager_approval', 'Pending Manager Approval'), ('approved', 'Approved')], default='pending_hr_approval', max_length=30)),
            ],
        ),
    ]
