# Generated by Django 4.2.4 on 2023-12-16 12:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0002_alter_meeting_options_alter_meeting_table_and_more"),
        ("votes", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vote",
            name="top",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="vote",
                to="meetings.timetableentry",
            ),
        ),
        migrations.AlterField(
            model_name="vote",
            name="upgrade_for",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="previous",
                to="votes.vote",
            ),
        ),
    ]
