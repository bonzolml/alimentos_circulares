from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import Usuario, Comercio, Categoria, Producto, Publicacion, Reserva, Entrega, Reporte
from .forms import RegistroForm, LoginForm, ComercioForm, PublicacionForm, ReporteForm

def catalogo(request):
    qs=Publicacion.objects.select_related('producto','producto__categoria','producto__comercio').filter(estado='activa',fecha_limite_retiro__gt=timezone.now(),cantidad_disponible__gt=0)
    q=request.GET.get('q','').strip(); categoria=request.GET.get('categoria',''); modalidad=request.GET.get('modalidad','')
    if q: qs=qs.filter(Q(producto__nombre__icontains=q)|Q(producto__descripcion__icontains=q)|Q(producto__comercio__nombre__icontains=q)|Q(producto__comercio__direccion__icontains=q))
    if categoria: qs=qs.filter(producto__categoria_id=categoria)
    if modalidad: qs=qs.filter(modalidad=modalidad)
    return render(request,'core/catalogo.html',{'publicaciones':qs.order_by('fecha_limite_retiro'),'categorias':Categoria.objects.all(),'q':q,'categoria':categoria,'modalidad':modalidad})

def registro(request):
    if request.user.is_authenticated: return redirect('dashboard')
    form=RegistroForm(request.POST or None)
    if form.is_valid():
        user=form.save(commit=False); user.nombre=form.cleaned_data['nombre']; user.email=form.cleaned_data['email']; user.rol=form.cleaned_data['rol']; user.save()
        if user.rol=='comercio': request.session['crear_comercio_usuario']=user.pk; login(request,user); return redirect('dashboard')
        login(request,user); messages.success(request,'¡Tu cuenta ya está lista! Bienvenido/a a Alimentos Circulares.'); return redirect('catalogo')
    return render(request,'core/formulario.html',{'form':form,'titulo':'Crea tu cuenta','subtitulo':'Únete a una comunidad que aprovecha mejor los alimentos.','boton':'Crear cuenta'})

def ingresar(request):
    if request.user.is_authenticated: return redirect('dashboard')
    form=LoginForm(request, data=request.POST or None)
    if form.is_valid(): login(request,form.get_user()); messages.success(request,'Sesión iniciada correctamente.'); return redirect('dashboard')
    return render(request,'core/formulario.html',{'form':form,'titulo':'Qué bueno verte de nuevo','subtitulo':'Ingresa para gestionar tus publicaciones o reservas.','boton':'Ingresar'})

def salir(request):
    logout(request); messages.info(request,'Has cerrado tu sesión.'); return redirect('catalogo')

@login_required
def dashboard(request):
    if request.user.rol=='comercio':
        comercio=getattr(request.user,'comercio',None)
        if not comercio:
            form=ComercioForm(request.POST or None)
            if form.is_valid(): c=form.save(commit=False); c.usuario=request.user; c.save(); messages.success(request,'Perfil del comercio creado. Ya puedes publicar alimentos.'); return redirect('dashboard')
            return render(request,'core/formulario.html',{'form':form,'titulo':'Configura tu comercio','subtitulo':'Estos datos ayudarán a las personas a retirar sus reservas.','boton':'Guardar comercio'})
        publicaciones=Publicacion.objects.filter(producto__comercio=comercio).select_related('producto').order_by('-fecha_publicacion')
        reservas=Reserva.objects.filter(publicacion__producto__comercio=comercio).select_related('publicacion__producto','usuario').order_by('-fecha_reserva')
        return render(request,'core/dashboard_comercio.html',{'comercio':comercio,'publicaciones':publicaciones,'reservas':reservas,'activas':publicaciones.filter(estado='activa').count(),'pendientes':reservas.filter(estado='pendiente').count(),'entregas':reservas.filter(estado='retirada').count()})
    if request.user.rol=='administrador' or request.user.is_superuser:
        return render(request,'core/dashboard_admin.html',{'usuarios':Usuario.objects.count(),'publicaciones':Publicacion.objects.count(),'reportes':Reporte.objects.select_related('usuario','publicacion__producto').order_by('-fecha_reporte'),'reservas':Reserva.objects.count()})
    return render(request,'core/dashboard_usuario.html',{'reservas':Reserva.objects.filter(usuario=request.user).select_related('publicacion__producto__comercio').order_by('-fecha_reserva')})

