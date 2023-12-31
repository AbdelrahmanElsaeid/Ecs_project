# Generated by Django 4.2.4 on 2023-11-24 14:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0001_initial"),
        ("checklists", "0001_initial"),
        ("documents", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="checklist",
            name="pdf_document",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="checklist",
                to="documents.document",
            ),
        ),
        migrations.AddField(
            model_name="checklist",
            name="submission",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="checklists",
                to="core.submission",
            ),
        ),
        migrations.AddField(
            model_name="checklist",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterUniqueTogether(
            name="checklistquestion",
            unique_together={("blueprint", "number")},
        ),
        migrations.AlterUniqueTogether(
            name="checklist",
            unique_together={("blueprint", "submission", "user")},
        ),
    ]
