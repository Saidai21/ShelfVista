from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.iniciar_sesion, name="iniciar"),
    path("home/", views.index, name="index"),
    path("analisis/", views.analisis_productos, name="analisis"),
    path('mantenedor-gondolas/', views.mantenedor_gondolas, name='mantenedor_gondolas'),
    path('ventas/', views.ventas, name='ventas'),
    path("reporte/pdf/", views.generar_reporte, name="generar_reporte"),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
