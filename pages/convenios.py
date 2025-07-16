#!/usr/bin/env python3
"""
Página de Gestão de Convênios
Sistema para controle de planos de saúde e faturamento
"""

import dash
from dash import dcc, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px

from utils.db_manager import db_manager

# Layout da página
def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("🏥 Gestão de Convênios", className="mb-4"),
                
                # KPIs de Convênios
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("15", className="text-primary mb-0"),
                                html.P("Convênios Ativos", className="text-muted mb-0")
                            ])
                        ], className="text-center")
                    ], md=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("R$ 45.680", className="text-success mb-0"),
                                html.P("Faturamento Mensal", className="text-muted mb-0")
                            ])
                        ], className="text-center")
                    ], md=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("R$ 12.340", className="text-warning mb-0"),
                                html.P("Pendente Recebimento", className="text-muted mb-0")
                            ])
                        ], className="text-center")
                    ], md=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("92%", className="text-info mb-0"),
                                html.P("Taxa de Aprovação", className="text-muted mb-0")
                            ])
                        ], className="text-center")
                    ], md=3)
                ], className="mb-4"),
                
                # Formulário de Novo Convênio
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("➕ Cadastrar Novo Convênio", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Nome do Convênio:"),
                                dbc.Input(
                                    id="nome-convenio",
                                    placeholder="Ex: Unimed, Bradesco Saúde...",
                                    className="mb-3"
                                )
                            ], md=4),
                            
                            dbc.Col([
                                dbc.Label("CNPJ:"),
                                dbc.Input(
                                    id="cnpj-convenio",
                                    placeholder="00.000.000/0000-00",
                                    className="mb-3"
                                )
                            ], md=3),
                            
                            dbc.Col([
                                dbc.Label("Telefone:"),
                                dbc.Input(
                                    id="telefone-convenio",
                                    placeholder="(11) 0000-0000",
                                    className="mb-3"
                                )
                            ], md=3),
                            
                            dbc.Col([
                                dbc.Label("Status:"),
                                dcc.Dropdown(
                                    id="status-convenio",
                                    options=[
                                        {'label': '✅ Ativo', 'value': 'ativo'},
                                        {'label': '⏸️ Suspenso', 'value': 'suspenso'},
                                        {'label': '❌ Inativo', 'value': 'inativo'}
                                    ],
                                    value='ativo',
                                    className="mb-3"
                                )
                            ], md=2)
                        ]),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Valor Consulta:"),
                                dbc.Input(
                                    id="valor-consulta-convenio",
                                    placeholder="R$ 0,00",
                                    type="number",
                                    step=0.01,
                                    className="mb-3"
                                )
                            ], md=3),
                            
                            dbc.Col([
                                dbc.Label("Prazo Pagamento (dias):"),
                                dbc.Input(
                                    id="prazo-pagamento-convenio",
                                    placeholder="30",
                                    type="number",
                                    className="mb-3"
                                )
                            ], md=3),
                            
                            dbc.Col([
                                dbc.Label("Taxa Administração (%):"),
                                dbc.Input(
                                    id="taxa-admin-convenio",
                                    placeholder="5.0",
                                    type="number",
                                    step=0.1,
                                    className="mb-3"
                                )
                            ], md=3),
                            
                            dbc.Col([
                                dbc.Label(" "),
                                dbc.Button(
                                    "💾 Salvar Convênio",
                                    id="btn-salvar-convenio",
                                    color="success",
                                    className="d-block"
                                )
                            ], md=3)
                        ])
                    ])
                ], className="mb-4"),
                
                # Lista de Convênios
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📋 Convênios Cadastrados", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="tabela-convenios")
                    ])
                ], className="mb-4"),
                
                # Gráficos de Análise
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H5("📊 Faturamento por Convênio", className="mb-0")
                            ]),
                            dbc.CardBody([
                                dcc.Graph(id="grafico-faturamento-convenios")
                            ])
                        ])
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H5("📈 Evolução de Consultas", className="mb-0")
                            ]),
                            dbc.CardBody([
                                dcc.Graph(id="grafico-evolucao-consultas")
                            ])
                        ])
                    ], md=6)
                ], className="mb-4"),
                
                # Relatório de Pendências
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("⏰ Pendências de Pagamento", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="tabela-pendencias")
                    ])
                ])
            ])
        ])
    ], fluid=True)

