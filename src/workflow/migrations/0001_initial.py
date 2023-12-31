# Generated by Django 4.2.4 on 2023-11-24 14:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Edge",
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
                ("deadline", models.BooleanField(default=False)),
                ("negated", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Node",
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
                ("name", models.CharField(blank=True, max_length=100)),
                ("data_id", models.PositiveIntegerField(null=True)),
                ("is_start_node", models.BooleanField(default=False)),
                ("is_end_node", models.BooleanField(default=False)),
                ("uid", models.CharField(db_index=True, max_length=100, null=True)),
                (
                    "data_ct",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="NodeType",
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
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "category",
                    models.PositiveIntegerField(
                        choices=[(1, "activity"), (2, "control"), (3, "subgraph")],
                        db_index=True,
                    ),
                ),
                ("implementation", models.CharField(max_length=200)),
                (
                    "content_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workflow_node_types",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "data_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Token",
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
                ("deadline", models.DateTimeField(null=True)),
                ("locked", models.BooleanField(default=False)),
                ("repeated", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "consumed_at",
                    models.DateTimeField(blank=True, default=None, null=True),
                ),
                (
                    "consumed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "node",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tokens",
                        to="workflow.node",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sent_tokens",
                        to="workflow.node",
                    ),
                ),
                (
                    "trail",
                    models.ManyToManyField(related_name="future", to="workflow.token"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Graph",
            fields=[
                (
                    "nodetype_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="workflow.nodetype",
                    ),
                ),
                ("auto_start", models.BooleanField(default=False)),
            ],
            bases=("workflow.nodetype",),
        ),
        migrations.CreateModel(
            name="Workflow",
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
                ("data_id", models.PositiveIntegerField()),
                ("is_finished", models.BooleanField(default=False)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="parent_workflow",
                        to="workflow.token",
                    ),
                ),
                (
                    "graph",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workflows",
                        to="workflow.graph",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="token",
            name="workflow",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tokens",
                to="workflow.workflow",
            ),
        ),
        migrations.AddField(
            model_name="node",
            name="node_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="workflow.nodetype"
            ),
        ),
        migrations.AddField(
            model_name="node",
            name="outputs",
            field=models.ManyToManyField(
                related_name="inputs", through="workflow.Edge", to="workflow.node"
            ),
        ),
        migrations.CreateModel(
            name="Guard",
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
                ("name", models.CharField(max_length=100)),
                ("implementation", models.CharField(max_length=200)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="edge",
            name="from_node",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="edges",
                to="workflow.node",
            ),
        ),
        migrations.AddField(
            model_name="edge",
            name="guard",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="nodes",
                to="workflow.guard",
            ),
        ),
        migrations.AddField(
            model_name="edge",
            name="to_node",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="incoming_edges",
                to="workflow.node",
            ),
        ),
        migrations.AddField(
            model_name="node",
            name="graph",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="nodes",
                to="workflow.graph",
            ),
        ),
        migrations.AddConstraint(
            model_name="guard",
            constraint=models.UniqueConstraint(
                fields=("content_type", "implementation"),
                name="unique_content_type_implementation",
            ),
        ),
    ]
