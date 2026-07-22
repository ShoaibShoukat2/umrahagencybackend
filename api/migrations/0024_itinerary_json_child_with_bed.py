from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_alter_image_fields_to_imagefield'),
    ]

    operations = [
        # Change itinerary from TextField to JSONField
        migrations.AlterField(
            model_name='package',
            name='itinerary',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Day-by-day itinerary as JSON array'
            ),
        ),
        # Add child_with_bed to RoomSharingPrice choices
        migrations.AlterField(
            model_name='roomsharingprice',
            name='sharing_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('single', 'Single (1 Adult)'),
                    ('double', 'Double Sharing (2 Adults)'),
                    ('triple', 'Triple Sharing (3 Adults)'),
                    ('quad', 'Quad Sharing (4 Adults)'),
                    ('child_with_bed', 'Child With Bed'),
                    ('child_no_bed', 'Child No Bed'),
                    ('infant', 'Infant'),
                ]
            ),
        ),
    ]