# Callbacks
@callback(
    Output('tabela-convenios', 'children'),
    Input('tabela-convenios', 'id')
)
def load_convenios_table(trigger):
    """Carrega tabela de convênios"""
    
    # Dados simulados de convênios
    convenios_data = [
        {
            'id': 1,
            'nome': 'Unimed São Paulo',
            'cnpj': '12.345.678/0001-90',
            'telefone': '(11) 3456-7890',
            'valor_consulta': 120.00,
            'prazo_pagamento': 30,
            'taxa_admin': 5.0,
            'status': 'ativo'
        },
        {
            'id': 2,
            'nome': 'Bradesco Saúde',
            'cnpj': '98.765.432/0001-10',
            'telefone': '(11) 2345-6789',
            'valor_consulta': 110.00,
            'prazo_pagamento': 45,
            'taxa_admin': 4.5,
            'status': 'ativo'
        },
        {
            'id': 3,
            'nome': 'SulAmérica Saúde',
            'cnpj': '11.222.333/0001-44',
            'telefone': '(11) 1234-5678',
            'valor_consulta': 115.00,
            'prazo_pagamento': 30,
            'taxa_admin': 5.5,
            'status': 'suspenso'
        }
    ]
    
    df = pd.DataFrame(convenios_data)
    
    # Criar badges de status
    def create_status_badge(status):
        if status == 'ativo':
            return html.Span("✅ Ativo", className="badge bg-success")
        elif status == 'suspenso':
            return html.Span("⏸️ Suspenso", className="badge bg-warning")
        else:
            return html.Span("❌ Inativo", className="badge bg-danger")
    
    # Criar tabela
    table_rows = []
    for _, row in df.iterrows():
        table_row = html.Tr([
            html.Td(row['nome']),
            html.Td(row['cnpj']),
            html.Td(row['telefone']),
            html.Td(f"R$ {row['valor_consulta']:.2f}"),
            html.Td(f"{row['prazo_pagamento']} dias"),
            html.Td(f"{row['taxa_admin']:.1f}%"),
            html.Td(create_status_badge(row['status'])),
            html.Td([
                dbc.ButtonGroup([
                    dbc.Button("✏️", color="primary", size="sm", outline=True),
                    dbc.Button("🗑️", color="danger", size="sm", outline=True)
                ])
            ])
        ])
        table_rows.append(table_row)
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Convênio"),
                html.Th("CNPJ"),
                html.Th("Telefone"),
                html.Th("Valor Consulta"),
                html.Th("Prazo Pagto"),
                html.Th("Taxa Admin"),
                html.Th("Status"),
                html.Th("Ações")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, bordered=True, hover=True, responsive=True)
    
    return table

