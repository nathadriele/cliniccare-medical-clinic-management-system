import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from utils.db_manager import db_manager
from components.navbar import create_page_header

def create_layout():
    """Cria o layout da página de relatórios"""
    
    return html.Div([
        # Cabeçalho da página
        create_page_header(
            title="Relatórios e Análises",
            subtitle="Insights estratégicos e análises de desempenho",
            actions=[
                dbc.Button([
                    html.I(className="fas fa-download me-1"),
                    "Exportar PDF"
                ], color="primary", id="btn-exportar-pdf"),
                dbc.Button([
                    html.I(className="fas fa-file-excel me-1"),
                    "Exportar Excel"
                ], color="outline-success", id="btn-exportar-excel")
            ]
        ),
        
        # Filtros de período
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Período de Análise:"),
                        dcc.DatePickerRange(
                            id='date-range-relatorios',
                            start_date=(datetime.now() - timedelta(days=90)).date(),
                            end_date=datetime.now().date(),
                            display_format='DD/MM/YYYY'
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Tipo de Relatório:"),
                        dcc.Dropdown(
                            id='dropdown-tipo-relatorio',
                            options=[
                                {'label': 'Geral', 'value': 'geral'},
                                {'label': 'Financeiro', 'value': 'financeiro'},
                                {'label': 'Operacional', 'value': 'operacional'},
                                {'label': 'Pacientes', 'value': 'pacientes'}
                            ],
                            value='geral'
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Atualizar:"),
                        html.Br(),
                        dbc.Button([
                            html.I(className="fas fa-sync me-1"),
                            "Atualizar"
                        ], color="outline-primary", size="sm", id="btn-atualizar-relatorios")
                    ], md=4)
                ])
            ])
        ], className="mb-4"),
        
        # Conteúdo dos relatórios
        html.Div(id="conteudo-relatorios"),
        
        # Interval para atualização
        dcc.Interval(
            id='interval-relatorios',
            interval=5*60*1000,  # Atualiza a cada 5 minutos
            n_intervals=0
        )
    ])

@callback(
    Output('conteudo-relatorios', 'children'),
    [Input('btn-atualizar-relatorios', 'n_clicks'),
     Input('interval-relatorios', 'n_intervals')],
    [State('date-range-relatorios', 'start_date'),
     State('date-range-relatorios', 'end_date'),
     State('dropdown-tipo-relatorio', 'value')]
)
def update_relatorios(n_clicks, n_intervals, start_date, end_date, tipo_relatorio):
    """Atualiza conteúdo dos relatórios"""
    
    if tipo_relatorio == 'geral':
        return create_relatorio_geral(start_date, end_date)
    elif tipo_relatorio == 'financeiro':
        return create_relatorio_financeiro(start_date, end_date)
    elif tipo_relatorio == 'operacional':
        return create_relatorio_operacional(start_date, end_date)
    elif tipo_relatorio == 'pacientes':
        return create_relatorio_pacientes(start_date, end_date)
    
    return html.Div()

def create_relatorio_geral(start_date, end_date):
    """Cria relatório geral"""
    
    try:
        # KPIs principais
        consultas = db_manager.get_consultas_periodo(start_date, end_date)
        total_consultas = len(consultas)
        
        receitas = db_manager.execute_query('''
            SELECT COALESCE(SUM(valor), 0) as total FROM financeiro 
            WHERE tipo = 'receita' AND DATE(data_vencimento) BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        pacientes_ativos = db_manager.execute_query('''
            SELECT COUNT(DISTINCT paciente_id) as total FROM consultas 
            WHERE DATE(data_consulta) BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        return html.Div([
            # KPIs
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{total_consultas:,}", className="text-primary"),
                            html.P("Total de Consultas", className="mb-0")
                        ])
                    ], className="text-center")
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"R$ {(receitas.iloc[0]['total'] or 0):,.2f}", className="text-success"),
                            html.P("Receita Total", className="mb-0")
                        ])
                    ], className="text-center")
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{(pacientes_ativos.iloc[0]['total'] or 0):,}", className="text-info"),
                            html.P("Pacientes Atendidos", className="mb-0")
                        ])
                    ], className="text-center")
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3(f"{(total_consultas/max((datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days, 1)):.1f}", className="text-warning"),
                            html.P("Consultas/Dia", className="mb-0")
                        ])
                    ], className="text-center")
                ], md=3)
            ], className="mb-4"),
            
            # Gráficos
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("📈 Evolução de Consultas", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_grafico_evolucao_consultas(start_date, end_date)
                            )
                        ])
                    ])
                ], md=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("🏥 Por Especialidade", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_grafico_especialidades(start_date, end_date)
                            )
                        ])
                    ])
                ], md=4)
            ], className="mb-4"),
            
            # Tabela resumo
            dbc.Card([
                dbc.CardHeader([
                    html.H5("📊 Resumo por Médico", className="mb-0")
                ]),
                dbc.CardBody([
                    create_tabela_resumo_medicos(start_date, end_date)
                ])
            ])
        ])
        
    except Exception as e:
        return dbc.Alert(f"Erro ao gerar relatório: {str(e)}", color="danger")

