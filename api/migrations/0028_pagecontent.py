from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_package_order_by_travel_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('title', models.CharField(max_length=120)),
                ('content', models.JSONField(blank=True, default=dict)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Page content',
                'verbose_name_plural': 'Page content',
            },
        ),
    ]
