from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_blogpost'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='package',
            options={'ordering': ['travel_date', 'created_at']},
        ),
    ]
