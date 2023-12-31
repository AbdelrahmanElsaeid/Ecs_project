# Generated by Django 4.2.4 on 2023-11-24 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ChecklistBillingState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "billed_at",
                    models.DateTimeField(
                        blank=True, db_index=True, default=None, null=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ChecklistPayment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Price",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "category",
                    models.SmallIntegerField(
                        choices=[
                            (1, "All studies except multicentre drug studies"),
                            (
                                2,
                                "Multicentre drug trials for controlling ethics committees",
                            ),
                            (
                                3,
                                "Multicentre drug trials for locally responsible ethics committees",
                            ),
                            (4, "fee exemption"),
                            (5, "External Reviewer"),
                        ],
                        db_index=True,
                        unique=True,
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
    ]
