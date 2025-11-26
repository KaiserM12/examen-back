# mainapp/forms.py
from django import forms
from .models import Pedido, ImagenReferencia # Asegúrate de que este import existe

# II.9. Formulario de Solicitud de Pedido
class SolicitudPedidoForm(forms.ModelForm):
    descripcion_solicitada = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        label="Describe tu artículo personalizado y los detalles de impresión/diseño"
    )
    
    # *** ESTA LÍNEA DEBE SER forms.FileInput ***
    imagenes_referencia = forms.FileField(
        widget=forms.FileInput(attrs={'multiple': True, 'class': 'form-control'}), 
        required=False,
        label="Sube tus imágenes de referencia (Máximo 3)"
    )
    
    class Meta:
        model = Pedido
        # ... (el resto del código de Meta)