@login_required
def nueva_publicacion(request):
    if request.user.rol!='comercio': return HttpResponseForbidden('Solo las cuentas de comercio pueden publicar alimentos.')
    comercio=getattr(request.user,'comercio',None)
    if not comercio: return redirect('dashboard')
    form=PublicacionForm(request.POST or None)
    if form.is_valid():
        d=form.cleaned_data
        if d['fecha_limite'] <= timezone.now(): form.add_error('fecha_limite','La fecha de retiro debe estar en el futuro.')
        elif d['modalidad']=='pronto_consumo' and (d['precio'] is None or d['precio']<=0): form.add_error('precio','Indica un precio mayor que cero para productos a precio reducido.')
        else:
            with transaction.atomic():
                producto=Producto.objects.create(comercio=comercio,categoria=d['categoria'],nombre=d['nombre'],descripcion=d['descripcion'],condiciones_conservacion=d['conservacion'])
                Publicacion.objects.create(producto=producto,modalidad=d['modalidad'],precio=(d['precio'] or 0) if d['modalidad']=='pronto_consumo' else 0,cantidad_inicial=d['cantidad'],cantidad_disponible=d['cantidad'],fecha_limite_retiro=d['fecha_limite'])
            messages.success(request,'¡Alimento publicado! Ya aparece en el catálogo.'); return redirect('dashboard')
    return render(request,'core/formulario.html',{'form':form,'titulo':'Publica un alimento','subtitulo':'Comparte excedentes aptos para el consumo con tu comunidad.','boton':'Publicar alimento'})

def detalle_publicacion(request,pk):
    p=get_object_or_404(Publicacion.objects.select_related('producto__comercio','producto__categoria'),pk=pk)
    return render(request,'core/detalle.html',{'p':p,'reporte_form':ReporteForm()})

@login_required
def reservar(request,pk):
    if request.user.rol!='usuario': return HttpResponseForbidden('Solo las cuentas de la comunidad pueden reservar.')
    if request.method!='POST': return redirect('detalle_publicacion',pk=pk)
    try: cantidad=int(request.POST.get('cantidad','1'))
    except ValueError: cantidad=0
    with transaction.atomic():
        p=Publicacion.objects.select_for_update().select_related('producto').filter(pk=pk).first()
        if not p or not p.vigente: messages.error(request,'Esta publicación ya no está disponible.'); return redirect('catalogo')
        if cantidad<1 or cantidad>p.cantidad_disponible: messages.error(request,'La cantidad solicitada no es válida o supera las unidades disponibles.'); return redirect('detalle_publicacion',pk=pk)
        p.cantidad_disponible-=cantidad
        if p.cantidad_disponible==0: p.estado='cerrada'
        p.save(update_fields=['cantidad_disponible','estado'])
        Reserva.objects.create(publicacion=p,usuario=request.user,cantidad=cantidad)
    messages.success(request,'Reserva realizada. Coordina el retiro con el comercio.'); return redirect('mis_reservas')

@login_required
def mis_reservas(request):
    if request.user.rol=='comercio': return redirect('dashboard')
    return render(request,'core/dashboard_usuario.html',{'reservas':Reserva.objects.filter(usuario=request.user).select_related('publicacion__producto__comercio').order_by('-fecha_reserva')})

@login_required
def estado_reserva(request,pk,estado):
    r=get_object_or_404(Reserva.objects.select_related('publicacion__producto__comercio'),pk=pk)
    if request.user.rol!='comercio' or r.publicacion.producto.comercio.usuario_id!=request.user.id: return HttpResponseForbidden('No tienes permiso para modificar esta reserva.')
    if estado not in ['confirmada','rechazada']: return HttpResponseForbidden('Estado no válido.')
    with transaction.atomic():
        r=Reserva.objects.select_for_update().get(pk=pk)
        if r.estado!='pendiente': messages.error(request,'Solo puedes responder reservas pendientes.')
        else:
            r.estado=estado; r.save(update_fields=['estado'])
            if estado=='rechazada':
                p=Publicacion.objects.select_for_update().get(pk=r.publicacion_id); p.cantidad_disponible+=r.cantidad
                if p.fecha_limite_retiro>timezone.now(): p.estado='activa'
                p.save(update_fields=['cantidad_disponible','estado'])
            else: Entrega.objects.get_or_create(reserva=r,defaults={'estado':'pendiente'})
            messages.success(request,'Reserva actualizada.')
    return redirect('dashboard')

@login_required
def registrar_entrega(request,pk):
    r=get_object_or_404(Reserva.objects.select_related('publicacion__producto__comercio'),pk=pk)
    if request.user.rol!='comercio' or r.publicacion.producto.comercio.usuario_id!=request.user.id: return HttpResponseForbidden('No tienes permiso para registrar esta entrega.')
    if r.estado!='confirmada': messages.error(request,'Solo las reservas confirmadas pueden marcarse como retiradas.')
    else:
        r.estado='retirada'; r.save(update_fields=['estado']); Entrega.objects.update_or_create(reserva=r,defaults={'estado':'entregada','fecha_entrega':timezone.now()}); messages.success(request,'Entrega registrada correctamente.')
    return redirect('dashboard')

@login_required
def reportar(request,pk):
    p=get_object_or_404(Publicacion,pk=pk); form=ReporteForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        rep=form.save(commit=False); rep.usuario=request.user; rep.publicacion=p; rep.save(); messages.success(request,'Gracias. El reporte fue enviado para revisión.'); return redirect('detalle_publicacion',pk=pk)
    return render(request,'core/formulario.html',{'form':form,'titulo':'Reportar publicación','subtitulo':'Cuéntanos por qué esta publicación requiere revisión.','boton':'Enviar reporte'})
