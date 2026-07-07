from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aggregator', '0002_seed_sources'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawitem',
            name='published_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='опубликовано в источнике'),
        ),
    ]
