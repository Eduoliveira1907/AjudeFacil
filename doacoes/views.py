from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Sum
from .models import Categoria, Doacao, Recebedor, Distribuicao, LocalEntrega
from .forms import FormCadastroUsuario, FormEditarUsuario, FormRecebedor, DistribuicaoMultiplaPorCategoriaForm, FormDoacoesMultiplas

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.tipo == 'administrador'

def registrar_usuario(request):
    if request.method == 'POST':
        form = FormCadastroUsuario(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get('tipo') == 'voluntario':
                user.is_active = False
            else:
                user.is_active = True

            user.save()

            perfil = user.perfil
            perfil.tipo = form.cleaned_data.get('tipo', 'doador')
            perfil.cpf_cnpj = form.cleaned_data.get('cpf_cnpj')
            perfil.endereco = form.cleaned_data.get('endereco')
            perfil.telefone = form.cleaned_data.get('telefone')
            perfil.data_nascimento_fundacao = form.cleaned_data.get('data_nascimento_fundacao')
            perfil.save()

            messages.success(request, "Cadastro realizado com sucesso! Faça login para continuar.")
            return redirect('login')
    else:
        form = FormCadastroUsuario()

    return render(request, 'doacoes/form_cadastro.html', {'form': form, 'acao': 'Cadastrar-se'})

# AUTENTICAÇÃO
def inicio(request):
    return redirect('login')

def login_usuario(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('senha')
        )
        if user:
            if not user.is_active:
                messages.error(request, 'Conta não ativada.')
                return redirect('login')
            login(request, user)
            perfil = getattr(user, 'perfil', None)
            if user.is_superuser or (perfil and perfil.tipo == 'administrador'):
                return redirect('admin_dashboard')
            if perfil and perfil.tipo == 'voluntario':
                return redirect('home_voluntario')
            if perfil and perfil.tipo == 'doador':
                return redirect('home_doador')
        messages.error(request, 'Usuário ou senha inválidos.')
        return redirect('login')
    return render(request, 'doacoes/login.html')

def logout_usuario(request):
    logout(request)
    return redirect('login')

@login_required
def redirecionar_home(request):
    perfil = getattr(request.user, 'perfil', None)
    if request.user.is_superuser or (perfil and perfil.tipo == 'administrador'):
        return redirect('admin_dashboard')
    if perfil and perfil.tipo == 'voluntario':
        return redirect('home_voluntario')
    if perfil and perfil.tipo == 'doador':
        return redirect('home_doador')
    return redirect('login')

@login_required
def editar_dados(request):
    perfil = request.user.perfil
    url_voltar = 'home_voluntario' if perfil.tipo == 'voluntario' else 'home_doador'

    if request.method == 'POST':
        form = FormEditarUsuario(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            perfil.endereco = form.cleaned_data.get('endereco', perfil.endereco)
            perfil.telefone = form.cleaned_data.get('telefone', perfil.telefone)
            perfil.save()
            return redirect(url_voltar)
    else:
        form = FormEditarUsuario(
            instance=request.user,
            initial={
                'endereco': perfil.endereco,
                'telefone': perfil.telefone
            }
        )

    return render(request, 'doacoes/editar_usuario.html', {
        'form': form,
        'perfil': perfil,
        'url_voltar': url_voltar,
    })

# USUÁRIOS (Admin)
@login_required
@user_passes_test(is_admin)
def cadastrar_usuario(request):
    if request.method == 'POST':
        form = FormCadastroUsuario(request.POST, usuario_logado=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            perfil = user.perfil
            perfil.tipo = form.cleaned_data['tipo']
            perfil.cpf_cnpj = form.cleaned_data.get('cpf_cnpj')
            perfil.endereco = form.cleaned_data.get('endereco')
            perfil.telefone = form.cleaned_data.get('telefone')
            perfil.data_nascimento_fundacao = form.cleaned_data.get('data_nascimento_fundacao')
            perfil.save()
            return redirect('admin_gerenciar_usuarios')
    else:
        form = FormCadastroUsuario(usuario_logado=request.user)

    return render(request, 'doacoes/admin/form_usuario.html', {'form': form, 'acao': 'Criar Usuário'})

@login_required
@user_passes_test(is_admin)
def gerenciar_usuarios(request):
    usuarios = User.objects.select_related('perfil').all()
    return render(request, 'doacoes/admin/gerenciar_usuarios.html', {'usuarios': usuarios})

@login_required
@user_passes_test(is_admin)
def ativar_ou_desativar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if usuario.perfil.tipo != 'administrador':
        usuario.is_active = not usuario.is_active
        usuario.save()
        messages.success(request, f"Usuário {'ativado' if usuario.is_active else 'desativado'} com sucesso.")
    else:
        messages.warning(request, "Você não pode alterar o status de administradores.")
    return redirect('admin_gerenciar_usuarios')

@login_required
@user_passes_test(is_admin)
def admin_editar_usuario(request, usuario_id):
    user = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        form = FormEditarUsuario(request.POST, instance=user)
        if form.is_valid():
            form.save()
            perfil = user.perfil
            perfil.tipo = request.POST.get('tipo', perfil.tipo)
            perfil.save()
            return redirect('admin_gerenciar_usuarios')
    else:
        form = FormEditarUsuario(instance=user)
    return render(request, 'doacoes/admin/form_usuario.html', {'form': form, 'acao': 'Editar Usuário'})

@login_required
@user_passes_test(is_admin)
def admin_excluir_usuario(request, usuario_id):
    user = get_object_or_404(User, id=usuario_id)
    if user != request.user:
        user.delete()
    return redirect('admin_gerenciar_usuarios')

# DOADOR
@login_required
def home_doador(request):
    return render(request, 'doacoes/home_doador.html')

@login_required
def minhas_doacoes(request):
    if request.user.perfil.tipo != 'doador':
        return HttpResponseForbidden()
    doacoes = Doacao.objects.filter(doador=request.user)
    return render(request, 'doacoes/minhas_doacoes.html', {'doacoes': doacoes})

@login_required
def fazer_doacoes_multiplas(request):
    if request.user.perfil.tipo != 'doador':
        return HttpResponseForbidden()

    categorias = Categoria.objects.all()

    if request.method == 'POST':
        form = FormDoacoesMultiplas(request.POST, categorias=categorias)
        if form.is_valid():
            local = form.cleaned_data['local_entrega']
            desc_geral = form.cleaned_data.get('descricao', '')

            for cat in categorias:
                qtd = form.cleaned_data.get(f'quantidade_{cat.id}')
                if qtd and qtd > 0:
                    Doacao.objects.create(
                        categoria=cat,
                        quantidade=qtd,
                        local_entrega=local,
                        descricao=desc_geral or f"Doação de {qtd} {cat.nome.lower()}",
                        doador=request.user
                    )
            messages.success(request, "Doações registradas com sucesso.")
            return redirect('minhas_doacoes')
    else:
        form = FormDoacoesMultiplas(categorias=categorias)

    return render(request, 'doacoes/form_doacoes_multiplas.html', {
        'form': form,
        'categorias': categorias,
        'url_voltar': 'home_doador'
    })

# VOLUNTÁRIO
@login_required
def home_voluntario(request):
    doacoes = Doacao.objects.filter(status='pendente')
    return render(request, 'doacoes/home_voluntario.html', {'doacoes': doacoes})

@login_required
def listar_doacoes(request):
    doacoes_agrupadas = (
        Doacao.objects
        .filter(status='pendente')  
        .values('categoria__nome', 'local_entrega__nome')
        .annotate(total_quantidade=Sum('quantidade'))
        .order_by('categoria__nome')
    )
    context = {'doacoes_agrupadas': doacoes_agrupadas}
    return render(request, 'doacoes/lista_doacoes.html', context)

@login_required
def cadastrar_recebedor(request):
    if request.method == 'POST':
        form = FormRecebedor(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home_voluntario')
    else:
        form = FormRecebedor()
    return render(request, 'doacoes/form_recebedor.html', {'form': form})

@login_required
def distribuir_por_categoria(request):
    from django.db.models import Sum
    categorias = Categoria.objects.annotate(disponivel=Sum('doacao__quantidade')).filter(disponivel__gt=0)

    if request.method == 'POST':
        form = DistribuicaoMultiplaPorCategoriaForm(request.POST, categorias=categorias)
        if form.is_valid():
            recebedor = form.cleaned_data['recebedor']
            for cat in categorias:
                quantidade = form.cleaned_data.get(f'quantidade_{cat.id}') or 0
                if quantidade > 0:
                    doacoes = Doacao.objects.filter(categoria=cat, status='pendente').order_by('data_criacao')
                    restante = quantidade
                    for d in doacoes:
                        if d.quantidade <= 0:
                            continue
                        usar = min(restante, d.quantidade)
                        Distribuicao.objects.create(
                            doacao=d,
                            recebedor=recebedor,
                            quantidade_distribuida=usar
                        )
                        d.quantidade -= usar
                        if d.quantidade == 0:
                            d.status = 'distribuida'
                        d.save()
                        restante -= usar
                        if restante <= 0:
                            break
            messages.success(request, "Distribuição por categoria realizada com sucesso.")
            return redirect('home_voluntario')
    else:
        form = DistribuicaoMultiplaPorCategoriaForm(categorias=categorias)

    return render(request, 'doacoes/distribuir_por_categoria.html', {
        'form': form,
        'categorias': categorias
    })

# PAINEL ADMINISTRADOR
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'doacoes/admin/dashboard.html', {
        'num_users': User.objects.count(),
        'num_categories': Categoria.objects.count(),
        'num_recebedores': Recebedor.objects.count(),
        'num_locais_entrega': LocalEntrega.objects.count(),
    })

@login_required
@user_passes_test(is_admin)
def admin_gerenciar_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'doacoes/admin/gerenciar_categorias.html', {'categorias': categorias})

@login_required
@user_passes_test(is_admin)
def admin_criar_categoria(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            Categoria.objects.create(nome=nome)
            return redirect('admin_gerenciar_categorias')
    return render(request, 'doacoes/admin/form_categoria.html', {'acao': 'Criar Categoria'})

@login_required
@user_passes_test(is_admin)
def admin_editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            categoria.nome = nome
            categoria.save()
            return redirect('admin_gerenciar_categorias')
    return render(request, 'doacoes/admin/form_categoria.html', {
        'acao': 'Editar Categoria', 'categoria': categoria
    })

@login_required
@user_passes_test(is_admin)
def admin_excluir_categoria(request, categoria_id):
    get_object_or_404(Categoria, id=categoria_id).delete()
    return redirect('admin_gerenciar_categorias')

@login_required
@user_passes_test(is_admin)
def admin_gerenciar_locais_entrega(request):
    locais = LocalEntrega.objects.all()
    return render(request, 'doacoes/admin/gerenciar_locais_entrega.html', {'locais': locais})

@login_required
@user_passes_test(is_admin)
def admin_criar_local_entrega(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            LocalEntrega.objects.create(nome=nome)
            return redirect('admin_gerenciar_locais_entrega')
    return render(request, 'doacoes/admin/form_local_entrega.html', {'acao': 'Adicionar'})

@login_required
@user_passes_test(is_admin)
def admin_editar_local_entrega(request, local_id):
    local = get_object_or_404(LocalEntrega, id=local_id)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            local.nome = nome
            local.save()
            return redirect('admin_gerenciar_locais_entrega')
    return render(request, 'doacoes/admin/form_local_entrega.html', {'local': local, 'acao': 'Editar'})

@login_required
@user_passes_test(is_admin)
def admin_excluir_local_entrega(request, local_id):
    local = get_object_or_404(LocalEntrega, id=local_id)
    local.delete()
    return redirect('admin_gerenciar_locais_entrega')

@login_required
@user_passes_test(is_admin)
def admin_gerenciar_recebedores(request):
    recebedores = Recebedor.objects.all()
    return render(request, 'doacoes/admin/gerenciar_recebedores.html', {'recebedores': recebedores})

@login_required
@user_passes_test(is_admin)
def admin_criar_recebedor(request):
    if request.method == 'POST':
        form = FormRecebedor(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_gerenciar_recebedores')
    else:
        form = FormRecebedor()
    return render(request, 'doacoes/admin/form_recebedor.html', {'form': form, 'acao': 'Criar Recebedor'})

@login_required
@user_passes_test(is_admin)
def admin_editar_recebedor(request, recebedor_id):
    rec = get_object_or_404(Recebedor, id=recebedor_id)
    if request.method == 'POST':
        form = FormRecebedor(request.POST, instance=rec)
        if form.is_valid():
            form.save()
            return redirect('admin_gerenciar_recebedores')
    else:
        form = FormRecebedor(instance=rec)
    return render(request, 'doacoes/admin/form_recebedor.html', {'form': form, 'acao': 'Editar Recebedor'})

@login_required
@user_passes_test(is_admin)
def admin_excluir_recebedor(request, recebedor_id):
    get_object_or_404(Recebedor, id=recebedor_id).delete()
    return redirect('admin_gerenciar_recebedores')

@login_required
@user_passes_test(is_admin)
def admin_relatorio_doacoes(request):
    cid = request.GET.get('categoria')
    status = request.GET.get('status')
    lid = request.GET.get('local_entrega')

    categorias = Categoria.objects.all()
    locais = LocalEntrega.objects.all()

    filtro_doacao = {}
    filtro_distribuicao = {}

    if cid:
        filtro_doacao['categoria_id'] = cid
        filtro_distribuicao['doacao__categoria_id'] = cid

    if lid:
        filtro_doacao['local_entrega_id'] = lid
        filtro_distribuicao['doacao__local_entrega_id'] = lid

    doacoes = []
    total = 0

    if status == "pendente":
        doacoes = Doacao.objects.filter(status="pendente", **filtro_doacao)
        total = doacoes.aggregate(Sum('quantidade'))['quantidade__sum'] or 0

    elif status == "distribuida":
        distribuicoes = Distribuicao.objects.filter(**filtro_distribuicao).select_related('doacao__categoria', 'doacao__doador')
        doacoes = [{
            'categoria': d.doacao.categoria,
            'quantidade': d.quantidade_distribuida,
            'status': "distribuida",
            'local_entrega': d.doacao.local_entrega,
            'doador': d.doacao.doador
        } for d in distribuicoes]
        total = sum(d['quantidade'] for d in doacoes)

    else:
        doacoes_pendentes = Doacao.objects.filter(status="pendente", **filtro_doacao)
        distribuicoes = Distribuicao.objects.filter(**filtro_distribuicao).select_related('doacao__categoria', 'doacao__doador')

        distribuicoes_formatadas = [{
            'categoria': d.doacao.categoria,
            'quantidade': d.quantidade_distribuida,
            'status': "distribuida",
            'local_entrega': d.doacao.local_entrega,
            'doador': d.doacao.doador
        } for d in distribuicoes]

        doacoes = list(doacoes_pendentes) + distribuicoes_formatadas

        total_pendentes = doacoes_pendentes.aggregate(Sum('quantidade'))['quantidade__sum'] or 0
        total_distribuidas = sum(d['quantidade'] for d in distribuicoes_formatadas)
        total = total_pendentes + total_distribuidas

    return render(request, 'doacoes/admin/relatorio_admin.html', {
        'doacoes': doacoes,
        'categorias': categorias,
        'cid': cid,
        'status': status,
        'total': total,
        'locais': locais,
        'lid': lid         
    })
