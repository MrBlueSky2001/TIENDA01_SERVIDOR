from django.urls import path
from . import views

urlpatterns = [
    # Página de bienvenida
    path('', views.welcome, name='welcome'),

    # Redirección a la página de bienvenida
    path('tienda/', views.welcome, name='welcome'),

    # Lista de productos disponibles para compra
    path('tienda/compra/', views.compra, name='compra'),

    # Gestión de productos (requiere inicio de sesión y permisos de personal)
    path('tienda/admin/productos/', views.listar_productos, name='listar_productos'),
    path('tienda/admin/productos/edicion/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('tienda/admin/productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('tienda/admin/productos/nuevo/', views.nuevo_producto, name='nuevo_producto'),

    # Registro y inicio de sesión
    path('tienda/registro/signin', views.sign_in, name='signin'),
    path('tienda/registro/login', views.mi_login, name='mi_login'),
    path('tienda/logout/', views.log_out, name='logout'),

    # Proceso de checkout para un producto seleccionado
    path('tienda/checkout/<int:pk>/', views.checkout, name='checkout'),

    # Informes y estadísticas
    path('tienda/informes/productos_por_marca/', views.productos_por_marca, name='productos_por_marca'),
    path('tienda/informes/top_ten_productos_vendidos/', views.top_ten_productos_vendidos, name='top_ten_productos_vendidos'),
    path('tienda/informes/compras_usuario/', views.compras_usuario, name='compras_usuario'),
    path('tienda/informes/top_ten_mejores_clientes/', views.top_ten_mejores_clientes, name='top_ten_mejores_clientes'),
]
