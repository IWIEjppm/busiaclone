# Generated by Django 5.0 on 2025-01-28 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0005_usuario_email_verificado'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='foto_perfil',
            field=models.ImageField(blank=True, null=True, upload_to='usuarios/fotos_perfil/'),
        ),
    ]
