from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_alter_package_itinerary'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('slug', models.SlugField(max_length=300, unique=True)),
                ('category', models.CharField(
                    choices=[
                        ('umrah-tips', 'Umrah Tips'),
                        ('packing-guide', 'Packing Guide'),
                        ('visa-updates', 'Visa Updates'),
                        ('dua-guide', 'Dua Guide'),
                        ('news', 'News & Announcements'),
                        ('travel-guide', 'Travel Guide'),
                        ('hajj-tips', 'Hajj Tips'),
                    ],
                    default='news',
                    max_length=30,
                )),
                ('excerpt', models.CharField(blank=True, help_text='Short summary shown on listing page', max_length=500)),
                ('content', models.TextField(help_text='Full article content (HTML or plain text supported)')),
                ('featured_image', models.ImageField(blank=True, null=True, upload_to='blog/')),
                ('author_name', models.CharField(default='TM Fouzy Travel & Tours', max_length=200)),
                ('is_published', models.BooleanField(default=False)),
                ('is_featured', models.BooleanField(default=False, help_text='Show on landing page')),
                ('views_count', models.IntegerField(default=0)),
                ('read_time_minutes', models.IntegerField(default=5, help_text='Estimated reading time in minutes')),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags e.g. umrah,2026,singapore', max_length=300)),
                ('meta_description', models.CharField(blank=True, help_text='SEO meta description (max 160 chars)', max_length=160)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Blog Post',
                'verbose_name_plural': 'Blog Posts',
                'ordering': ['-published_at', '-created_at'],
            },
        ),
    ]
