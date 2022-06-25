# Generated by Django 3.2.13 on 2022-06-23 01:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0041_cohortuser_watching'),
        ('registry', '0005_auto_20220502_2210'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='academy',
            field=models.ForeignKey(default=None,
                                    null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    to='admissions.academy'),
        ),
        migrations.AddField(
            model_name='asset',
            name='published_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='status',
            field=models.CharField(choices=[('UNASSIGNED', 'Unassigned'), ('WRITING', 'Writing'),
                                            ('DRAFT', 'Draft'), ('PUBLISHED', 'Published')],
                                   default='DRAFT',
                                   help_text='Related to the publishing of the asset',
                                   max_length=20),
        ),
    ]
