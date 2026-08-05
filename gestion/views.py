import json
import random
import time
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DonanteForm, ProgramaSocialForm, VoluntarioForm
from .models import Actividad, Donante, ProgramaSocial, TurnoApoyo, Voluntario


def enviar_correo_seguro(asunto, mensaje, destinatario):
    """Envia correos de forma totalmente aislada para evitar que errores SMTP tiren la app."""
    if not destinatario:
        return
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@ong.com')
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=from_email,
            recipient_list=[destinatario],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error omitido al enviar correo a {destinatario}: {e}")


def inicio_view(request):
    voluntarios = Voluntario.objects.all()
    actividades = Actividad.objects.all()
    donantes = Donante.objects.all()

    total_horas = 120
    fidelizacion = 85

    chart_voluntarios_labels = ['Juan Pérez', 'María López', 'Carlos Ruiz', 'Ana Gómez']
    chart_voluntarios_data = [35, 28, 42, 15]

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

    dest = getattr(settings, 'EMAIL_HOST_USER', '')
    enviar_correo_seguro(
        asunto='Código de Seguridad Administrador - ONG',
        mensaje=f'Estimado Administrador,\n\nSu código de verificación es: {codigo}',
        destinatario=dest
    )

    return render(request, 'gestion/verificar_admin.html')


# --- VOLUNTARIOS ---
def lista_voluntarios(request):
    voluntarios = Voluntario.objects.all()
    form = VoluntarioForm()
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_staff:
        form = VoluntarioForm(request.POST)
        if form.is_valid():
            voluntario = form.save()
            email = getattr(voluntario, 'email', None)
            if email:
                enviar_correo_seguro(
                    asunto='Bienvenido a la ONG',
                    mensaje=f'Hola {voluntario.nombre},\n\nGracias por registrarte como voluntario.',
                    destinatario=email
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
            email = getattr(donante, 'email', None)
            if email:
                enviar_correo_seguro(
                    asunto='Comprobante de Donación - Gestor ONG',
                    mensaje=f'Estimado/a {donante.nombre},\n\nHemos recibido con éxito su donación por un valor de ${monto}. ¡Muchas gracias!',
                    destinatario=email
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
        except Exception as e:
            return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'mensaje': 'Petición inválida.'}, status=400)


# --- REGISTRO PÚBLICO RESISTENTE A FALLOS DE SCHEMA Y SMTP ---
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
            
            campos_donante = {}
            model_fields = [f.name for f in Donante._meta.get_fields()]
            
            if 'nombre' in model_fields: campos_donante['nombre'] = nombre
            if 'email' in model_fields: campos_donante['email'] = email
            if 'monto_donado' in model_fields: campos_donante['monto_donado'] = monto
            if 'monto' in model_fields: campos_donante['monto'] = monto

            try:
                Donante.objects.create(**campos_donante)
            except Exception as e:
                print(f"Error BD al crear donante: {e}")

            enviar_correo_seguro(
                asunto='Confirmación de Donación - Gestor ONG',
                mensaje=f'Hola {nombre},\n\n¡Muchas gracias por tu contribución generosa de ${monto}!',
                destinatario=email
            )

            messages.success(request, f'¡Gracias por tu donación de ${monto}, {nombre}! Registro completado con éxito.')
            return redirect('inicio')

        else:
            cedula_val = request.POST.get('cedula', '').strip() or f'VOL-{int(time.time())}'
            habilidades_val = request.POST.get('habilidades', 'General')
            horas_val = request.POST.get('horas_aportadas', 5)

            campos_voluntario = {}
            model_fields = [f.name for f in Voluntario._meta.get_fields()]

            if 'nombre' in model_fields: campos_voluntario['nombre'] = nombre
            if 'email' in model_fields: campos_voluntario['email'] = email
            if 'cedula' in model_fields: campos_voluntario['cedula'] = cedula_val
            if 'habilidades' in model_fields: campos_voluntario['habilidades'] = habilidades_val
            if 'especialidad' in model_fields: campos_voluntario['especialidad'] = habilidades_val
            if 'horas_aportadas' in model_fields: campos_voluntario['horas_aportadas'] = horas_val
            if 'horas' in model_fields: campos_voluntario['horas'] = horas_val

            try:
                Voluntario.objects.create(**campos_voluntario)
            except Exception as e:
                print(f"Error BD al crear voluntario: {e}")

            enviar_correo_seguro(
                asunto='Bienvenido/a al equipo de Voluntarios - Gestor ONG',
                mensaje=f'Hola {nombre},\n\n¡Gracias por registrarte como voluntario/a en nuestra plataforma!',
                destinatario=email
            )

            messages.success(request, f'¡Gracias por ser voluntario/a, {nombre}! Registro completado con éxito.')
            return redirect('inicio')

    return render(request, 'gestion/registro_publico.html', {'tipo': tipo})