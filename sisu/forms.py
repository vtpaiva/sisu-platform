# sisu/forms.py

from django import forms
from .models import Nota

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = [
            'nota_matematica',
            'nota_linguagens',
            'nota_humanas',
            'nota_natureza',
            'nota_redacao',
            'CO_IES_CURSO',
            'CO_IES',
            'DS_GRAU',
            'DS_TURNO',
            'DS_MOD_CONCORRENCIA',
            'CO_CAMPUS',
            'SG_UF_CAMPUS',
            # REMOVIDO: 'conteudo',
        ]
        widgets = {
            'nota_matematica': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Ex: 750.50'}),
            'nota_linguagens': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Ex: 680.25'}),
            'nota_humanas': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Ex: 720.00'}),
            'nota_natureza': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Ex: 690.75'}),
            'nota_redacao': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Ex: 920.00'}),
            # REMOVIDO: 'conteudo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Detalhes adicionais sobre a nota'}),
            'CO_IES_CURSO': forms.TextInput(attrs={'placeholder': 'Ex: 12345'}),
            'DS_GRAU': forms.TextInput(attrs={'placeholder': 'Ex: Bacharelado'}),
            'DS_TURNO': forms.TextInput(attrs={'placeholder': 'Ex: Integral'}),
            'DS_MOD_CONCORRENCIA': forms.TextInput(attrs={'placeholder': 'Ex: Ampla Concorrência'}),
            'SG_UF_CAMPUS': forms.TextInput(attrs={'placeholder': 'Ex: SP', 'maxlength': 2}),
        }