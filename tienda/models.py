from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone

# Modelo para representar Marcas de productos
class Marca(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Marcas"

# Modelo para representar Clientes
class Cliente(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vip = models.BooleanField(default=False)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.user.username}'

    class Meta:
        verbose_name_plural = "Clientes"

# Modelo para representar Productos
class Producto(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    unidades = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(limit_value=0)])
    vip = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.marca} {self.modelo}'

    class Meta:
        unique_together = ['marca', 'modelo']
        verbose_name_plural = "Productos"

# Modelo para representar Compras
class Compra(models.Model):
    producto = models.ForeignKey(Producto, models.PROTECT)
    user = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    fecha = models.DateField(default=timezone.now)
    unidades = models.PositiveIntegerField()
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    iva = models.DecimalField(max_digits=4, decimal_places=2, default=0.21)

    def __str__(self):
        return f'{self.user.username} {self.fecha}'

    class Meta:
        unique_together = ['fecha', 'producto', 'user']
        verbose_name_plural = "Compras"