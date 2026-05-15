from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_alter_package_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='expo_push_token',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
    ]
