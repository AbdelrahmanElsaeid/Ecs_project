# Generated by Django 4.2.4 on 2023-12-04 19:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("votes", "0001_initial"),
        ("core", "0003_alter_submission_current_submission_form"),
    ]

    operations = [
        migrations.AlterField(
            model_name="investigator",
            name="submission_form",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="investigators",
                to="core.submissionform",
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="current_pending_vote",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="_currently_pending_for",
                to="votes.vote",
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="current_published_vote",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="_currently_published_for",
                to="votes.vote",
            ),
        ),
        migrations.AlterField(
            model_name="submissionform",
            name="primary_investigator",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.investigator",
            ),
        ),
    ]
