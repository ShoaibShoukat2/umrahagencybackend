from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_liveaudiosession'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ]