@callback(
    Output('grafico-faturamento-convenios', 'figure'),
    Input('grafico-faturamento-convenios', 'id')
)
def update_faturamento_chart(trigger):
    """Atualiza gráfico de faturamento por convênio"""
    
    # Dados simulados
    convenios = ['Unimed', 'Bradesco', 'SulAmérica', 'Amil', 'Porto Seguro']
    faturamento = [15680, 12340, 8950, 6780, 4230]
    
    fig = go.Figure(data=[
        go.Bar(
            x=convenios,
            y=faturamento,
            marker_color=['#1e40af', '#059669', '#d97706', '#dc2626', '#7c3aed'],
            text=[f'R$ {v:,.0f}' for v in faturamento],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Faturamento Mensal por Convênio",
        xaxis_title="Convênios",
        yaxis_title="Faturamento (R$)",
        height=350,
        showlegend=False
    )
    
    return fig

@callback(
    Output('grafico-evolucao-consultas', 'figure'),
    Input('grafico-evolucao-consultas', 'id')
)
def update_evolucao_chart(trigger):
    """Atualiza gráfico de evolução de consultas"""
    
    import numpy as np
    
    # Dados simulados dos últimos 6 meses
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
    
    fig = go.Figure()
    
    # Unimed
    fig.add_trace(go.Scatter(
        x=meses,
        y=[45, 52, 48, 61, 58, 65],
        mode='lines+markers',
        name='Unimed',
        line=dict(color='#1e40af', width=3)
    ))
    
    # Bradesco
    fig.add_trace(go.Scatter(
        x=meses,
        y=[38, 42, 45, 48, 52, 55],
        mode='lines+markers',
        name='Bradesco',
        line=dict(color='#059669', width=3)
    ))
    
    # SulAmérica
    fig.add_trace(go.Scatter(
        x=meses,
        y=[25, 28, 32, 30, 35, 38],
        mode='lines+markers',
        name='SulAmérica',
        line=dict(color='#d97706', width=3)
    ))
    
    fig.update_layout(
        title="Evolução de Consultas por Convênio",
        xaxis_title="Mês",
        yaxis_title="Número de Consultas",
        height=350,
        hovermode='x unified'
    )
    
    return fig

@callback(
    Output('tabela-pendencias', 'children'),
    Input('tabela-pendencias', 'id')
)
def load_pendencias_table(trigger):
    """Carrega tabela de pendências"""
    
    # Dados simulados de pendências
    pendencias_data = [
        {
            'convenio': 'Unimed São Paulo',
            'mes_referencia': 'Mai/2025',
            'consultas': 65,
            'valor_bruto': 7800.00,
            'taxa_admin': 390.00,
            'valor_liquido': 7410.00,
            'vencimento': '15/07/2025',
            'status': 'Vencido'
        },
        {
            'convenio': 'Bradesco Saúde',
            'mes_referencia': 'Jun/2025',
            'consultas': 55,
            'valor_bruto': 6050.00,
            'taxa_admin': 272.25,
            'valor_liquido': 5777.75,
            'vencimento': '30/07/2025',
            'status': 'Pendente'
        }
    ]
    
    df = pd.DataFrame(pendencias_data)
    
    # Criar badges de status
    def create_status_badge(status):
        if status == 'Vencido':
            return html.Span("🔴 Vencido", className="badge bg-danger")
        elif status == 'Pendente':
            return html.Span("🟡 Pendente", className="badge bg-warning")
        else:
            return html.Span("🟢 Pago", className="badge bg-success")
    
    # Criar tabela
    table_rows = []
    for _, row in df.iterrows():
        table_row = html.Tr([
            html.Td(row['convenio']),
            html.Td(row['mes_referencia']),
            html.Td(row['consultas']),
            html.Td(f"R$ {row['valor_bruto']:,.2f}"),
            html.Td(f"R$ {row['taxa_admin']:,.2f}"),
            html.Td(f"R$ {row['valor_liquido']:,.2f}"),
            html.Td(row['vencimento']),
            html.Td(create_status_badge(row['status'])),
            html.Td([
                dbc.Button("📧 Cobrar", color="warning", size="sm", outline=True)
            ])
        ])
        table_rows.append(table_row)
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Convênio"),
                html.Th("Mês Ref."),
                html.Th("Consultas"),
                html.Th("Valor Bruto"),
                html.Th("Taxa Admin"),
                html.Th("Valor Líquido"),
                html.Th("Vencimento"),
                html.Th("Status"),
                html.Th("Ação")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, bordered=True, hover=True, responsive=True)
    
    return table
