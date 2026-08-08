"""Migration to create the AcademyAccess authorization table."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademyAccess',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('user_id', models.CharField(max_length=36)),
                ('granted_at', models.DateTimeField(auto_now_add=True)),
                ('granted_by_id', models.CharField(blank=True, max_length=36, null=True)),
                ('note', models.CharField(blank=True, default='', max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'AcademyAccess',
            },
        ),
        migrations.AddIndex(
            model_name='academyaccess',
            index=models.Index(
                fields=['user_id', 'is_active'],
                name='academyaccess_user_active_idx',
            ),
        ),
        migrations.AddConstraint(
            model_name='academyaccess',
            constraint=models.UniqueConstraint(
                condition=models.Q(is_active=True),
                fields=['user_id'],
                name='unique_active_academy_access_per_user',
            ),
        ),
    ]