from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from .models import Producto, Categoria, Pedido, ImagenReferencia # Importamos los modelos


def catalogo(request):
    categorias = Categoria.objects.all()
    productos_list = Producto.objects.all()
    
    categoria_slug = request.GET.get('categoria')
    query = request.GET.get('q')

    if categoria_slug:
        productos_list = productos_list.filter(categoria__slug=categoria_slug)

    if query:
        productos_list = productos_list.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        ).distinct()

    productos_destacados = Producto.objects.filter(destacado=True)

    context = {
        'productos': productos_list,
        'categorias': categorias,
        'query': query,
        'productos_destacados': productos_destacados
    }
    return render(request, 'catalogo.html', context)


def producto_detalle(request, slug):
    producto = get_object_or_404(Producto, slug=slug)
    imagenes = producto.imagenes.all() 
    
    context = {
        'producto': producto,
        'imagenes': imagenes,
    }
    return render(request, 'producto_detalle.html', context)



def solicitar_pedido(request, producto_id=None):
    producto = None
    if producto_id:
        producto = get_object_or_404(Producto, pk=producto_id)

    if request.method == 'POST':
        nombre_cliente = request.POST.get('nombre_cliente')
        descripcion = request.POST.get('descripcion_solicitada')

        if not nombre_cliente or not descripcion:
            messages.error(request, "El nombre del cliente y la descripción son campos obligatorios.")
            return redirect(request.path_info) 

        try:
            producto_ref_id = request.POST.get('producto_referencia')
            producto_ref = None
            if producto_ref_id:
                producto_ref = Producto.objects.get(pk=producto_ref_id)
            

            elif producto_id:
                producto_ref = producto


            nuevo_pedido = Pedido.objects.create(
                nombre_cliente=nombre_cliente,
                email_cliente=request.POST.get('email_cliente'),
                telefono_cliente=request.POST.get('telefono_cliente'),
                red_social_cliente=request.POST.get('red_social_cliente'),
                descripcion_solicitada=descripcion,
                fecha_necesidad=request.POST.get('fecha_necesidad'),
                producto_referencia=producto_ref,
                

                estado='SOLICITADO',
                estado_pago='PENDIENTE',
                plataforma_origen='SITIO_WEB' 
            )


            imagenes = request.FILES.getlist('imagenes_referencia') 
            
            if imagenes:
                count = 0
                for img in imagenes:
                    # Limita a 3 imágenes
                    if count < 3:
                        ImagenReferencia.objects.create(pedido=nuevo_pedido, imagen=img)
                        count += 1


            seguimiento_url = reverse('seguimiento', args=[str(nuevo_pedido.token_seguimiento)])
            messages.success(request, f"¡Tu solicitud ha sido enviada! Usa este enlace para seguir el estado de tu pedido: http://127.0.0.1:8000{seguimiento_url}")
            return redirect('seguimiento', token=nuevo_pedido.token_seguimiento)
        
        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar el pedido: {e}")
            return redirect(request.path_info)


    context = {
        'producto': producto,
    }
    return render(request, 'formulario_solicitud.html', context)



def seguimiento(request, token):
    try:
        pedido = Pedido.objects.get(token_seguimiento=token)
        
        context = {
            'pedido': pedido,
            'imagenes_referencia': pedido.imagenes_referencia.all(),
        }
        return render(request, 'seguimiento.html', context)
    except Pedido.DoesNotExist:
        context = {
            'error_message': 'El código de seguimiento no es válido.'
        }
        return render(request, 'seguimiento.html', context, status=404)