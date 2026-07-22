from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_customer_expo_push_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='featured_image',
            field=models.ImageField(blank=True, null=True, upload_to='packages/'),
        ),
        migrations.AlterField(
            model_name='package',
            name='hotel_image',
            field=models.ImageField(blank=True, null=True, upload_to='hotels/', help_text='Hotel image'),
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='categories/'),
        ),
        migrations.AlterField(
            model_name='travelitem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='items/'),
        ),
        migrations.AlterField(
            model_name='packageimage',
            name='image',
            field=models.ImageField(upload_to='package_gallery/', max_length=500),
        ),
    ]
