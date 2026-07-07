from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_customuser_status_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='discord_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