def create_relatorio_financeiro(start_date, end_date):
    """Cria relatório financeiro"""
    
    try:
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("💰 Análise Financeira", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_grafico_financeiro_detalhado(start_date, end_date)
                            )
                        ])
                    ])
                ], md=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("📊 Categorias", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_grafico_categorias_financeiro(start_date, end_date)
                            )
                        ])
                    ])
                ], md=4)
            ])
        ])
        
    except Exception as e:
        return dbc.Alert(f"Erro ao gerar relatório financeiro: {str(e)}", color="danger")

def create_relatorio_operacional(start_date, end_date):
    """Cria relatório operacional"""
    
    try:
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("⏰ Horários de Pico", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_grafico_horarios_pico(start_date, end_date)
                            )
                        ])
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("📅 Dias da Semana", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_grafico_dias_semana(start_date, end_date)
                            )
                        ])
                    ])
                ], md=6)
            ])
        ])
        
    except Exception as e:
        return dbc.Alert(f"Erro ao gerar relatório operacional: {str(e)}", color="danger")

def create_relatorio_pacientes(start_date, end_date):
    """Cria relatório de pacientes"""
    
    try:
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("👥 Perfil dos Pacientes", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_grafico_perfil_pacientes(start_date, end_date)
                            )
                        ])
                    ])
                ])
            ])
        ])
        
    except Exception as e:
        return dbc.Alert(f"Erro ao gerar relatório de pacientes: {str(e)}", color="danger")

