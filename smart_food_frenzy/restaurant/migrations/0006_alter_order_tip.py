# Generated by Django 5.1.1 on 2024-10-12 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0005_alter_orderitem_modified_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='tip',
            field=models.FloatField(default=0.0, help_text='Tip amount'),
        ),
    ]
