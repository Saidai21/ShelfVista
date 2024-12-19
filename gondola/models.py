from django.db import models

class Usuario(models.Model):
    nombre_usuario = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_usuario

class Local(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    nombre_producto = models.CharField(max_length=255)
    cantidad_comprado = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre_producto} - {self.local.nombre}"

class Stock(models.Model):
    nombre_producto = models.CharField(max_length=255)
    stock_bodega = models.IntegerField()
    local = models.ForeignKey(Local, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre_producto} - {self.local.nombre}"

class ResultadoDivisibilidad(models.Model):
    producto = models.CharField(max_length=255)
    stock_sala = models.IntegerField()
    local = models.ForeignKey(Local, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.producto} - {self.local.nombre}"
