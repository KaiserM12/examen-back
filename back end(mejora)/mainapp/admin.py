from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import (
    Categoria, Producto, ProductoImagen, Insumo, 
    Pedido, ImagenReferencia
)


class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1
    max_num = 3 
    fields = ('imagen', 'imagen_preview',)
    readonly_fields = ('imagen_preview',)

    def imagen_preview(self, obj):
        """Muestra la vista previa de la imagen."""
        if obj.imagen:
            return format_html('<img src="{}" width="100" height="auto" />', obj.imagen.url)
        return 'Sin imagen'
    imagen_preview.short_description = 'Vista Previa'


class ImagenReferenciaInline(admin.TabularInline):
    model = ImagenReferencia
    extra = 0
    fields = ('imagen', 'imagen_preview',)
    readonly_fields = ('imagen_preview',)

    def imagen_preview(self, obj):
        """Muestra la vista previa de la imagen de referencia."""
        if obj.imagen:
            return format_html('<img src="{}" width="100" height="auto" />', obj.imagen.url)
        return 'Sin imagen'
    imagen_preview.short_description = 'Vista Previa Cliente'


# --- ADMINS ---

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):

    list_display = ('nombre', 'categoria', 'precio_base', 'destacado', 'mostrar_primera_imagen')
    list_filter = ('categoria', 'destacado')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ProductoImagenInline]

    def mostrar_primera_imagen(self, obj):
        """Muestra la primera imagen asociada al producto."""
        imagen = obj.imagenes.first()
        if imagen:
            return format_html('<img src="{}" width="50" height="auto" />', imagen.imagen.url)
        return 'Sin imagen'
    mostrar_primera_imagen.short_description = 'Imagen'



@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'cantidad_disponible', 'unidad', 'marca', 'color')
    list_filter = ('tipo', 'marca', 'color')
    search_fields = ('nombre', 'tipo')
    actions = ['actualizar_stock'] 

    @admin.action(description='Aumentar stock en 10 unidades')
    def actualizar_stock(self, request, queryset):
        """Implementa la funcionalidad extra de aumentar el stock."""
        for insumo in queryset:
            insumo.cantidad_disponible += 10
            insumo.save()
        self.message_user(request, f"Se aumentó el stock de {queryset.count()} insumos en 10 unidades cada uno.")



@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'nombre_cliente', 'plataforma_origen', 
        'estado', 'estado_pago', 'monto_total', 'url_seguimiento_admin'
    )
    list_filter = ('estado', 'estado_pago', 'plataforma_origen', 'fecha_creacion')
    search_fields = ('nombre_cliente', 'token_seguimiento', 'descripcion_solicitada')
    date_hierarchy = 'fecha_creacion'
    inlines = [ImagenReferenciaInline]
    
    readonly_fields = ('fecha_creacion', 'token_seguimiento', 'url_seguimiento_admin', 'estado_pago_check')

    fieldsets = (
        ('Datos del Cliente', {
            'fields': ('nombre_cliente', 'email_cliente', 'telefono_cliente', 'red_social_cliente')
        }),
        ('Detalles del Pedido', {
            'fields': ('producto_referencia', 'descripcion_solicitada', 'fecha_necesidad')
        }),
        ('Control de Pago y Estado', {
            'fields': ('estado', 'estado_pago', 'monto_total', 'monto_abonado', 'estado_pago_check')
        }),
        ('Seguimiento y Origen', {
            'fields': ('plataforma_origen', 'token_seguimiento', 'url_seguimiento_admin', 'fecha_creacion')
        }),
    )


    def estado_pago_check(self, obj):
        """Muestra visualmente el estado del pago."""
        if obj.estado_pago == 'PAGADO':
            return format_html('<span style="color: green; font-weight: bold;">✔ PAGADO COMPLETO</span>')
        elif obj.estado_pago == 'PARCIAL':
            return format_html('<span style="color: orange; font-weight: bold;">⚠️ PAGO PARCIAL</span>')
        return format_html('<span style="color: red; font-weight: bold;">❌ PENDIENTE</span>')
    estado_pago_check.short_description = 'Estado de Pago Actual'



    def save_model(self, request, obj, form, change):
        if obj.estado == 'FINALIZADA' and obj.estado_pago != 'PAGADO':
            messages.error(request, 'ERROR: No se puede finalizar un pedido si el estado de pago no es "PAGADO".')
            return 
        
        super().save_model(request, obj, form, change)



    def url_seguimiento_admin(self, obj):
        """Genera la URL única para el seguimiento del cliente."""
        url_base = reverse('seguimiento', args=[str(obj.token_seguimiento)])
        full_url = f"http://127.0.0.1:8000{url_base}"
        return format_html('<a href="{}" target="_blank">{}</a>', full_url, full_url)
    url_seguimiento_admin.short_description = 'URL de Seguimiento'