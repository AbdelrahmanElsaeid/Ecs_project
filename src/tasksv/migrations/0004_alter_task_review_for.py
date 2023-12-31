# Generated by Django 4.2.4 on 2023-12-04 20:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tasksv", "0003_alter_task_managers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="review_for",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="tasksv.task",
            ),
        ),
    ]
