from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_blogpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='insurance_included',
            field=models.BooleanField(default=False, help_text='Is travel insurance included in the package price?'),
        ),
        migrations.AddField(
            model_name='package',
            name='insurance_price_per_pax',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Insurance cost per passenger (0 if included in package price)',
                max_digits=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='package',
            name='insurance_provider',
            field=models.CharField(blank=True, default='', help_text='Name of the insurance provider', max_length=200),
        ),
        migrations.AddField(
            model_name='package',
            name='insurance_description',
            field=models.TextField(blank=True, default='', help_text='Details of the insurance coverage'),
        ),
    ]
