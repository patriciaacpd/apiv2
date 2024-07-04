# Generated by Django 3.1.2 on 2020-10-12 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("admissions", "0011_auto_20201006_0058"),
        ("events", "0012_auto_20201012_1650"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="online_event",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("eventbrite_id", models.CharField(blank=True, max_length=30, unique=True)),
                ("eventbrite_key", models.CharField(blank=True, default=None, max_length=255, null=True)),
                ("name", models.CharField(blank=True, default=None, max_length=100, null=True)),
                (
                    "sync_status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("PERSISTED", "Persisted"), ("ERROR", "Error")],
                        default="PENDING",
                        help_text="One of: PENDING, PERSISTED or ERROR depending on how the eventbrite sync status",
                        max_length=9,
                    ),
                ),
                ("sync_desc", models.TextField(blank=True, default=None, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "academy",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="admissions.academy"
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="event",
            name="organizacion",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="events.organization"
            ),
        ),
        migrations.AlterField(
            model_name="venue",
            name="organization",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="events.organization"
            ),
        ),
        migrations.DeleteModel(
            name="Organizacion",
        ),
    ]
