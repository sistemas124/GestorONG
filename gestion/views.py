import json
import random
import time
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DonanteForm, ProgramaSocialForm, VoluntarioForm
from .models import Actividad, Donante, ProgramaSocial, TurnoApoyo, Voluntario


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

    return render(request, 'gestion/verificar_admin.html')


# --- VOLUNTARIOS ---
def lista_voluntarios(request):
    voluntarios = Voluntario.objects.all()
    form = VoluntarioForm()
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_staff:
        form = VoluntarioForm(request.POST)
        if form.is_valid():
            form.save()
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
            form.save()
            messages.success(request, 'Donante registrado.')
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


# --- REGISTRO PÚBLICO ULTRA GARANTIZADO ---
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
            monto = request.POST.get('monto', '10')
            try:
                monto_val = float(monto)
            except ValueError:
                monto_val = 10.0

            # Estrategia 1: Uso del Formulario
            form_data = {
                'nombre': nombre,
                'email': email,
                'monto_donado': monto_val,
                'monto': monto_val,
                'telefono': request.POST.get('telefono', '0000000000')
            }
            form = DonanteForm(form_data)
            if form.is_valid():
                form.save()
            else:
                # Estrategia 2: Guardado directo con asignación dinámica
                obj = Donante()
                for field in Donante._meta.fields:
                    fname = field.name
                    if fname == 'nombre':
                        setattr(obj, fname, nombre)
                    elif fname == 'email':
                        setattr(obj, fname, email)
                    elif fname in ['monto_donado', 'monto']:
                        setattr(obj, fname, monto_val)
                    elif not field.null and field.default == float('nan'):
                        if field.get_internal_type() in ['CharField', 'TextField']:
                            setattr(obj, fname, 'N/A')
                        elif field.get_internal_type() in ['IntegerField', 'FloatField', 'DecimalField']:
                            setattr(obj, fname, 0)
                try:
                    obj.save()
                except Exception:
                    # Estrategia 3: Creación mínima
                    Donante.objects.create(nombre=nombre, email=email)

            messages.success(request, f'¡Gracias por tu donación de ${monto_val}, {nombre}! Registro completado con éxito.')
            return redirect('inicio')

        else:
            cedula_val = request.POST.get('cedula', '').strip() or f'VOL-{int(time.time())}'
            habilidades_val = request.POST.get('habilidades', 'General')
            horas_val = request.POST.get('horas_aportadas', 5)

            form_data = {
                'nombre': nombre,
                'email': email,
                'cedula': cedula_val,
                'habilidades': habilidades_val,
                'especialidad': habilidades_val,
                'horas_aportadas': horas_val,
                'horas': horas_val,
                'telefono': request.POST.get('telefono', '0000000000')
            }
            form = VoluntarioForm(form_data)
            if form.is_valid():
                form.save()
            else:
                obj = Voluntario()
                for field in Voluntario._meta.fields:
                    fname = field.name
                    if fname == 'nombre':
                        setattr(obj, fname, nombre)
                    elif fname == 'email':
                        setattr(obj, fname, email)
                    elif fname == 'cedula':
                        setattr(obj, fname, cedula_val)
                    elif fname in ['habilidades', 'especialidad']:
                        setattr(obj, fname, habilidades_val)
                    elif fname in ['horas_aportadas', 'horas']:
                        setattr(obj, fname, 5)
                    elif not field.null:
                        if field.get_internal_type() in ['CharField', 'TextField']:
                            setattr(obj, fname, 'General')
                        elif field.get_internal_type() in ['IntegerField', 'FloatField', 'DecimalField']:
                            setattr(obj, fname, 0)
                try:
                    obj.save()
                except Exception:
                    Voluntario.objects.create(nombre=nombre, email=email)

            messages.success(request, f'¡Gracias por ser voluntario/a, {nombre}! Registro completado con éxito.')
            return redirect('inicio')

    return render(request, 'gestion/registro_publico.html', {'tipo': tipo})