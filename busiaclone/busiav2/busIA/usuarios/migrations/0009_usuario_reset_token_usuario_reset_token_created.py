# Generated by Django 5.0 on 2025-01-29 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0008_alter_usuario_codigo_recuperacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='reset_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='reset_token_created',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
