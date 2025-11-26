from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from mainapp import views 

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # II.7. Catálogo (Home del sitio público)
    path('', views.catalogo, name='catalogo'),
    
    # II.8. Detalle del Producto (usando slug)
    path('producto/<slug:slug>/', views.producto_detalle, name='producto_detalle'),
    
    # II.9. Formulario de Solicitud 
    path('solicitar/', views.solicitar_pedido, name='solicitar_pedido'),
    path('solicitar/<int:producto_id>/', views.solicitar_pedido, name='solicitar_pedido_producto'),
    
    # II.10. Seguimiento del Pedido (usando el token UUID)
    path('seguimiento/<uuid:token>/', views.seguimiento, name='seguimiento'),
]

# Manejo de archivos MEDIA (IMAGENES)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)