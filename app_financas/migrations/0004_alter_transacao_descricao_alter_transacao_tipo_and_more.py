# Generated by Django 5.0.7 on 2024-08-04 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_financas', '0003_alter_transacao_descricao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transacao',
            name='descricao',
            field=models.CharField(default='Sem descrição', max_length=200),
        ),
        migrations.AlterField(
            model_name='transacao',
            name='tipo',
            field=models.CharField(choices=[('entrada', 'Entrada'), ('saida', 'Saída')], default='saida', max_length=7),
        ),
        migrations.AlterOrderWithRespectTo(
            name='transacao',
            order_with_respect_to='categoria',
        ),
    ]
