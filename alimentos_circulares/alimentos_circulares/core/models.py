from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

class Usuario(AbstractUser):
    ROLES = [('usuario','Usuario'),('comercio','Comercio'),('administrador','Administrador')]
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')
    nombre = models.CharField(max_length=100, blank=True)
    REQUIRED_FIELDS = ['email']
    def __str__(self): return self.nombre or self.username

class Comercio(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comercio')
    nombre = models.CharField(max_length=120)
    direccion = models.CharField(max_length=200)
    horario = models.CharField(max_length=150, blank=True)
    contacto = models.CharField(max_length=40, blank=True)
    def __str__(self): return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.CharField(max_length=250, blank=True)
    def __str__(self): return self.nombre

class Producto(models.Model):
    comercio = models.ForeignKey(Comercio, on_delete=models.CASCADE, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    condiciones_conservacion = models.TextField(blank=True)
    def __str__(self): return self.nombre

class Publicacion(models.Model):
    MODALIDADES = [('donacion','Donación'),('pronto_consumo','Precio reducido')]
    ESTADOS = [('activa','Activa'),('pausada','Pausada'),('cerrada','Cerrada')]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='publicaciones')
    modalidad = models.CharField(max_length=20, choices=MODALIDADES)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_inicial = models.PositiveIntegerField()
    cantidad_disponible = models.PositiveIntegerField()
    fecha_limite_retiro = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activa')
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    @property
    def vigente(self): return self.estado == 'activa' and self.fecha_limite_retiro > timezone.now() and self.cantidad_disponible > 0
    def __str__(self): return self.producto.nombre

class Reserva(models.Model):
    ESTADOS = [('pendiente','Pendiente'),('confirmada','Confirmada'),('rechazada','Rechazada'),('retirada','Retirada'),('cancelada','Cancelada')]
    publicacion = models.ForeignKey(Publicacion, on_delete=models.PROTECT, related_name='reservas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reservas')
    cantidad = models.PositiveIntegerField()
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

class Entrega(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='entrega')
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, default='pendiente')
    observacion = models.CharField(max_length=250, blank=True)

class Reporte(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reportes')
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='reportes')
    motivo = models.CharField(max_length=250)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='pendiente')
