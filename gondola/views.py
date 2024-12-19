from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import *
from django.db.models import Sum, F
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Local, Stock, Venta, ResultadoDivisibilidad
from collections import OrderedDict


def index(request):
    return render(request, "index.html")

def iniciar_sesion(request):

    nombre_usuario = None

    if request.method == "POST":
        correo = request.POST.get("email")
        contrasena = request.POST.get("contrasena")

        try:
            # Buscar el usuario en la base de datos
            usuario = Usuario.objects.get(email=correo)

            # Comprobar si la contraseña coincide
            if check_password(contrasena, usuario.contrasena):
                request.session["usuario_id"] = usuario.id
                request.session["nombre_usuario"] = usuario.nombre_usuario
                return redirect("index")
            else:
                error_message = "Contraseña incorrecta."
        except Usuario.DoesNotExist:
            error_message = "El correo electrónico no está registrado."

        return render(request, "iniciar.html", {"error_message": error_message})

    context = {
        "nombre_usuario": nombre_usuario,
    }
    return render(request, "iniciar.html", context)

def analisis_productos(request):
    ventas = (
        Venta.objects.values('nombre_producto', 'local__nombre')
        .annotate(
            cantidad=Sum('cantidad_comprado'),  # Aquí usamos Sum correctamente
            ganancias=Sum(F('total'))  # Usamos F() para acceder al campo 'total'
        )
        .order_by('nombre_producto', 'local__nombre')
    )

    # Estructurar datos para la tabla y el gráfico
    productos = {}
    for venta in ventas:
        producto = venta['nombre_producto']
        local = venta['local__nombre']
        if producto not in productos:
            productos[producto] = {}
        productos[producto][local] = {
            'cantidad': venta['cantidad'],
            'ganancias': venta['ganancias']
        }

    # Datos para el gráfico
    productos_nombres = list(productos.keys())
    locales_nombres = list({local for prod in productos.values() for local in prod.keys()})
    datos_grafico = [
        {
            'name': local,
            'data': [productos[producto].get(local, {}).get('cantidad', 0) for producto in productos_nombres]
        }
        for local in locales_nombres
    ]

    return render(request, 'analisis.html', {
        'productos': productos,
        'datos_grafico': datos_grafico,
        'productos_nombres': productos_nombres
    })

def mantenedor_gondolas(request):
    # Obtener todos los locales
    locales = Local.objects.all()
    
    # Diccionario para almacenar los datos que se pasarán al template
    gondolas = {}

    # Orden predefinido de los productos
    productos_orden = ["Chocolates", "Chicles", "Caramelos", "Bebidas Pequeñas", "Snacks"]

    for local in locales:
        # Obtener el stock en sala (resultado de divisibilidad)
        resultados_divisibilidad = ResultadoDivisibilidad.objects.filter(local=local)
        stock_sala = {r.producto: r.stock_sala for r in resultados_divisibilidad}

        # Obtener productos vendidos
        ventas = Venta.objects.filter(local=local).values('nombre_producto').annotate(
            cantidad_vendida=Sum('cantidad_comprado')
        )
        productos_vendidos = {v['nombre_producto']: v['cantidad_vendida'] for v in ventas}

        # Obtener el stock en bodega
        stock_bodega = Stock.objects.filter(local=local)
        stock_bodega_dict = {s.nombre_producto: s.stock_bodega for s in stock_bodega}

        # Ordenar los diccionarios según el orden predefinido
        stock_sala = OrderedDict(
            sorted(stock_sala.items(), key=lambda x: productos_orden.index(x[0]))
        )
        productos_vendidos = OrderedDict(
            sorted(productos_vendidos.items(), key=lambda x: productos_orden.index(x[0]))
        )
        stock_bodega_dict = OrderedDict(
            sorted(stock_bodega_dict.items(), key=lambda x: productos_orden.index(x[0]))
        )

        # Agregar datos al diccionario
        gondolas[local.nombre] = {
            'resultados_divisibilidad': stock_sala,
            'productos': productos_vendidos,
            'stock': stock_bodega_dict
        }

    # Renderizar el template con los datos
    return render(request, 'mantenedor_gondolas.html', {'gondolas': gondolas})

