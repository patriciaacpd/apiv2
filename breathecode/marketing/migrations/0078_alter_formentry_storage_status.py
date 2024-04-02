# Generated by Django 5.0.1 on 2024-03-18 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0077_course_cohort'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formentry',
            name='storage_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('PERSISTED', 'Persisted'),
                                            ('REJECTED', 'Rejected'), ('DUPLICATED', 'Duplicated'), ('ERROR', 'Error')],
                                   default='PENDING',
                                   max_length=15),
        ),
    ]
