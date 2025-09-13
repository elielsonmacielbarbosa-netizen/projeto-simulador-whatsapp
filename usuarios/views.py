from django.shortcuts import render, get_object_or_404, redirect
from .models import Grupo, Mensagem
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
import json


def home(request):
    grupos = Grupo.objects.all()

    contexto = {
        'grupos': grupos,
        'mensagens': [],
        'grupo_ativo': None,
    }
    return render(request, 'usuarios/home.html', contexto)


def chat_do_grupo(request, grupo_id):
    grupos = Grupo.objects.all()
    grupo_ativo = get_object_or_404(Grupo, pk=grupo_id)
    mensagens = Mensagem.objects.filter(grupo=grupo_ativo).order_by('id')

    contexto = {
        'grupos': grupos,
        'mensagens': mensagens,
        'grupo_ativo': grupo_ativo,
    }
    return render(request, 'usuarios/home.html', contexto)


def enviar_mensagem(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            texto_mensagem = dados.get('texto_mensagem')
            grupo_id = dados.get('grupo_id')
            imagem = None
        except (json.JSONDecodeError, TypeError):
            # Fallback para o caso de envio de formulário tradicional
            texto_mensagem = request.POST.get('texto_mensagem')
            grupo_id = request.POST.get('grupo_id')
            imagem = request.FILES.get('imagem')

        if grupo_id:
            grupo = get_object_or_404(Grupo, pk=grupo_id)
            nova_mensagem = Mensagem.objects.create(
                grupo=grupo,
                texto=texto_mensagem,
                autor_e_hora="Telemonitoramento",
                imagem=imagem,
                # Suas mensagens (Telemonitoramento) devem ter é_resposta=True
                é_resposta=True
            )
            return JsonResponse({'status': 'ok', 'mensagem_id': nova_mensagem.id})

    return JsonResponse({'status': 'error'}, status=400)


def encaminhar_mensagem(request, mensagem_id):
    mensagem_a_encaminhar = get_object_or_404(Mensagem, pk=mensagem_id)
    grupos = Grupo.objects.all()

    contexto = {
        'mensagem': mensagem_a_encaminhar,
        'grupos': grupos,
    }
    return render(request, 'usuarios/encaminhar.html', contexto)


def processar_encaminhamento(request, mensagem_id):
    if request.method == 'POST':
        grupos_destino_ids = request.POST.getlist('grupos')
        mensagem_original = get_object_or_404(Mensagem, pk=mensagem_id)

        for grupo_id in grupos_destino_ids:
            grupo_destino = get_object_or_404(Grupo, pk=grupo_id)

            nova_mensagem = Mensagem(
                grupo=grupo_destino,
                texto=mensagem_original.texto,
                autor_e_hora="Telemonitoramento",
                é_resposta=False
            )

            if mensagem_original.imagem:
                nova_mensagem.imagem = mensagem_original.imagem

            nova_mensagem.save()

        if grupos_destino_ids:
            return redirect('chat_do_grupo', grupo_id=grupos_destino_ids[0])
        else:
            return redirect('home')

    return redirect('encaminhar_mensagem', mensagem_id=mensagem_id)


def verificar_novas_mensagens(request, grupo_id):
    ultima_mensagem_id = request.GET.get('ultima_mensagem_id')

    # Busca apenas mensagens do operador
    mensagens_operador = Mensagem.objects.filter(grupo_id=grupo_id, autor_e_hora="CGE")

    if ultima_mensagem_id:
        mensagens_novas = mensagens_operador.filter(id__gt=ultima_mensagem_id)
    else:
        mensagens_novas = mensagens_operador.all()

    mensagens_json = []
    for mensagem in mensagens_novas:
        mensagens_json.append({
            'id': mensagem.id,
            'texto': mensagem.texto,
            'autor_e_hora': mensagem.autor_e_hora,
            'data_envio': mensagem.data_envio.strftime("%H:%M"),
            'imagem_url': mensagem.imagem.url if mensagem.imagem else None,
            # Mensagens do operador (CGE) devem ter é_resposta=False
            'é_resposta': False
        })

    return JsonResponse({'mensagens': mensagens_json})