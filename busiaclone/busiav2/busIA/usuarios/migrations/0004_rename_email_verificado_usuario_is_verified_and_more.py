# Generated by Django 5.0 on 2025-01-28 15:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_usuario_telefono'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usuario',
            old_name='email_verificado',
            new_name='is_verified',
        ),
        migrations.AlterField(
            model_name='usuario',
            name='nombre',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='telefono',
            field=models.CharField(blank=True, help_text='Formato: +56912345678', max_length=15, null=True, validators=[django.core.validators.RegexValidator(message="El número debe estar en formato: '+999999999'. Mínimo 9 y máximo 15 dígitos.", regex='^\\+?1?\\d{9,15}$')]),
        ),
    ]
