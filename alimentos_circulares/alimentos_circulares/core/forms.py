from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, Comercio, Producto, Publicacion, Categoria, Reporte
class RegistroForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')
    nombre = forms.CharField(label='Nombre completo', max_length=100)
    rol = forms.ChoiceField(label='Quiero participar como', choices=[('usuario','Persona de la comunidad'),('comercio','Comercio local')])
    class Meta: model = Usuario; fields = ('nombre','username','email','rol','password1','password2')
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        labels={'username':'Nombre de usuario','password1':'Contraseña','password2':'Confirmar contraseña'}
        for k,v in labels.items(): self.fields[k].label=v
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario o correo')
class ComercioForm(forms.ModelForm):
    class Meta: model=Comercio; fields=['nombre','direccion','horario','contacto']; labels={'nombre':'Nombre del comercio','direccion':'Dirección de retiro','horario':'Horario de retiro','contacto':'Teléfono o contacto'}
class PublicacionForm(forms.Form):
    nombre=forms.CharField(max_length=120,label='Nombre del alimento')
    categoria=forms.ModelChoiceField(queryset=Categoria.objects.all(),label='Categoría')
    descripcion=forms.CharField(widget=forms.Textarea(attrs={'rows':3}),label='Descripción',required=False)
    conservacion=forms.CharField(widget=forms.Textarea(attrs={'rows':2}),label='Conservación',required=False)
    modalidad=forms.ChoiceField(choices=Publicacion.MODALIDADES,label='Modalidad')
    precio=forms.DecimalField(min_value=0,decimal_places=2,max_digits=10,label='Precio (CLP)',required=False,initial=0)
    cantidad=forms.IntegerField(min_value=1,label='Unidades disponibles')
    fecha_limite=forms.DateTimeField(label='Fecha y hora límite de retiro',widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
class ReporteForm(forms.ModelForm):
    class Meta: model=Reporte; fields=['motivo']; labels={'motivo':'Motivo del reporte'}