def ventas(request):
    # Obtener las ventas agrupadas por producto
    ventas = (
        Venta.objects.values('nombre_producto')
        .annotate(
            cantidad=Sum('cantidad_comprado'),  # Sumar la cantidad comprada por producto
            ganancias=Sum(F('total'))  # Calcular las ganancias totales por producto
        )
        .order_by('nombre_producto')  # Ordenar por nombre del producto
    )

    # Estructurar los datos para el template
    productos = {
        venta['nombre_producto']: {
            'cantidad': venta['cantidad'],
            'ganancias': venta['ganancias']
        }
        for venta in ventas
    }

    # Datos para el gráfico
    nombres_productos = [venta['nombre_producto'] for venta in ventas]
    cantidades = [venta['cantidad'] for venta in ventas]
    ganancias = [float(venta['ganancias']) for venta in ventas]  # Convertir a float para evitar problemas en el gráfico

    # Renderizar el template con los datos
    return render(request, 'ventas.html', {
        'productos': productos,
        'nombres_productos': nombres_productos,
        'cantidades': cantidades,
        'ganancias': ganancias,
    })

def generar_reporte(request):
    # Inicializar datos
    gondolas = {}

    # Obtener datos de ventas
    ventas = Venta.objects.select_related('local')
    for venta in ventas:
        local_nombre = venta.local.nombre
        producto = venta.nombre_producto
        cantidad = venta.cantidad_comprado

        if local_nombre not in gondolas:
            gondolas[local_nombre] = {
                "productos": {},
                "stock": {},
                "resultados_divisibilidad": {},
            }

        gondolas[local_nombre]["productos"][producto] = (
            gondolas[local_nombre]["productos"].get(producto, 0) + cantidad
        )

    # Obtener datos de stock
    stock_items = Stock.objects.select_related('local')
    for stock in stock_items:
        local_nombre = stock.local.nombre
        producto = stock.nombre_producto
        stock_bodega = stock.stock_bodega

        if local_nombre not in gondolas:
            gondolas[local_nombre] = {
                "productos": {},
                "stock": {},
                "resultados_divisibilidad": {},
            }

        gondolas[local_nombre]["stock"][producto] = stock_bodega

    # Obtener datos de resultados de divisibilidad
    resultados = ResultadoDivisibilidad.objects.select_related('local')
    for resultado in resultados:
        local_nombre = resultado.local.nombre
        producto = resultado.producto
        stock_sala = resultado.stock_sala

        if local_nombre not in gondolas:
            gondolas[local_nombre] = {
                "productos": {},
                "stock": {},
                "resultados_divisibilidad": {},
            }

        gondolas[local_nombre]["resultados_divisibilidad"][producto] = stock_sala

    # Calcular resultados de divisibilidad
    for local in gondolas:
        for producto in gondolas[local]["resultados_divisibilidad"]:
            ventas = gondolas[local]["productos"].get(producto, 0)
            resultado = gondolas[local]["resultados_divisibilidad"][producto] - ventas
            gondolas[local]["resultados_divisibilidad"][producto] = max(0, resultado)

        for producto in gondolas[local]["stock"]:
            if producto not in gondolas[local]["productos"]:
                gondolas[local]["productos"][producto] = 0

    # Ordenar productos
    for local in gondolas:
        gondolas[local]["productos"] = dict(
            sorted(gondolas[local]["productos"].items())
        )
        gondolas[local]["stock"] = dict(sorted(gondolas[local]["stock"].items()))
        gondolas[local]["resultados_divisibilidad"] = dict(
            sorted(gondolas[local]["resultados_divisibilidad"].items())
        )

    # Generar el PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="reporte_gondolas.pdf"'

    # Crear objeto Canvas
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Agregar datos al PDF, cada góndola en una nueva página
    for local, datos in gondolas.items():
        p.drawString(100, height - 100, f"Reporte de Góndola: {local}")
        y_position = height - 120  # Inicializa la posición Y para el contenido

        # Productos
        p.drawString(100, y_position, "Productos:")
        y_position -= 10

        for producto, cantidad in datos["productos"].items():
            p.drawString(120, y_position, f"{producto}: {cantidad}")
            y_position -= 15

        # Stock en Bodega
        p.drawString(100, y_position, "Stock en Bodega:")
        y_position -= 10

        for producto, cantidad in datos["stock"].items():
            p.drawString(120, y_position, f"{producto}: {cantidad}")
            y_position -= 15

        # Stock en Sala
        p.drawString(100, y_position, "Resultados de Stock en Sala:")
        y_position -= 10

        for producto, cantidad in datos["resultados_divisibilidad"].items():
            p.drawString(120, y_position, f"{producto}: {cantidad}")
            y_position -= 15

        # Agregar una nueva página para la siguiente góndola
        p.showPage()

    p.save()

    return response