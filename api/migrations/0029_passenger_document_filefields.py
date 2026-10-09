from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_pagecontent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passenger',
            name='passport_photo',
            field=models.FileField(blank=True, help_text='Passport photo page (image or PDF)', null=True, upload_to='passports/'),
        ),
        migrations.AlterField(
            model_name='passenger',
            name='photo_id',
            field=models.FileField(blank=True, help_text='NRIC, FIN, or other photo ID (image or PDF)', null=True, upload_to='photo_ids/'),
        ),
    ]
