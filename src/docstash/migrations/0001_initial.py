# Generated by Django 4.2.4 on 2023-11-24 18:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields.json
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocStash",
            fields=[
                (
                    "key",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("group", models.CharField(db_index=True, max_length=120, null=True)),
                ("current_version", models.IntegerField(default=-1)),
                ("modtime", models.DateTimeField(auto_now=True)),
                ("name", models.TextField(blank=True, null=True)),
                ("value", django_extensions.db.fields.json.JSONField(default=dict)),
                ("object_id", models.PositiveIntegerField(null=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("group", "owner", "content_type", "object_id")},
            },
        ),
    ]