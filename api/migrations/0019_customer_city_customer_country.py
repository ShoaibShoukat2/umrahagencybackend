# Generated migration to add city and country fields to Customer model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_customerdocument'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='customer',
            name='country',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
