from django.db import migrations, models
import json


def convert_itinerary_to_json(apps, schema_editor):
    """Convert existing text itinerary to JSON array"""
    Package = apps.get_model('api', 'Package')
    for package in Package.objects.all():
        if package.itinerary and package.itinerary.strip():
            # Has text content — wrap in JSON array with single day
            package.itinerary = json.dumps([{
                'day': 1,
                'title': 'Itinerary',
                'description': package.itinerary
            }])
        else:
            # Empty or None — set to empty JSON array
            package.itinerary = '[]'
        package.save(update_fields=['itinerary'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_alter_image_fields_to_imagefield'),
    ]

    operations = [
        # Step 1: Convert existing TextField data to JSON-formatted strings
        migrations.RunPython(convert_itinerary_to_json, migrations.RunPython.noop),
        
        # Step 2: Change field type from TextField to JSONField
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
