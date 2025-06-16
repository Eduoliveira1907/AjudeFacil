from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticação
    path('', views.inicio, name='inicio'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('trocar_senha/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html',success_url=reverse_lazy('senha_trocada')), name='trocar_senha'),
    path('senha_trocada/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='senha_trocada'),
    path('home/', views.redirecionar_home, name='home'),

    # Perfil de Usuário
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('cadastrar_usuario/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('editar_dados/', views.editar_dados, name='editar_dados'),

    # Doador
    path('home_doador/', views.home_doador, name='home_doador'),
    path('minhas_doacoes/', views.minhas_doacoes, name='minhas_doacoes'),
    path('fazer_doacoes_multiplas/', views.fazer_doacoes_multiplas, name='fazer_doacoes_multiplas'),

    # Voluntário
    path('home_voluntario/', views.home_voluntario, name='home_voluntario'),
    path('listar_doacoes/', views.listar_doacoes, name='listar_doacoes'),
    path('cadastrar_recebedor/', views.cadastrar_recebedor, name='cadastrar_recebedor'),
    path('distribuir_por_categoria/', views.distribuir_por_categoria, name='distribuir_por_categoria'),

    # Painel de Administração
    path('painel_admin/', views.admin_dashboard, name='admin_dashboard'),

    # Admin - Usuários
    path('painel_admin/usuarios/', views.gerenciar_usuarios, name='admin_gerenciar_usuarios'),
    path('painel_admin/usuarios/criar/', views.cadastrar_usuario, name='admin_criar_usuario'),
    path('painel_admin/usuarios/editar/<int:usuario_id>/', views.admin_editar_usuario, name='admin_editar_usuario'),
    path('painel_admin/usuarios/excluir/<int:usuario_id>/', views.admin_excluir_usuario, name='admin_excluir_usuario'),
    path('painel_admin/usuarios/<int:user_id>/status/', views.ativar_ou_desativar_usuario, name='admin_alterar_status_usuario'),

    # Admin - Categorias
    path('painel_admin/categorias/', views.admin_gerenciar_categorias, name='admin_gerenciar_categorias'),
    path('painel_admin/categorias/criar/', views.admin_criar_categoria, name='admin_criar_categoria'),
    path('painel_admin/categorias/editar/<int:categoria_id>/', views.admin_editar_categoria, name='admin_editar_categoria'),
    path('painel_admin/categorias/excluir/<int:categoria_id>/', views.admin_excluir_categoria, name='admin_excluir_categoria'),

    # Admin - Recebedores
    path('painel_admin/recebedores/', views.admin_gerenciar_recebedores, name='admin_gerenciar_recebedores'),
    path('painel_admin/recebedores/criar/', views.admin_criar_recebedor, name='admin_criar_recebedor'),
    path('painel_admin/recebedores/editar/<int:recebedor_id>/', views.admin_editar_recebedor, name='admin_editar_recebedor'),
    path('painel_admin/recebedores/excluir/<int:recebedor_id>/', views.admin_excluir_recebedor, name='admin_excluir_recebedor'),

    # Admin - Locais de Entrega
    path('painel_admin/locais_entrega/', views.admin_gerenciar_locais_entrega, name='admin_gerenciar_locais_entrega'),
    path('painel_admin/locais_entrega/criar/', views.admin_criar_local_entrega, name='admin_criar_local_entrega'),
    path('painel_admin/locais_entrega/editar/<int:local_id>/', views.admin_editar_local_entrega, name='admin_editar_local_entrega'),
    path('painel_admin/locais_entrega/excluir/<int:local_id>/', views.admin_excluir_local_entrega, name='admin_excluir_local_entrega'),

    # Admin - Relatórios
    path('painel_admin/relatorio/', views.admin_relatorio_doacoes, name='admin_relatorio'),


]
