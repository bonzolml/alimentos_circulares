from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from core.models import Comercio,Categoria,Producto,Publicacion
class Command(BaseCommand):
    help='Carga categorías y publicaciones de demostración.'
    def handle(self,*args,**kwargs):
        U=get_user_model()
        cats={n:Categoria.objects.get_or_create(nombre=n)[0] for n in ['Frutas y verduras','Panadería','Lácteos','Despensa']}
        user,_=U.objects.get_or_create(username='comercio_demo',defaults={'email':'comercio@example.com','nombre':'Comercio Demo','rol':'comercio'})
        if not user.has_usable_password(): user.set_password('Demo12345!'); user.save()
        if not hasattr(user,'comercio'): c=Comercio.objects.create(usuario=user,nombre='Almacén La Esquina',direccion='Av. Principal 123, Copiapó',horario='Lun–Sáb, 10:00–18:00',contacto='+56 9 1234 5678')
        else: c=user.comercio
        rows=[('Caja de manzanas','Frutas y verduras','Fruta fresca, ideal para consumo inmediato.','donacion',0,8),('Pan del día','Panadería','Pan fresco del día anterior, conservar en lugar seco.','pronto_consumo',800,12),('Yogur natural','Lácteos','Mantener refrigerado. Revisar fecha y envase al retirar.','pronto_consumo',500,6),('Legumbres surtidas','Despensa','Paquetes cerrados en buen estado.','donacion',0,10)]
        for name,cat,desc,mode,price,qty in rows:
            product,created=Producto.objects.get_or_create(comercio=c,nombre=name,defaults={'categoria':cats[cat],'descripcion':desc,'condiciones_conservacion':'Retirar dentro del horario indicado.'})
            if created or not product.publicaciones.exists(): Publicacion.objects.create(producto=product,modalidad=mode,precio=price,cantidad_inicial=qty,cantidad_disponible=qty,fecha_limite_retiro=timezone.now()+timedelta(days=2))
        self.stdout.write(self.style.SUCCESS('Datos demo cargados. Usuario comercio: comercio_demo / Demo12345!'))
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from core.models import Comercio,Categoria,Producto,Publicacion
class Command(BaseCommand):
    help='Carga categorías y publicaciones de demostración.'
    def handle(self,*args,**kwargs):
        U=get_user_model()
        cats={n:Categoria.objects.get_or_create(nombre=n)[0] for n in ['Frutas y verduras','Panadería','Lácteos','Despensa']}
        user,_=U.objects.get_or_create(username='alfredo',defaults={'email':'comercio@example.com','nombre':'Comercio Demo','rol':'comercio'})
        if not user.has_usable_password(): user.set_password('12345'); user.save()
        if not hasattr(user,'comercio'): c=Comercio.objects.create(usuario=user,nombre='Almacén La Esquina',direccion='Av. Principal 123, Copiapó',horario='Lun–Sáb, 10:00–18:00',contacto='+56 9 1234 5678')
        else: c=user.comercio
        rows=[('Caja de manzanas','Frutas y verduras','Fruta fresca, ideal para consumo inmediato.','donacion',0,8),('Pan del día','Panadería','Pan fresco del día anterior, conservar en lugar seco.','pronto_consumo',800,12),('Yogur natural','Lácteos','Mantener refrigerado. Revisar fecha y envase al retirar.','pronto_consumo',500,6),('Legumbres surtidas','Despensa','Paquetes cerrados en buen estado.','donacion',0,10)]
        for name,cat,desc,mode,price,qty in rows:
            product,created=Producto.objects.get_or_create(comercio=c,nombre=name,defaults={'categoria':cats[cat],'descripcion':desc,'condiciones_conservacion':'Retirar dentro del horario indicado.'})
            if created or not product.publicaciones.exists(): Publicacion.objects.create(producto=product,modalidad=mode,precio=price,cantidad_inicial=qty,cantidad_disponible=qty,fecha_limite_retiro=timezone.now()+timedelta(days=2))
        self.stdout.write(self.style.SUCCESS('Datos demo cargados. Usuario comercio: comercio_demo / Demo12345!'))
