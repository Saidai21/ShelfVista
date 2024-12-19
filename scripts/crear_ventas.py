from django.db.models import Sum
from gondola.models import Stock, Venta, ResultadoDivisibilidad, Local

# Lista de productos y sus múltiplos (cantidad en una caja típica)
productos = [
    {"nombre": "Chocolates", "multiplo": 24},  # Ejemplo: 24 chocolates en una caja
    {"nombre": "Chicles", "multiplo": 50},     # Ejemplo: 50 paquetes de chicles
    {"nombre": "Caramelos", "multiplo": 100},  # Ejemplo: 100 caramelos
    {"nombre": "Bebidas Pequeñas", "multiplo": 12},  # Ejemplo: 12 bebidas en un pack
    {"nombre": "Snacks", "multiplo": 20},      # Ejemplo: 20 snacks en una caja
]

# Obtener todos los locales
locales = Local.objects.all()

# Crear stock en sala para cada producto en cada local
for local in locales:
    print(f"Calculando stock en sala para {local.nombre}...")
    for producto in productos:
        # Obtener las ventas totales de este producto en el local
        ventas = Venta.objects.filter(local=local, nombre_producto=producto["nombre"]).aggregate(total_vendido=Sum('cantidad_comprado'))['total_vendido'] or 0

        # Calcular cuántas cajas se necesitan para cubrir las ventas
        multiplo = producto["multiplo"]
        cajas_necesarias = (ventas // multiplo) + 1 if ventas % multiplo > 0 else ventas // multiplo
        stock_sala = max(0, cajas_necesarias * multiplo - ventas)  # Calcular stock en sala

        # Crear o actualizar el resultado de divisibilidad
        ResultadoDivisibilidad.objects.update_or_create(
            local=local,
            producto=producto["nombre"],
            defaults={"stock_sala": stock_sala},
        )
        print(
            f"Stock en sala actualizado: {producto['nombre']} - {stock_sala} unidades en sala - Local: {local.nombre}"
        )
