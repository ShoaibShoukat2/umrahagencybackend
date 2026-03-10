# Generated migration for LiveAudioSession model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_customer_city_customer_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveAudioSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(help_text='Agora channel name', max_length=200, unique=True)),
                ('title', models.CharField(default='Live Audio from Tour Leader', max_length=300)),
                ('tour_leader_email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('active', 'Active'), ('ended', 'Ended'), ('cancelled', 'Cancelled')], default='active', max_length=20)),
                ('listener_count', models.IntegerField(default=0, help_text='Number of customers who joined')),
                ('started_at', models.DateTimeField()),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='live_sessions', to='api.package')),
            ],
            options={
                'verbose_name': 'Live Audio Session',
                'verbose_name_plural': 'Live Audio Sessions',
                'ordering': ['-started_at'],
            },
        ),
    ]
