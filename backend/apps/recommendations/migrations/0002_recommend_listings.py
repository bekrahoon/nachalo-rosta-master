import django.db.models.deletion
from django.db import migrations, models


def clear_recommendations(apps, schema_editor):
    EventRecommendation = apps.get_model('recommendations', 'EventRecommendation')
    EventRecommendation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('aggregator', '0005_more_telegram_sources'),
        ('recommendations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(clear_recommendations, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='eventrecommendation',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='eventrecommendation',
            name='event',
        ),
        migrations.AddField(
            model_name='eventrecommendation',
            name='listing',
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recommendations',
                to='aggregator.listing',
                verbose_name='объявление',
            ),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='eventrecommendation',
            unique_together={('user', 'listing')},
        ),
        migrations.AlterModelOptions(
            name='eventrecommendation',
            options={
                'ordering': ['-match_score', '-created_at'],
                'verbose_name': 'рекомендация объявления',
                'verbose_name_plural': 'рекомендации объявлений',
            },
        ),
    ]
