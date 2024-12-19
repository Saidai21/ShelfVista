# Generated by Django 5.1.2 on 2024-12-19 03:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Local",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Usuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre_usuario", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("contrasena", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="ResultadoDivisibilidad",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("producto", models.CharField(max_length=255)),
                ("stock_sala", models.IntegerField()),
                (
                    "local",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="gondola.local"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Stock",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre_producto", models.CharField(max_length=255)),
                ("stock_bodega", models.IntegerField()),
                (
                    "local",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="gondola.local"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Venta",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre_producto", models.CharField(max_length=255)),
                ("cantidad_comprado", models.IntegerField()),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "local",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="gondola.local"
                    ),
                ),
            ],
        ),
    ]
