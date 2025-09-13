from django.db import models


class Grupo(models.Model):
    nome = models.CharField(max_length=200)
    imagem_perfil = models.ImageField(upload_to='grupo_perfis/', blank=True, null=True)
    usa_ia = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class Mensagem(models.Model):
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name='mensagens')
    texto = models.TextField(blank=True, null=True)
    autor_e_hora = models.CharField(max_length=200)
    imagem = models.ImageField(upload_to='imagens/', blank=True, null=True)
    é_resposta = models.BooleanField(default=False)

    # Adicione esta nova linha
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.autor_e_hora}: {self.texto[:50]}'