def create_grafico_evolucao_consultas(start_date, end_date):
    """Cria gráfico de evolução de consultas"""
    
    try:
        consultas = db_manager.get_consultas_periodo(start_date, end_date)
        
        if consultas.empty:
            fig = go.Figure()
            fig.add_annotation(text="Nenhuma consulta encontrada", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        consultas['data'] = pd.to_datetime(consultas['data_consulta']).dt.date
        consultas_por_dia = consultas.groupby('data').size().reset_index(name='total')
        
        fig = px.line(consultas_por_dia, x='data', y='total', 
                     title='Consultas por Dia', markers=True)
        fig.update_layout(height=300)
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erro: {str(e)}", 
                         xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

def create_grafico_especialidades(start_date, end_date):
    """Cria gráfico por especialidades"""
    
    try:
        consultas = db_manager.get_consultas_periodo(start_date, end_date)
        
        if consultas.empty:
            fig = go.Figure()
            fig.add_annotation(text="Nenhum dado disponível", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        especialidades = consultas['especialidade'].value_counts()
        
        fig = px.pie(values=especialidades.values, names=especialidades.index)
        fig.update_layout(height=300, showlegend=True)
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erro: {str(e)}", 
                         xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

def create_grafico_financeiro_detalhado(start_date, end_date):
    """Cria gráfico financeiro detalhado"""
    
    try:
        financeiro = db_manager.execute_query('''
            SELECT 
                DATE(data_vencimento) as data,
                tipo,
                SUM(valor) as valor
            FROM financeiro 
            WHERE DATE(data_vencimento) BETWEEN ? AND ?
            GROUP BY DATE(data_vencimento), tipo
            ORDER BY data
        ''', (start_date, end_date))
        
        if financeiro.empty:
            fig = go.Figure()
            fig.add_annotation(text="Nenhum dado financeiro encontrado", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = px.bar(financeiro, x='data', y='valor', color='tipo',
                    title='Receitas vs Despesas por Dia',
                    color_discrete_map={'receita': 'green', 'despesa': 'red'})
        fig.update_layout(height=400)
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erro: {str(e)}", 
                         xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

def create_grafico_categorias_financeiro(start_date, end_date):
    """Cria gráfico de categorias financeiras"""
    
    try:
        categorias = db_manager.execute_query('''
            SELECT categoria, SUM(valor) as total
            FROM financeiro 
            WHERE DATE(data_vencimento) BETWEEN ? AND ?
            GROUP BY categoria
        ''', (start_date, end_date))
        
        if categorias.empty:
            fig = go.Figure()
            fig.add_annotation(text="Nenhuma categoria encontrada", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = px.pie(categorias, values='total', names='categoria')
        fig.update_layout(height=300)
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erro: {str(e)}", 
                         xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

def create_grafico_horarios_pico(start_date, end_date):
    """Cria gráfico de horários de pico"""
    
    try:
        consultas = db_manager.get_consultas_periodo(start_date, end_date)
        
        if consultas.empty:
            fig = go.Figure()
            fig.add_annotation(text="Nenhuma consulta encontrada", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        consultas['hora'] = pd.to_datetime(consultas['data_consulta']).dt.hour
        horarios = consultas['hora'].value_counts().sort_index()
        
        fig = px.bar(x=horarios.index, y=horarios.values,
                    title='Consultas por Horário',
                    labels={'x': 'Hora', 'y': 'Número de Consultas'})
        fig.update_layout(height=300)
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erro: {str(e)}", 
                         xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

def create_grafico_dias_semana(start_date, end_date):
    """Cria gráfico de dias da semana"""
    
    try:
        consultas = db_manager.get_consultas_periodo(start_date, end_date)
        
        if consultas.empty:
            fig = go.Figure()
            fig.add_annotation(text="Nenhuma consulta encontrada", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        consultas['dia_semana'] = pd.to_datetime(consultas['data_consulta']).dt.day_name()
        dias = consultas['dia_semana'].value_counts()
        
        # Ordenar dias da semana
        ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias = dias.reindex(ordem_dias, fill_value=0)
        
        fig = px.bar(x=dias.index, y=dias.values,
                    title='Consultas por Dia da Semana')
        fig.update_layout(height=300)
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erro: {str(e)}", 
                         xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

def create_grafico_perfil_pacientes(start_date, end_date):
    """Cria gráfico de perfil dos pacientes"""
    
    try:
        # Simulação de dados de perfil (idade, gênero, etc.)
        pacientes = db_manager.execute_query('''
            SELECT DISTINCT p.convenio
            FROM pacientes p
            JOIN consultas c ON p.id = c.paciente_id
            WHERE DATE(c.data_consulta) BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        if pacientes.empty:
            fig = go.Figure()
            fig.add_annotation(text="Nenhum paciente encontrado", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        convenios = pacientes['convenio'].value_counts()
        
        fig = px.pie(values=convenios.values, names=convenios.index,
                    title='Distribuição por Convênio')
        fig.update_layout(height=300)
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Erro: {str(e)}", 
                         xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

def create_tabela_resumo_medicos(start_date, end_date):
    """Cria tabela resumo por médicos"""
    
    try:
        resumo = db_manager.execute_query('''
            SELECT 
                m.nome as medico,
                m.especialidade,
                COUNT(c.id) as total_consultas,
                COALESCE(SUM(c.valor), 0) as receita_total,
                COALESCE(AVG(c.valor), 0) as valor_medio
            FROM medicos m
            LEFT JOIN consultas c ON m.id = c.medico_id 
                AND DATE(c.data_consulta) BETWEEN ? AND ?
            GROUP BY m.id, m.nome, m.especialidade
            ORDER BY total_consultas DESC
        ''', (start_date, end_date))
        
        if resumo.empty:
            return html.P("Nenhum dado encontrado", className="text-muted text-center")
        
        # Criar tabela
        rows = []
        for _, row in resumo.iterrows():
            tr = html.Tr([
                html.Td(row['medico']),
                html.Td(row['especialidade']),
                html.Td(f"{row['total_consultas']:,}"),
                html.Td(f"R$ {row['receita_total']:,.2f}"),
                html.Td(f"R$ {row['valor_medio']:.2f}")
            ])
            rows.append(tr)
        
        table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Médico"),
                    html.Th("Especialidade"),
                    html.Th("Consultas"),
                    html.Th("Receita Total"),
                    html.Th("Valor Médio")
                ])
            ]),
            html.Tbody(rows)
        ], striped=True, hover=True, responsive=True)
        
        return table
        
    except Exception as e:
        return dbc.Alert(f"Erro ao criar tabela: {str(e)}", color="danger")
