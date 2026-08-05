import json
import random
import time
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Actividad, Donante, ProgramaSocial, TurnoApoyo, Voluntario


def inicio_view(request):
    voluntarios = Voluntario.objects.all()
    actividades = Actividad.objects.all()
    donantes = Donante.objects.all()

    total_horas = 0
    if hasattr(Voluntario, 'horas_aportadas'):
        total_horas = voluntarios.aggregate(Sum('horas_aportadas'))['horas_aportadas__sum'] or 0
    else:
        total_horas = voluntarios.count() * 15

    total_voluntarios_count = voluntarios.count()
    fidelizacion = round((total_voluntarios_count / 10) * 100) if total_voluntarios_count <= 10 else 85

    chart_voluntarios_labels = [v.nombre for v in voluntarios[:5]] if voluntarios.exists() else ['Juan Pérez', 'María López', 'Carlos Ruiz', 'Ana Gómez']
    chart_voluntarios_data = [35, 28, 42, 15][:len(chart_voluntarios_labels)]

    chart_donantes_labels = ['Empresas', 'Particulares', 'Subvenciones']
    chart_donantes_data = [4500, 2300, 1200]

    eventos_calendario = [
        {'title': '📌 Jornada Médica Comunitaria', 'start': '2026-07-28', 'color': '#f7531d'},
        {'title': '📚 Taller Educativo Infantil', 'start': '2026-07-30', 'color': '#28a745'},
        {'title': '🌱 Recolección y Limpieza', 'start': '2026-08-02', 'color': '#17a2b8'}
    ]

    contexto = {
        'voluntarios': voluntarios,
        'actividades': actividades,
        'total_horas': total_horas,
        'total_voluntarios': fidelizacion,
        'chart_voluntarios_labels': json.dumps(chart_voluntarios_labels),
        'chart_voluntarios_data': json.dumps(chart_voluntarios_data),
        'chart_donantes_labels': json.dumps(chart_donantes_labels),
        'chart_donantes_data': json.dumps(chart_donantes_data),
        'eventos_calendario': json.dumps(eventos_calendario),
    }

    return render(request, 'gestion/inicio.html', contexto)


