from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Categoria, Doacao, Recebedor, Perfil, Distribuicao, LocalEntrega


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfis'
    fk_name = 'usuario'

class CustomUserAdmin(UserAdmin):
    inlines = (PerfilInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'quantidade', 'categoria', 'status', 'doador')
    list_filter = ('categoria', 'status')
    search_fields = ('descricao', 'doador__username')

@admin.register(Recebedor)
class RecebedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf_cnpj', 'telefone')
    search_fields = ('nome', 'cpf_cnpj', 'telefone')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(LocalEntrega)
class LocalEntregaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Distribuicao)
class DistribuicaoAdmin(admin.ModelAdmin):
    list_display = ('doacao', 'recebedor', 'quantidade_distribuida', 'data_distribuicao')
    list_filter = ('data_distribuicao',)
    search_fields = ('doacao__descricao', 'recebedor__nome')

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo')
    list_filter = ('tipo',)

