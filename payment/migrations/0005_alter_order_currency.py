# Generated by Django 4.1.3 on 2022-11-26 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_remove_discount_item_remove_item_order_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='currency',
            field=models.CharField(default='usd', max_length=3),
        ),
    ]
