# Generated by Django 3.2.12 on 2022-03-22 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_agent', '0002_alter_bank_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferrequest',
            name='info',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]