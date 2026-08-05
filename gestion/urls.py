from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.inicio_view, name='inicio'),
    path('verificar-admin/', views.verificar_admin_view, name='verificar_admin'),
    
    # Registro Público
    path('unirse/', views.registro_publico_view, name='registro_publico'),
    
    # Voluntarios
    path('voluntarios/', views.lista_voluntarios, name='voluntarios'),
    path('voluntarios/editar/<int:id>/', views.editar_voluntario, name='editar_voluntario'),
    path('voluntarios/eliminar/<int:id>/', views.eliminar_voluntario, name='eliminar_voluntario'),
    
    # Programas
    path('programas/', views.lista_programas, name='programas'),
    path('programas/editar/<int:id>/', views.editar_programa, name='editar_programa'),
    path('programas/eliminar/<int:id>/', views.eliminar_programa, name='eliminar_programa'),
    
    # Donantes
    path('donantes/', views.lista_donantes, name='donantes'),
    path('donantes/editar/<int:id>/', views.editar_donante, name='editar_donante'),
    path('donantes/eliminar/<int:id>/', views.eliminar_donante, name='eliminar_donante'),
    
    # Login / Logout
    path('login/', auth_views.LoginView.as_view(template_name='gestion/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),

    # NUEVA RUTA PARA AJAX: Asignar voluntario a programa/tarea
    path('asignar-voluntario/', views.asignar_voluntario, name='asignar_voluntario'),
]