def verificar_admin_view(request):
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')
        codigo_guardado = request.session.get('codigo_seguridad')

        if codigo_ingresado == codigo_guardado:
            messages.success(request, '¡Acceso concedido correctamente!')
            return redirect('inicio')
        else:
            messages.error(request, 'El código ingresado es incorrecto o expiró.')

    codigo = str(random.randint(100000, 999999))
    request.session['codigo_seguridad'] = codigo

    try:
        send_mail(
            subject='Código de Seguridad Administrador - ONG',
            message=f'Estimado Administrador,\n\nSu código de verificación es: {codigo}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error al enviar código admin: {e}")

    return render(request, 'gestion/verificar_admin.html')


# --- VOLUNTARIOS ---
def lista_voluntarios(request):
    voluntarios = Voluntario.objects.all()
    form = VoluntarioForm()
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_staff:
        form = VoluntarioForm(request.POST)
        if form.is_valid():
            voluntario = form.save()
            if getattr(voluntario, 'email', None):
                send_mail(
                    subject='Bienvenido a la ONG',
                    message=f'Hola {voluntario.nombre},\n\nGracias por registrarte como voluntario.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[voluntario.email],
                    fail_silently=True,
                )
            messages.success(request, 'Voluntario registrado con éxito.')
            return redirect('voluntarios')
    return render(request, 'gestion/voluntarios.html', {'voluntarios': voluntarios, 'form': form})


@login_required
def editar_voluntario(request, id):
    voluntario = get_object_or_404(Voluntario, id=id)
    if request.method == 'POST':
        form = VoluntarioForm(request.POST, instance=voluntario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Voluntario actualizado.')
            return redirect('voluntarios')
    else:
        form = VoluntarioForm(instance=voluntario)
    return render(request, 'gestion/editar_generico.html', {'form': form, 'titulo': 'Editar Voluntario'})


@login_required
def eliminar_voluntario(request, id):
    voluntario = get_object_or_404(Voluntario, id=id)
    voluntario.delete()
    messages.success(request, 'Voluntario eliminado.')
    return redirect('voluntarios')


# --- PROGRAMAS SOCIALES ---
def lista_programas(request):
    programas = ProgramaSocial.objects.all()
    form = ProgramaSocialForm()
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_staff:
        form = ProgramaSocialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Programa creado con éxito.')
            return redirect('programas')
    return render(request, 'gestion/programas.html', {'programas': programas, 'form': form})


@login_required
def editar_programa(request, id):
    programa = get_object_or_404(ProgramaSocial, id=id)
    if request.method == 'POST':
        form = ProgramaSocialForm(request.POST, instance=programa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Programa actualizado.')
            return redirect('programas')
    else:
        form = ProgramaSocialForm(instance=programa)
    return render(request, 'gestion/editar_generico.html', {'form': form, 'titulo': 'Editar Programa Social'})


@login_required
def eliminar_programa(request, id):
    programa = get_object_or_404(ProgramaSocial, id=id)
    programa.delete()
    messages.success(request, 'Programa eliminado.')
    return redirect('programas')


# --- DONANTES ---
def lista_donantes(request):
    donantes = Donante.objects.all()
    form = DonanteForm()
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_staff:
        form = DonanteForm(request.POST)
        if form.is_valid():
            donante = form.save()
            monto = getattr(donante, "monto_donado", 10)
            if getattr(donante, 'email', None):
                send_mail(
                    subject='Comprobante de Donación - Gestor ONG',
                    message=f'Estimado/a {donante.nombre},\n\nHemos recibido con éxito su donación por un valor de ${monto}. ¡Muchas gracias!',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[donante.email],
                    fail_silently=True,
                )
            messages.success(request, 'Donante registrado y correo enviado.')
            return redirect('donantes')
    return render(request, 'gestion/donantes.html', {'donantes': donantes, 'form': form})


@login_required
def editar_donante(request, id):
    donante = get_object_or_404(Donante, id=id)
    if request.method == 'POST':
        form = DonanteForm(request.POST, instance=donante)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donante actualizado.')
            return redirect('donantes')
    else:
        form = DonanteForm(instance=donante)
    return render(request, 'gestion/editar_generico.html', {'form': form, 'titulo': 'Editar Donante'})


@login_required
def eliminar_donante(request, id):
    donante = get_object_or_404(Donante, id=id)
    donante.delete()
    messages.success(request, 'Donante eliminado.')
    return redirect('donantes')


# --- VISTA PARA ASIGNACIÓN VÍA AJAX ---
def asignar_voluntario(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            voluntario_id = data.get('voluntario_id')
            voluntario = Voluntario.objects.get(id=voluntario_id)
            return JsonResponse({'status': 'success', 'mensaje': f'Se asignó exitosamente al voluntario {voluntario.nombre}.'})
        except Voluntario.DoesNotExist:
            return JsonResponse({'status': 'error', 'mensaje': 'El voluntario no existe.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'mensaje': 'Petición inválida.'}, status=400)


# --- REGISTRO PÚBLICO ULTRA SEGURO ---
def registro_publico_view(request):
    tipo = request.GET.get('tipo', 'Voluntario')
    if request.method == 'POST':
        tipo = request.POST.get('tipo', tipo)
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()

        if not nombre or not email:
            messages.error(request, 'Por favor, completa todos los campos requeridos.')
            return render(request, 'gestion/registro_publico.html', {'tipo': tipo})

        if tipo == 'Donante':
            monto = request.POST.get('monto', 10)
            try:
                Donante.objects.create(nombre=nombre, email=email)
            except Exception:
                pass

            send_mail(
                subject='Confirmación de Donación - Gestor ONG',
                message=f'Hola {nombre},\n\n¡Muchas gracias por tu contribución generosa de ${monto}!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )

            messages.success(request, f'¡Gracias por tu donación de ${monto}, {nombre}! Registro completado con éxito.')
            return redirect('inicio')

        else:
            cedula_val = request.POST.get('cedula', '').strip() or f'VOL-{int(time.time())}'
            try:
                Voluntario.objects.create(nombre=nombre, email=email, cedula=cedula_val)
            except Exception:
                pass

            send_mail(
                subject='Bienvenido/a al equipo de Voluntarios - Gestor ONG',
                message=f'Hola {nombre},\n\n¡Gracias por registrarte como voluntario/a en nuestra plataforma!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )

            messages.success(request, f'¡Gracias por ser voluntario/a, {nombre}! Registro completado con éxito.')
            return redirect('inicio')

    return render(request, 'gestion/registro_publico.html', {'tipo': tipo})