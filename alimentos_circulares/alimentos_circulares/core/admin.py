from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Comercio, Categoria, Producto, Publicacion, Reserva, Entrega, Reporte
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets=UserAdmin.fieldsets + (('Alimentos Circulares',{'fields':('nombre','rol')}),)
    list_display=('username','email','nombre','rol','is_active')
for model in [Comercio,Categoria,Producto,Publicacion,Reserva,Entrega,Reporte]: admin.site.register(model)
