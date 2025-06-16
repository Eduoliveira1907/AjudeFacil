from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Categoria(models.Model):
    nome = models.CharField("Nome da categoria", max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome

class LocalEntrega(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Recebedor(models.Model):
    nome = models.CharField("Nome do Recebedor", max_length=100)
    cpf_cnpj = models.CharField("CPF/CNPJ", max_length=20)
    endereco = models.TextField("Endereço")
    telefone = models.CharField("Telefone", max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} – {self.cpf_cnpj}"

class Doacao(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    quantidade = models.PositiveIntegerField()
    quantidade_inicial = models.PositiveIntegerField(editable=False, default=0, help_text="Quantidade total que foi doada inicialmente")
    local_entrega = models.ForeignKey(LocalEntrega, on_delete=models.CASCADE)
    doador = models.ForeignKey(User, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField("Status", max_length=20, choices=[('pendente', 'Pendente'), ('distribuida', 'Distribuída')], default='pendente')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.quantidade_inicial = self.quantidade
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.categoria.nome} – {self.quantidade} un."

class Distribuicao(models.Model):
    doacao = models.ForeignKey(Doacao, on_delete=models.CASCADE)
    recebedor = models.ForeignKey(Recebedor, on_delete=models.CASCADE)
    quantidade_distribuida = models.PositiveIntegerField()
    data_distribuicao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.recebedor.nome} recebeu "
            f"{self.quantidade_distribuida} de {self.doacao.categoria.nome}"
        )

class Perfil(models.Model):
    TIPO_CHOICES = [
        ('doador', 'Doador'),
        ('voluntario', 'Voluntário'),
        ('administrador', 'Administrador'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField("Tipo de usuário", max_length=20, choices=TIPO_CHOICES)
    cpf_cnpj = models.CharField("CPF/CNPJ", max_length=20, blank=True, null=True)
    data_nascimento_fundacao = models.DateField("Nascimento/Fundação", blank=True, null=True)
    endereco = models.TextField("Endereço", blank=True, null=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.username} ({self.tipo})"

@receiver(post_save, sender=User)
def criar_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(
            usuario=instance,
            tipo='administrador' if instance.is_superuser else 'doador'
        )

@receiver(post_save, sender=User)
def salvar_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
