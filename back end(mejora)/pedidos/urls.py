from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from mainapp import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    

    path('', views.catalogo, name='catalogo'),
    
    path('producto/<slug:slug>/', views.producto_detalle, name='producto_detalle'),
    

    path('solicitar/', views.solicitar_pedido, name='solicitar_pedido'),
    path('solicitar/<int:producto_id>/', views.solicitar_pedido, name='solicitar_pedido_producto'),
    
    path('seguimiento/<uuid:token>/', views.seguimiento, name='seguimiento'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)