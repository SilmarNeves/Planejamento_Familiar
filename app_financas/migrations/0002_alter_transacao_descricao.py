# Generated by Django 5.0.7 on 2024-08-03 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_financas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transacao',
            name='descricao',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
