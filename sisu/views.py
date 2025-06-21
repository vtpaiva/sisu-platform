# sisu/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models.functions import TruncDate
from django.db.models import Count, Avg, F
from django.contrib import messages
from .models import Nota
from .forms import NotaForm
import random
import json

# Importações para Pandas e Plotly
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def dashboard_view(request): # Renomeada de volta para dashboard_view
    # --- Lógica da Aba 1: Inserção de Nota ---
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nota salva com sucesso!")
            # Redireciona para o GET da própria dashboard, pode incluir o parâmetro de aba aqui
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo '{form[field].label}': {error}")
    else:
        form = NotaForm()

    # --- Lógica da Aba 2: Gráficos de Medidas (com Plotly) ---
    notas = Nota.objects.all()

    plot_div_medias = ""
    plot_div_dist = ""
    plot_div_top_modalidades_pie = ""
    no_data_for_charts = False

    if not notas.exists():
        no_data_for_charts = True
    else:
        df = pd.DataFrame(list(notas.values()))
        
        areas = ['nota_matematica', 'nota_linguagens', 'nota_humanas', 'nota_natureza', 'nota_redacao']
        for area in areas:
            df[area] = pd.to_numeric(df[area])

        # Média e Mediana
        medias = df[areas].mean().reset_index()
        medias.columns = ['Área', 'Média']
        medianas = df[areas].median().reset_index()
        medianas.columns = ['Área', 'Mediana']
        nomes_amigaveis = {
            'nota_matematica': 'Matemática', 'nota_linguagens': 'Linguagens', 
            'nota_humanas': 'Humanas', 'nota_natureza': 'Natureza', 'nota_redacao': 'Redação'
        }
        medias['Área'] = medias['Área'].map(nomes_amigaveis)
        medianas['Área'] = medianas['Área'].map(nomes_amigaveis)
        fig_medias = go.Figure()
        fig_medias.update_layout(
            width=480,    # largura em pixels
            height=320,   # altura em pixels
            margin=dict(t=50, b=50, l=50, r=50)  # margens, opcional
        )
        fig_medias.add_trace(go.Bar(x=medias['Área'], y=medias['Média'], name='Média', marker_color='rgba(75, 192, 192, 0.8)'))
        fig_medias.add_trace(go.Bar(x=medianas['Área'], y=medianas['Mediana'], name='Mediana', marker_color='rgba(153, 102, 255, 0.8)'))
        fig_medias.update_layout( barmode='group', height=320, margin=dict(t=50, b=50, l=50, r=50))
        plot_div_medias = fig_medias.to_html(full_html=False, include_plotlyjs='cdn')

        # Distribuição das Médias Gerais
        df['media_geral'] = df[areas].mean(axis=1)
        fig_dist = px.histogram(df, x="media_geral", nbins=20)
        fig_dist.update_layout(width=450, height=320, margin=dict(t=50, b=50, l=50, r=50))
        plot_div_dist = fig_dist.to_html(full_html=False, include_plotlyjs='cdn')

        # Top 5 Modalidades de Concorrência
        top_modalidades_df = df.groupby('DS_MOD_CONCORRENCIA').size().reset_index(name='count')
        top_modalidades_df = top_modalidades_df.loc[top_modalidades_df['DS_MOD_CONCORRENCIA'].notna()]
        top_modalidades_df = top_modalidades_df.loc[top_modalidades_df['DS_MOD_CONCORRENCIA'] != '']
        top_modalidades_df = top_modalidades_df.sort_values(by='count', ascending=False).head(5)

        if not top_modalidades_df.empty:
            fig_top_modalidades_pie = px.pie(top_modalidades_df, values='count', names='DS_MOD_CONCORRENCIA')
            fig_top_modalidades_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_top_modalidades_pie.update_layout(width=450, height=400, margin=dict(t=50, b=50, l=50, r=50))
            plot_div_top_modalidades_pie = fig_top_modalidades_pie.to_html(full_html=False, include_plotlyjs='cdn')
        else:
            plot_div_top_modalidades_pie = "<p style='text-align: center; color: #777;'>Não há dados de modalidades de concorrência para exibir.</p>"

        variancias = df[areas].var().reset_index()

    variancias.columns = ['Área', 'Variância']
    variancias['Área'] = variancias['Área'].map(nomes_amigaveis)

    # Cria gráfico de barras
    fig_var = go.Figure()
    fig_var.add_trace(go.Bar(
        x=variancias['Área'],
        y=variancias['Variância'],
        marker_color='rgba(255, 99, 132, 0.8)'
    ))
    fig_var.update_layout(
        xaxis_title='Área',
        yaxis_title='Variância',
        width=450, height=320,
        margin=dict(t=50, b=50, l=50, r=50)
    )

    # HTML safe plot
    plot_div_variancias = fig_var.to_html(full_html=False, include_plotlyjs='cdn')

    notas_salvas = Nota.objects.all().order_by('-data_criacao')

    context = {
        'form': form,
        'object_list': notas_salvas,
        'plot_div_medias': plot_div_medias,
        'plot_div_dist': plot_div_dist,
        'plot_div_top_modalidades_pie': plot_div_top_modalidades_pie,
        'plot_div_variancias': plot_div_variancias,
        'no_data_for_charts': no_data_for_charts,
    }
    return render(request, 'dashboard.html', context) # Renderiza o template dashboard.html


