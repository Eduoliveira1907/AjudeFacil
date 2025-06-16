from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recebedor, Perfil, LocalEntrega
from validate_docbr import CPF, CNPJ # type: ignore
import re

class FormCadastroUsuario(UserCreationForm):
    tipo = forms.ChoiceField(
        choices=Perfil.TIPO_CHOICES,
        label='Tipo de usuário',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    email = forms.EmailField(
        label='E-mail', required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    cpf_cnpj = forms.CharField(
        label='CPF/CNPJ', max_length=20, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    data_nascimento_fundacao = forms.DateField(
        label='Data de nascimento/fundação', required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    endereco = forms.CharField(
        label='Endereço', required=True,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})
    )
    telefone = forms.CharField(
        label='Telefone', max_length=20, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, usuario_logado=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not usuario_logado or not usuario_logado.is_authenticated:
            self.fields['tipo'].choices = [
                (k, v) for k, v in Perfil.TIPO_CHOICES if k != 'administrador'
            ]
        elif not hasattr(usuario_logado, 'perfil') or usuario_logado.perfil.tipo != 'administrador':
            self.fields.pop('tipo')

    def clean_cpf_cnpj(self):
        valor = self.cleaned_data.get('cpf_cnpj', '')
        valor_numeros = re.sub(r'\D', '', valor)
        cpf = CPF()
        cnpj = CNPJ()
        if len(valor_numeros) == 11:
            if not cpf.validate(valor_numeros):
                raise forms.ValidationError('CPF inválido.')
        elif len(valor_numeros) == 14:
            if not cnpj.validate(valor_numeros):
                raise forms.ValidationError('CNPJ inválido.')
        else:
            raise forms.ValidationError('Informe um CPF (11 dígitos) ou CNPJ (14 dígitos) válido.')
        return valor_numeros

    def clean_telefone(self):
        valor = self.cleaned_data.get('telefone', '')
        valor_numeros = re.sub(r'\D', '', valor)
        if len(valor_numeros) not in [10, 11]:
            raise forms.ValidationError('Telefone inválido. Informe com DDD (10 ou 11 dígitos).')
        return valor_numeros

class FormEditarUsuario(forms.ModelForm):
    endereco = forms.CharField(
        label='Endereço', required=True,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})
    )
    telefone = forms.CharField(
        label='Telefone', max_length=20, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_telefone(self):
        valor = self.cleaned_data.get('telefone', '')
        valor_numeros = re.sub(r'\D', '', valor)
        if len(valor_numeros) not in [10, 11]:
            raise forms.ValidationError('Telefone inválido. Informe com DDD (10 ou 11 dígitos).')
        return valor_numeros

class FormDoacoesMultiplas(forms.Form):
    local_entrega = forms.ModelChoiceField(
        label='Local de entrega',
        queryset=LocalEntrega.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    descricao = forms.CharField(
        label='Descrição geral',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )

    def __init__(self, *args, categorias=None, **kwargs):
        super().__init__(*args, **kwargs)
        if categorias:
            for cat in categorias:
                self.fields[f'quantidade_{cat.id}'] = forms.IntegerField(
                    label=cat.nome,
                    required=False,
                    min_value=0,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'style': 'width: 200px;'
                    })
                )

class FormRecebedor(forms.ModelForm):
    class Meta:
        model = Recebedor
        fields = ['nome', 'cpf_cnpj', 'endereco', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome do Recebedor',
            'cpf_cnpj': 'CPF/CNPJ',
            'endereco': 'Endereço',
            'telefone': 'Telefone',
        }

    def clean_cpf_cnpj(self):
        valor = self.cleaned_data.get('cpf_cnpj', '')
        valor_numeros = re.sub(r'\D', '', valor)
        cpf = CPF()
        cnpj = CNPJ()
        if len(valor_numeros) == 11:
            if not cpf.validate(valor_numeros):
                raise forms.ValidationError('CPF inválido.')
        elif len(valor_numeros) == 14:
            if not cnpj.validate(valor_numeros):
                raise forms.ValidationError('CNPJ inválido.')
        else:
            raise forms.ValidationError('Informe um CPF (11 dígitos) ou CNPJ (14 dígitos) válido.')
        return valor_numeros

    def clean_telefone(self):
        valor = self.cleaned_data.get('telefone', '')
        valor_numeros = re.sub(r'\D', '', valor)
        if len(valor_numeros) not in [10, 11]:
            raise forms.ValidationError('Telefone inválido. Informe com DDD (10 ou 11 dígitos).')
        return valor_numeros

class DistribuicaoMultiplaPorCategoriaForm(forms.Form):
    recebedor = forms.ModelChoiceField(
        queryset=Recebedor.objects.all(),
        label='Recebedor',
        required=True
    )

    def __init__(self, *args, categorias=None, **kwargs):
        super().__init__(*args, **kwargs)
        if categorias:
            for cat in categorias:
                self.fields[f'quantidade_{cat.id}'] = forms.IntegerField(
                    label=f"{cat.nome} (Disponível: {cat.disponivel})",
                    required=False,
                    min_value=0,
                    max_value=cat.disponivel,
                    widget=forms.NumberInput(attrs={'style': 'width: 100px'})
                )

class FormLocalEntrega(forms.ModelForm):
    class Meta:
        model = LocalEntrega
        fields = ['nome']
        widgets = {'nome': forms.TextInput(attrs={'class': 'form-control'})}
