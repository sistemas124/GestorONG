from django.db import models

class ProgramaSocial(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    meta_beneficiarios = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Voluntario(models.Model):
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=15, unique=True)
    email = models.EmailField()
    habilidades = models.CharField(max_length=200, help_text="Ej: Primeros auxilios, Docencia")
    horas_aportadas = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.habilidades})"

class Actividad(models.Model):
    nombre = models.CharField(max_length=150)
    programa = models.ForeignKey(ProgramaSocial, on_delete=models.CASCADE)
    fecha = models.DateField()
    lugar = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre

class TurnoApoyo(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    voluntario = models.ForeignKey(Voluntario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    asistio = models.BooleanField(default=False)

    def __str__(self):
        return f"Turno {self.actividad.nombre} - {self.voluntario}"

class Donante(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(default="contacto@donante.com")
    monto_donado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_donacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - ${self.monto_donado}"