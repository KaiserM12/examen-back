from django.db import models
from django.utils.text import slugify
import uuid
from decimal import Decimal


ESTADO_PEDIDO = (
    ('SOLICITADO', 'Solicitado'),
    ('APROBADO', 'Aprobado'),
    ('EN_PROCESO', 'En Proceso'),
    ('REALIZADA', 'Realizada'),
    ('ENTREGADA', 'Entregada'),
    ('FINALIZADA', 'Finalizada'),
    ('CANCELADA', 'Cancelada'),
)


ESTADO_PAGO = (
    ('PENDIENTE', 'Pendiente'),
    ('PARCIAL', 'Parcial'),
    ('PAGADO', 'Pagado'),
)


PLATAFORMA_ORIGEN = (
    ('FACEBOOK', 'Facebook'),
    ('INSTAGRAM', 'Instagram'),
    ('WHATSAPP', 'WhatsApp'),
    ('PRESENCIAL', 'Presencial'),
    ('SITIO_WEB', 'Sitio Web'),
    ('OTRO', 'Otro'),
)


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Categorías"


# I.1. Productos
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    destacado = models.BooleanField(default=False) 

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre



class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos_imagenes')

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"
    
    class Meta:
        verbose_name_plural = "Imágenes de Producto"



class Insumo(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    cantidad_disponible = models.IntegerField(default=0)
    unidad = models.CharField(max_length=20, blank=True, null=True)
    marca = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.cantidad_disponible} {self.unidad})"



class Pedido(models.Model):
    nombre_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField(blank=True, null=True)
    telefono_cliente = models.CharField(max_length=50, blank=True, null=True)
    red_social_cliente = models.CharField(max_length=100, blank=True, null=True)

    producto_referencia = models.ForeignKey(
        Producto, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        help_text="Producto del catálogo usado como base si aplica."
    )
    descripcion_solicitada = models.TextField()
    fecha_necesidad = models.DateField(blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_PEDIDO, default='SOLICITADO')
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO, default='PENDIENTE')
    plataforma_origen = models.CharField(max_length=20, choices=PLATAFORMA_ORIGEN, default='SITIO_WEB') 


    token_seguimiento = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 

    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    monto_abonado = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Pedido {self.token_seguimiento.hex[:8]} - {self.nombre_cliente}"



class ImagenReferencia(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='imagenes_referencia', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='referencias_clientes')

    def __str__(self):
        return f"Referencia para Pedido {self.pedido.id}"
    
    class Meta:
        verbose_name_plural = "Imágenes de Referencia"