# A API para a simulação preditiva continua sendo via AJAX
def prever_notas_api(request):
    if request.method == 'GET':
        previsoes = []
        cursos_exemplo = [
            {"nome": "Engenharia de Software", "universidade": "UFSCar", "campus": "São Carlos", "estado": "SP"},
            {"nome": "Medicina", "universidade": "USP", "campus": "Ribeirão Preto", "estado": "SP"},
            {"nome": "Ciência da Computação", "universidade": "Unicamp", "campus": "Campinas", "estado": "SP"},
            {"nome": "Direito", "universidade": "UFRJ", "campus": "Cidade Universitária", "estado": "RJ"},
            {"nome": "Administração", "universidade": "UFMG", "campus": "Pampulha", "estado": "MG"},
            {"nome": "Arquitetura e Urbanismo", "universidade": "UNB", "campus": "Darcy Ribeiro", "estado": "DF"},
            {"nome": "Odontologia", "universidade": "UFU", "campus": "Santa Mônica", "estado": "MG"},
            {"nome": "Engenharia Elétrica", "universidade": "ITA", "campus": "São José dos Campos", "estado": "SP"},
            {"nome": "Psicologia", "universidade": "UFBA", "campus": "Ondina", "estado": "BA"},
            {"nome": "Engenharia Mecânica", "universidade": "UFPE", "campus": "Cidade Universitária", "estado": "PE"},
            {"nome": "Enfermagem", "universidade": "UFSC", "campus": "Trindade", "estado": "SC"},
            {"nome": "Farmácia", "universidade": "UFPR", "campus": "Jardim Botânico", "estado": "PR"},
            {"nome": "Fisioterapia", "universidade": "UFPB", "campus": "Castelo Branco", "estado": "PB"},
            {"nome": "Jornalismo", "universidade": "UFES", "campus": "Goiabeiras", "estado": "ES"},
            {"nome": "Serviço Social", "universidade": "UFAM", "campus": "Manaus", "estado": "AM"},
            {"nome": "Engenharia Civil", "universidade": "UFPA", "campus": "Guamá", "estado": "PA"},
            {"nome": "Engenharia Química", "universidade": "UFPI", "campus": "Ininga", "estado": "PI"},
            {"nome": "Pedagogia", "universidade": "UFMT", "campus": "Cuiabá", "estado": "MT"},
            {"nome": "Ciências Biológicas", "universidade": "UFRGS", "campus": "Campus do Vale", "estado": "RS"},
            {"nome": "Biomedicina", "universidade": "UEPB", "campus": "Campina Grande", "estado": "PB"},
            {"nome": "Zootecnia", "universidade": "UFMS", "campus": "Campo Grande", "estado": "MS"},
            {"nome": "Veterinária", "universidade": "UFAC", "campus": "Rio Branco", "estado": "AC"},
            {"nome": "Geografia", "universidade": "UFAL", "campus": "Arapiraca", "estado": "AL"},
            {"nome": "Letras", "universidade": "UNIFAP", "campus": "Macapá", "estado": "AP"},
            {"nome": "Física", "universidade": "UFRR", "campus": "Boa Vista", "estado": "RR"},
            {"nome": "Química", "universidade": "UFTO", "campus": "Palmas", "estado": "TO"},
            {"nome": "História", "universidade": "UFMA", "campus": "Bacanga", "estado": "MA"},
            {"nome": "Ciências Sociais", "universidade": "UFRO", "campus": "Porto Velho", "estado": "RO"},
            {"nome": "Design", "universidade": "UEMG", "campus": "Belo Horizonte", "estado": "MG"},
            {"nome": "Artes Cênicas", "universidade": "UFPEL", "campus": "Pelotas", "estado": "RS"},
            {"nome": "Cinema e Audiovisual", "universidade": "UFF", "campus": "Niterói", "estado": "RJ"},
            {"nome": "Música", "universidade": "UFG", "campus": "Goiânia", "estado": "GO"},
            {"nome": "Engenharia Ambiental", "universidade": "UFV", "campus": "Viçosa", "estado": "MG"},
            {"nome": "Engenharia de Produção", "universidade": "UTFPR", "campus": "Curitiba", "estado": "PR"},
            {"nome": "Engenharia de Computação", "universidade": "UFRN", "campus": "Natal", "estado": "RN"},
            {"nome": "Engenharia de Alimentos", "universidade": "UFRA", "campus": "Belém", "estado": "PA"},
            {"nome": "Meteorologia", "universidade": "USP", "campus": "Butantã", "estado": "SP"},
            {"nome": "Oceanografia", "universidade": "FURG", "campus": "Rio Grande", "estado": "RS"},
            {"nome": "Estatística", "universidade": "UFRPE", "campus": "Dois Irmãos", "estado": "PE"},
            {"nome": "Biblioteconomia", "universidade": "UNESP", "campus": "Marília", "estado": "SP"},
            {"nome": "Ciência da Informação", "universidade": "UFS", "campus": "São Cristóvão", "estado": "SE"},
            {"nome": "Relações Internacionais", "universidade": "PUC-Rio", "campus": "Gávea", "estado": "RJ"},
            {"nome": "Engenharia Aeroespacial", "universidade": "UFABC", "campus": "São Bernardo do Campo", "estado": "SP"},
            {"nome": "Ciências Contábeis", "universidade": "UEMA", "campus": "São Luís", "estado": "MA"},
            {"nome": "Turismo", "universidade": "UFOP", "campus": "Ouro Preto", "estado": "MG"},
            {"nome": "Engenharia de Materiais", "universidade": "UFC", "campus": "Fortaleza", "estado": "CE"},
            {"nome": "Antropologia", "universidade": "UFPR", "campus": "Reitoria", "estado": "PR"},
            {"nome": "Engenharia de Petróleo", "universidade": "UENF", "campus": "Campos dos Goytacazes", "estado": "RJ"},
            {"nome": "Segurança da Informação", "universidade": "IFSP", "campus": "São Paulo", "estado": "SP"},
            {"nome": "Licenciatura em Computação", "universidade": "IFCE", "campus": "Fortaleza", "estado": "CE"},
            {"nome": "Engenharia Biomédica", "universidade": "UFPE", "campus": "Recife", "estado": "PE"},
        ]

        for i in range(len(cursos_exemplo)):
            curso = random.choice(cursos_exemplo)
            nota_prevista = round(random.uniform(600, 850), 2)
            previsoes.append({
                "curso": curso["nome"],
                "universidade": curso["universidade"],
                "campus": curso["campus"],
                "estado": curso["estado"],
                "nota_prevista": nota_prevista
            })
        return JsonResponse({"previsoes": previsoes})
    return JsonResponse({"error": "Método não permitido"}, status=405)