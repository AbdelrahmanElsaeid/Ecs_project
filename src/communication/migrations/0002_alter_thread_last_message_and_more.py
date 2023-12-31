# Generated by Django 4.2.4 on 2023-12-04 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("communication", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="thread",
            name="last_message",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="head",
                to="communication.message",
            ),
        ),
        migrations.AlterField(
            model_name="thread",
            name="related_thread",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="communication.thread",
            ),
        ),
    ]
