from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Producto, Cliente, Compra, Marca
from .forms import ProductoForm, CompraForm, LoginForm, SignInForm, FormBuscarProducto
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum

#Create your views here.
# welcome(request):
# Descripción: Esta vista simplemente renderiza la página de bienvenida de la tienda.
# Acciones:
#  - Renderiza el template 'tienda/index.html'.
def welcome(request):
    return render(request, 'tienda/index.html', {})

# compra(request):
# Descripción: Muestra una lista de productos disponibles para la compra.
# Acciones:
#  - Filtra todos los productos disponibles.
#  - Renderiza el template 'tienda/compra.html' con la lista de productos.
def compra(request):
    productos= Producto.objects.all()
    form = FormBuscarProducto(request.GET)

    if form.is_valid():
        texto_busqueda = form.cleaned_data['texto']
        marcas_seleccionadas = form.cleaned_data['marca']

        productos = productos.filter(nombre__contains=texto_busqueda)

        if len(marcas_seleccionadas) != 0:
            productos = productos.filter(marca_id__in=marcas_seleccionadas)
    return render(request,'tienda/compra.html', {'productos':productos, 'form': form})

# listar_productos(request):
# Descripción: Lista todos los productos en el sistema (requiere inicio de sesión y permisos de personal).
# Acciones:
#  - Obtiene todos los productos desde la base de datos.
#  - Renderiza el template 'tienda/admin/listado_productos.html' con la lista de productos.
@login_required(login_url='/tienda/registro/login/')
@staff_member_required
def listar_productos(request):
    productos = Producto.objects.all()
    form = FormBuscarProducto(request.GET)

    if form.is_valid():
        texto_busqueda = form.cleaned_data['texto']
        marcas_seleccionadas = form.cleaned_data['marca']

        productos = productos.filter(nombre__contains=texto_busqueda)

        if len(marcas_seleccionadas) != 0:
            productos = productos.filter(marca_id__in=marcas_seleccionadas)

    return render(request, 'tienda/admin/listado_productos.html', {'productos': productos, 'form': form})

# nuevo_producto(request):
# Descripción: Permite a un administrador agregar un nuevo producto al sistema (requiere inicio de sesión y permisos de personal).
# Acciones:
# - Si la solicitud es un POST y el formulario es válido, guarda el nuevo producto y redirige a la lista de productos.
# - Si la solicitud es GET, muestra un formulario para agregar un nuevo producto.
@login_required(login_url='/tienda/registro/login/')
@staff_member_required
def nuevo_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'tienda/admin/nuevo_producto.html', {'form': form})

# editar_producto(request, pk):
# Descripción: Permite a un administrador editar un producto existente (requiere inicio de sesión y permisos de personal).
# Acciones:
#  - Si la solicitud es un POST y el formulario es válido, guarda los cambios y redirige a la lista de productos.
#  - Si la solicitud es GET, muestra un formulario prellenado con la información del producto.
@login_required(login_url='/tienda/registro/login/')
@staff_member_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'tienda/admin/editar_producto.html', {'form': form, 'producto': producto})

# eliminar_producto(request, pk):
# Descripción: Permite a un administrador eliminar un producto existente (requiere inicio de sesión y permisos de personal).
# Acciones:
#  - Si la solicitud es un POST, elimina el producto y redirige a la lista de productos.
#  - Si la solicitud es GET, muestra una confirmación para eliminar el producto.
@login_required(login_url='/tienda/registro/login/')
@staff_member_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        return redirect('listar_productos')
    return render(request, 'tienda/admin/eliminar_producto.html', {'producto': producto})

