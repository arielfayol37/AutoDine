# Generated by Django 5.1.1 on 2024-10-12 03:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity_in_stock', models.IntegerField(help_text='Quantity available in stock')),
            ],
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('description', models.TextField()),
                ('num_left', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('tip', models.DecimalField(decimal_places=2, default=0.0, help_text='Tip amount', max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredients', models.ManyToManyField(to='restaurant.ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='MenuItemIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_required', models.IntegerField(help_text='Amount of this ingredient needed for the item')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.ingredient')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.menuitem')),
            ],
        ),
        migrations.AddField(
            model_name='menuitem',
            name='ingredients',
            field=models.ManyToManyField(through='restaurant.MenuItemIngredient', to='restaurant.ingredient'),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_price', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('additional_ingredients', models.ManyToManyField(blank=True, related_name='added_ingredients', to='restaurant.ingredient')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.menuitem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.order')),
                ('removed_ingredients', models.ManyToManyField(blank=True, related_name='removed_ingredients', to='restaurant.ingredient')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='menu_items',
            field=models.ManyToManyField(through='restaurant.OrderItem', to='restaurant.menuitem'),
        ),
    ]
