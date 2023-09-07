# Generated by Django 4.2.4 on 2023-09-06 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0002_menuitem_inventory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='quantity',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateField(auto_now=True, db_index=True),
        ),
    ]