# checkout(request, pk):
# Descripción: Procesa el checkout de un producto seleccionado (requiere inicio de sesión).
# Acciones:
#  - Si la solicitud es un POST y el formulario es válido, realiza el proceso de compra y ajusta el inventario y el saldo del cliente.
@transaction.atomic
@login_required(login_url='/tienda/registro/login/')
def checkout(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    cliente = get_object_or_404(Cliente, user=request.user)
    if request.method == "POST":
        form = CompraForm(request.POST)
        if form.is_valid():
            unidades = form.cleaned_data['unidades']
            if unidades <= producto.unidades:
                producto.unidades -= unidades
                producto.save()
                compra = Compra()
                compra.producto = producto
                compra.user = cliente
                compra.unidades = unidades
                compra.importe = unidades*producto.precio
                compra.fecha = timezone.now()
                compra.save()
                cliente.saldo -= compra.importe
                cliente.save()
                return redirect('welcome')
    form = CompraForm()
    return render(request, 'tienda/checkout.html', {'form': form, 'producto': producto})

# mi_login(request):
# Descripción: Muestra el formulario de inicio de sesión y maneja el proceso de inicio de sesión.
# Acciones:
#  - Si la solicitud es un POST y el formulario es válido, autentica al usuario y lo redirige a la página de inicio.
#  - Si el usuario no existe, muestra un mensaje de error.
def mi_login(request):
    form = LoginForm()
    return_render = render(request, 'tienda/registro/login.html', {'form': form})
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            next_ruta = request.GET.get('next')
            if next_ruta is None:
                next_ruta = '/tienda'
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return_render = redirect(next_ruta)
            else:
                messages.info(request, 'usuario no existe')

    return return_render

# log_out(request):
# Descripción: Cierra la sesión del usuario y lo redirige a la página de bienvenida.
def log_out(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)

# sign_in(request):
# Descripción: Permite a un nuevo usuario registrarse en la tienda.
# Acciones:
#  - Si la solicitud es un POST y el formulario es válido, crea un nuevo usuario y lo registra.
def sign_in(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            cliente = Cliente(user=user, saldo=0, vip=False)
            cliente.save()
            login(request, user)
            return redirect('welcome')
    else:
        form = SignInForm()

    return render(request, 'tienda/registro/login.html', {'form': form})

# productos_por_marca(request):
# Descripción: Muestra productos filtrados por marca (requiere inicio de sesión y permisos de personal).
# Acciones:
#  - Obtiene todos los productos y marcas desde la base de datos.
#  - Renderiza el template 'tienda/productos_por_marca.html' con la lista de productos y marcas.
@login_required(login_url='/tienda/registro/login/')
@staff_member_required
def productos_por_marca(request):
    producto = Producto.objects.all()
    marcas = Producto.objects.all()
    return render(request, 'tienda/productos_por_marca.html', {'productos': producto, 'marcas': marcas})

# top_ten_productos_vendidos(request):
# Descripción: Muestra los diez productos más vendidos (requiere inicio de sesión y permisos de personal).
# Acciones:
#  - Obtiene los productos ordenados por la cantidad de compras y limita la lista a los primeros diez.
#  - Renderiza el template 'tienda/top_ten_productos_vendidos.html' con la lista de productos.
@login_required(login_url='/tienda/registro/login/')
@staff_member_required
def top_ten_productos_vendidos(request):
    productos_top_ten = Producto.objects.annotate(purchase_count=Count('compra')).order_by('-purchase_count')[:10]
    return render(request, 'tienda/top_ten_productos_vendidos.html', {'productos_top_ten': productos_top_ten})

# compras_usuario(request):
# Descripción: Muestra las compras realizadas por el usuario (requiere inicio de sesión).
# Acciones:
#  - Obtiene el cliente asociado al usuario y las compras asociadas a ese cliente.
#  - Renderiza el template 'tienda/compras_usuario.html' con la lista de compras.
@login_required(login_url='/tienda/registro/login/')
def compras_usuario(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    compras = Compra.objects.all().filter(producto__compra__user_id=cliente)
    return render(request, 'tienda/compras_usuario.html', {'compras': compras})

# top_ten_mejores_clientes(request):
# Descripción: Muestra los diez mejores clientes basados en el dinero gastado (requiere inicio de sesión y permisos de personal).
# Acciones:
#  - Obtiene los clientes ordenados por la cantidad total de dinero gastado y limita la lista a los primeros diez.
#  - Renderiza el template 'tienda/top_ten_mejores_clientes.html' con la lista de clientes.
@login_required(login_url='/tienda/registro/login/')
@staff_member_required
def top_ten_mejores_clientes(request):
    mejores_clientes = Cliente.objects.annotate(dinero_gastado=Sum('compra__importe')).order_by('-dinero_gastado')[:10]
    return render(request, 'tienda/top_ten_mejores_clientes.html', {'mejores_clientes': mejores_clientes})
