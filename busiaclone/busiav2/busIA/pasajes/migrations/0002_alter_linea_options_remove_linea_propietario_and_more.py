# Generated by Django 5.0 on 2025-01-29 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pasajes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='linea',
            options={'ordering': ['nombre_empresa', 'nombre'], 'verbose_name': 'Línea', 'verbose_name_plural': 'Líneas'},
        ),
        migrations.RemoveField(
            model_name='linea',
            name='propietario',
        ),
        migrations.AddField(
            model_name='linea',
            name='nombre_empresa',
            field=models.CharField(default='Sin Empresa', max_length=100),
            preserve_default=False,
        ),
    ]
