# Generated by Django 2.2.19 on 2021-03-19 15:20

from django.db import migrations, models
import django.db.models.deletion
import django_lifecycle.mixins
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0061_call_handle_artifact_checksums_command'),
    ]

    operations = [
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('pulp_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('pulp_created', models.DateTimeField(auto_now_add=True)),
                ('pulp_last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('pulp_type', models.TextField(db_index=True, default=None)),
                ('name', models.TextField(db_index=True, unique=True)),
                ('base_path', models.TextField(unique=True)),
                ('content_guard', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.ContentGuard')),
                ('publication', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Publication')),
                ('remote', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Remote')),
                ('repository', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Repository', related_name='distributions')),
                ('repository_version', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.RepositoryVersion')),
            ],
            options={
                'abstract': False,
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
        ),
    ]
