# Generated by Django 3.1.3 on 2020-11-22 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20201121_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalaccount',
            name='organization_title',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Название организации'),
        ),
    ]
