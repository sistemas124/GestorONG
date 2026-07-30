from django import forms
from .models import Voluntario, ProgramaSocial, Donante

class VoluntarioForm(forms.ModelForm):
    class Meta:
        model = Voluntario
        fields = ['cedula', 'nombre', 'email', 'habilidades', 'horas_aportadas']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1712345678'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'habilidades': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Medicina, Logística'}),
            'horas_aportadas': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProgramaSocialForm(forms.ModelForm):
    class Meta:
        model = ProgramaSocial
        fields = ['nombre', 'descripcion', 'meta_beneficiarios']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meta_beneficiarios': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class DonanteForm(forms.ModelForm):
    class Meta:
        model = Donante
        fields = ['nombre', 'email', 'monto_donado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@donante.com'}),
            'monto_donado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }