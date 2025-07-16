import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from utils.db_manager import db_manager
from components.navbar import create_page_header, create_stats_cards

def create_layout():
    """Cria o layout da página inicial/dashboard"""
    
    return html.Div([
        # Cabeçalho da página
        create_page_header(
            title="Visão Geral",
            subtitle="Visão geral do sistema - Bem-vindo ao ClinicCare"
        ),
        
        # Cards de KPIs
        html.Div(id="kpi-cards"),
        
        # Gráficos principais
        dbc.Row([
            # Gráfico de consultas por período
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📅 Consultas por Período", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-consultas-periodo")
                    ])
                ])
            ], md=8),
            
            # Distribuição por especialidade
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("👨‍⚕️ Por Especialidade", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-especialidades")
                    ])
                ])
            ], md=4)
        ], className="mb-4"),
        
        dbc.Row([
            # Status das consultas
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📊 Status das Consultas", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-status-consultas")
                    ])
                ])
            ], md=6),
            
            # Receita mensal
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("💰 Receita Mensal", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-receita-mensal")
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # Tabela de próximas consultas
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("🕐 Próximas Consultas", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="proximas-consultas")
                    ])
                ])
            ])
        ], className="mb-4"),

        # Gráficos Avançados
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("🔥 Heatmap de Agendamentos por Dia/Hora", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="heatmap-agendamentos")
                    ])
                ])
            ], md=8),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("⏱️ Horários de Pico", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-horarios-pico")
                    ])
                ])
            ], md=4)
        ], className="mb-4"),

        # Timeline de Atendimentos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📈 Timeline de Atendimentos (Últimos 30 dias)", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="timeline-atendimentos")
                    ])
                ])
            ])
        ]),
        
        # Interval para atualização automática
        dcc.Interval(
            id='interval-dashboard',
            interval=30*1000,  # Atualiza a cada 30 segundos
            n_intervals=0
        )
    ])

@callback(
    Output('kpi-cards', 'children'),
    Input('interval-dashboard', 'n_intervals')
)
def update_kpi_cards(n):
    """Atualiza os cards de KPIs"""
    
    try:
        kpis = db_manager.get_kpis_dashboard()
        
        stats = [
            {
                'value': f"{kpis['consultas_mes']:,}",
                'label': 'Consultas este mês',
                'icon': 'fa-calendar-check'
            },
            {
                'value': f"{kpis['taxa_comparecimento']:.1f}%",
                'label': 'Taxa de comparecimento',
                'icon': 'fa-user-check'
            },
            {
                'value': f"R$ {kpis['receita_mes']:,.2f}",
                'label': 'Receita do mês',
                'icon': 'fa-dollar-sign'
            },
            {
                'value': f"{kpis['pacientes_ativos']:,}",
                'label': 'Pacientes ativos',
                'icon': 'fa-users'
            }
        ]
        
        return create_stats_cards(stats)
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar KPIs: {str(e)}", color="danger")

@callback(
    Output('grafico-consultas-periodo', 'figure'),
    Input('interval-dashboard', 'n_intervals')
)
def update_grafico_consultas_periodo(n):
    """Atualiza gráfico de consultas por período"""
    
    try:
        # Últimos 30 dias
        data_fim = datetime.now().date()
        data_inicio = data_fim - timedelta(days=30)
        
        consultas = db_manager.get_consultas_periodo(data_inicio, data_fim)
        
        if consultas.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhuma consulta encontrada",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Agrupar por data
        consultas['data'] = pd.to_datetime(consultas['data_consulta']).dt.date
        consultas_por_dia = consultas.groupby('data').size().reset_index(name='total')
        
        fig = px.line(
            consultas_por_dia,
            x='data',
            y='total',
            title='Consultas nos últimos 30 dias',
            markers=True
        )
        
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Número de Consultas",
            showlegend=False,
            height=300
        )
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erro: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

@callback(
    Output('grafico-especialidades', 'figure'),
    Input('interval-dashboard', 'n_intervals')
)
def update_grafico_especialidades(n):
    """Atualiza gráfico de distribuição por especialidade"""
    
    try:
        data_fim = datetime.now().date()
        data_inicio = data_fim - timedelta(days=30)
        
        consultas = db_manager.get_consultas_periodo(data_inicio, data_fim)
        
        if consultas.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        especialidades = consultas['especialidade'].value_counts()
        
        fig = px.pie(
            values=especialidades.values,
            names=especialidades.index,
            title='Consultas por Especialidade'
        )
        
        fig.update_layout(height=300, showlegend=True)
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erro: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

@callback(
    Output('grafico-status-consultas', 'figure'),
    Input('interval-dashboard', 'n_intervals')
)
def update_grafico_status(n):
    """Atualiza gráfico de status das consultas"""
    
    try:
        data_fim = datetime.now().date()
        data_inicio = data_fim - timedelta(days=30)
        
        consultas = db_manager.get_consultas_periodo(data_inicio, data_fim)
        
        if consultas.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        status_counts = consultas['status'].value_counts()
        
        colors = {
            'agendado': '#17a2b8',
            'confirmado': '#28a745',
            'concluido': '#2c5aa0',
            'cancelado': '#dc3545'
        }
        
        fig = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            color=status_counts.index,
            color_discrete_map=colors,
            title='Status das Consultas'
        )
        
        fig.update_layout(
            xaxis_title="Status",
            yaxis_title="Quantidade",
            showlegend=False,
            height=300
        )
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erro: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

@callback(
    Output('grafico-receita-mensal', 'figure'),
    Input('interval-dashboard', 'n_intervals')
)
def update_grafico_receita(n):
    """Atualiza gráfico de receita mensal"""
    
    try:
        # Últimos 6 meses
        hoje = datetime.now().date()
        meses = []
        receitas = []
        
        for i in range(6):
            mes_atual = hoje.replace(day=1) - timedelta(days=30*i)
            mes_seguinte = (mes_atual.replace(day=28) + timedelta(days=4)).replace(day=1)
            
            consultas_mes = db_manager.execute_query('''
                SELECT COALESCE(SUM(valor), 0) as receita 
                FROM consultas 
                WHERE DATE(data_consulta) >= ? AND DATE(data_consulta) < ?
                AND status = 'concluido'
            ''', (mes_atual, mes_seguinte))
            
            meses.append(mes_atual.strftime('%m/%Y'))
            receitas.append(consultas_mes.iloc[0]['receita'] or 0)
        
        # Inverter para ordem cronológica
        meses.reverse()
        receitas.reverse()
        
        fig = px.bar(
            x=meses,
            y=receitas,
            title='Receita dos Últimos 6 Meses'
        )
        
        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Receita (R$)",
            showlegend=False,
            height=300
        )
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erro: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

@callback(
    Output('proximas-consultas', 'children'),
    Input('interval-dashboard', 'n_intervals')
)
def update_proximas_consultas(n):
    """Atualiza tabela de próximas consultas"""
    
    try:
        hoje = datetime.now().date()
        amanha = hoje + timedelta(days=7)  # Próximos 7 dias
        
        consultas = db_manager.get_consultas_periodo(hoje, amanha)
        
        if consultas.empty:
            return html.P("Nenhuma consulta agendada para os próximos dias.", 
                         className="text-muted text-center p-3")
        
        # Criar tabela
        table_rows = []
        for _, consulta in consultas.iterrows():
            data_consulta = pd.to_datetime(consulta['data_consulta'])
            
            status_color = {
                'agendado': 'info',
                'confirmado': 'success',
                'cancelado': 'danger',
                'concluido': 'primary'
            }.get(consulta['status'], 'secondary')
            
            row = html.Tr([
                html.Td(data_consulta.strftime('%d/%m/%Y %H:%M')),
                html.Td(consulta['paciente_nome']),
                html.Td(consulta['medico_nome']),
                html.Td(consulta['especialidade']),
                html.Td([
                    dbc.Badge(consulta['status'].title(), color=status_color, pill=True)
                ])
            ])
            table_rows.append(row)
        
        table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Data/Hora"),
                    html.Th("Paciente"),
                    html.Th("Médico"),
                    html.Th("Especialidade"),
                    html.Th("Status")
                ])
            ]),
            html.Tbody(table_rows)
        ], striped=True, hover=True, responsive=True, size="sm")
        
        return table
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar consultas: {str(e)}", color="danger")

@callback(
    Output('heatmap-agendamentos', 'figure'),
    Input('interval-dashboard', 'n_intervals')
)
def update_heatmap_agendamentos(n):
    """Atualiza heatmap de agendamentos por dia da semana e hora"""

    try:
        import pandas as pd
        import numpy as np

        # Simular dados de agendamentos por dia da semana e hora
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        horas = [f"{h:02d}:00" for h in range(8, 18)]  # 8h às 17h

        # Criar matriz de dados simulados
        np.random.seed(42)  # Para resultados consistentes
        data = np.random.poisson(3, (len(dias_semana), len(horas)))

        # Adicionar padrões realistas
        for i, dia in enumerate(dias_semana):
            for j, hora in enumerate(horas):
                h = j + 8
                # Mais agendamentos no meio da manhã e tarde
                if 9 <= h <= 11 or 14 <= h <= 16:
                    data[i][j] += np.random.poisson(2)
                # Menos agendamentos no sábado
                if i == 5:
                    data[i][j] = max(0, data[i][j] - 2)

        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=horas,
            y=dias_semana,
            colorscale='Blues',
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>%{x}<br>Agendamentos: %{z}<extra></extra>'
        ))

        fig.update_layout(
            title="Densidade de Agendamentos por Dia e Hora",
            xaxis_title="Horário",
            yaxis_title="Dia da Semana",
            height=300,
            margin=dict(l=80, r=20, t=40, b=40)
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erro: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

@callback(
    Output('grafico-horarios-pico', 'figure'),
    Input('interval-dashboard', 'n_intervals')
)
def update_grafico_horarios_pico(n):
    """Atualiza gráfico de horários de pico"""

    try:
        import pandas as pd
        import numpy as np

        # Simular dados de horários de pico
        horas = [f"{h:02d}:00" for h in range(8, 18)]
        np.random.seed(42)

        # Criar padrão realista de agendamentos por hora
        agendamentos = []
        for i, hora in enumerate(horas):
            h = i + 8
            base = 5
            if 9 <= h <= 11:  # Pico manhã
                base += np.random.poisson(8)
            elif 14 <= h <= 16:  # Pico tarde
                base += np.random.poisson(6)
            elif h == 8 or h >= 17:  # Início e fim do dia
                base += np.random.poisson(2)
            else:
                base += np.random.poisson(4)

            agendamentos.append(base)

        # Identificar horários de pico (acima da média)
        media = np.mean(agendamentos)
        cores = ['#ef4444' if x > media else '#3b82f6' for x in agendamentos]

        fig = go.Figure(data=go.Bar(
            x=horas,
            y=agendamentos,
            marker_color=cores,
            hovertemplate='<b>%{x}</b><br>Agendamentos: %{y}<extra></extra>'
        ))

        # Adicionar linha da média
        fig.add_hline(
            y=media,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Média: {media:.1f}"
        )

        fig.update_layout(
            title="Agendamentos por Horário",
            xaxis_title="Horário",
            yaxis_title="Número de Agendamentos",
            height=300,
            showlegend=False,
            margin=dict(l=40, r=20, t=40, b=40)
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erro: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

@callback(
    Output('timeline-atendimentos', 'figure'),
    Input('interval-dashboard', 'n_intervals')
)
def update_timeline_atendimentos(n):
    """Atualiza timeline de atendimentos dos últimos 30 dias"""

    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta

        # Gerar dados dos últimos 30 dias
        hoje = datetime.now().date()
        datas = [hoje - timedelta(days=i) for i in range(29, -1, -1)]

        np.random.seed(42)

        # Simular diferentes tipos de atendimento
        consultas = []
        emergencias = []
        retornos = []

        for data in datas:
            # Menos atendimentos nos fins de semana
            multiplicador = 0.3 if data.weekday() >= 5 else 1.0

            consultas.append(max(0, int(np.random.poisson(8) * multiplicador)))
            emergencias.append(max(0, int(np.random.poisson(2) * multiplicador)))
            retornos.append(max(0, int(np.random.poisson(4) * multiplicador)))

        fig = go.Figure()

        # Adicionar linhas para cada tipo
        fig.add_trace(go.Scatter(
            x=datas,
            y=consultas,
            mode='lines+markers',
            name='Consultas',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=6)
        ))

        fig.add_trace(go.Scatter(
            x=datas,
            y=emergencias,
            mode='lines+markers',
            name='Emergências',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=6)
        ))

        fig.add_trace(go.Scatter(
            x=datas,
            y=retornos,
            mode='lines+markers',
            name='Retornos',
            line=dict(color='#10b981', width=3),
            marker=dict(size=6)
        ))

        fig.update_layout(
            title="Evolução dos Atendimentos (Últimos 30 dias)",
            xaxis_title="Data",
            yaxis_title="Número de Atendimentos",
            height=400,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erro: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
