from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('grupo/<int:grupo_id>/', views.chat_do_grupo, name='chat_do_grupo'),
    path('enviar/', views.enviar_mensagem, name='enviar_mensagem'),
    path('encaminhar/<int:mensagem_id>/', views.encaminhar_mensagem, name='encaminhar_mensagem'),
    path('processar-encaminhamento/<int:mensagem_id>/', views.processar_encaminhamento, name='processar_encaminhamento'),
]