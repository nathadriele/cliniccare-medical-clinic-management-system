import dash
from dash import html, dcc, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import pandas as pd
from utils.db_manager import db_manager
from components.navbar import create_page_header, create_alert, create_stats_cards

def create_layout():
    """Cria o layout da página financeira"""
    
    return html.Div([
        # Cabeçalho da página
        create_page_header(
            title="Gestão Financeira",
            subtitle="Controle de receitas, despesas e fluxo de caixa",
            actions=[
                dbc.Button([
                    html.I(className="fas fa-plus me-1"),
                    "Nova Receita"
                ], color="success", id="btn-nova-receita"),
                dbc.Button([
                    html.I(className="fas fa-minus me-1"),
                    "Nova Despesa"
                ], color="danger", id="btn-nova-despesa"),
                dbc.Button([
                    html.I(className="fas fa-file-export me-1"),
                    "Relatório"
                ], color="outline-primary", id="btn-relatorio-financeiro")
            ]
        ),
        
        # Alertas
        html.Div(id="financeiro-alerts"),
        
        # Filtros de período
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Período:"),
                        dcc.DatePickerRange(
                            id='date-picker-range-financeiro',
                            start_date=datetime.now().replace(day=1).date(),
                            end_date=datetime.now().date(),
                            display_format='DD/MM/YYYY',
                            style={'width': '100%'}
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Categoria:"),
                        dcc.Dropdown(
                            id='dropdown-categoria-filtro',
                            options=[
                                {'label': 'Todas', 'value': 'todas'},
                                {'label': 'Consultas', 'value': 'consultas'},
                                {'label': 'Medicamentos', 'value': 'medicamentos'},
                                {'label': 'Equipamentos', 'value': 'equipamentos'},
                                {'label': 'Aluguel', 'value': 'aluguel'},
                                {'label': 'Outros', 'value': 'outros'}
                            ],
                            value='todas'
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Status:"),
                        dcc.Dropdown(
                            id='dropdown-status-financeiro',
                            options=[
                                {'label': 'Todos', 'value': 'todos'},
                                {'label': 'Pendente', 'value': 'pendente'},
                                {'label': 'Pago', 'value': 'pago'},
                                {'label': 'Vencido', 'value': 'vencido'}
                            ],
                            value='todos'
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Ações:"),
                        html.Br(),
                        dbc.Button([
                            html.I(className="fas fa-filter me-1"),
                            "Filtrar"
                        ], color="outline-primary", size="sm", id="btn-filtrar-financeiro")
                    ], md=2)
                ])
            ])
        ], className="mb-4"),
        
        # KPIs financeiros
        html.Div(id="kpis-financeiros"),
        
        # Gráficos financeiros
        dbc.Row([
            # Fluxo de caixa
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("💰 Fluxo de Caixa", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-fluxo-caixa")
                    ])
                ])
            ], md=8),
            
            # Receitas vs Despesas
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📊 Receitas vs Despesas", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="grafico-receitas-despesas")
                    ])
                ])
            ], md=4)
        ], className="mb-4"),
        
        # Tabelas de movimentações
        dbc.Row([
            # Receitas
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col([
                                html.H5("💚 Receitas", className="mb-0")
                            ], width=True),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-plus")
                                ], color="success", size="sm", id="btn-add-receita")
                            ], width="auto")
                        ])
                    ]),
                    dbc.CardBody([
                        html.Div(id="tabela-receitas")
                    ])
                ])
            ], md=6),
            
            # Despesas
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col([
                                html.H5("💸 Despesas", className="mb-0")
                            ], width=True),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-plus")
                                ], color="danger", size="sm", id="btn-add-despesa")
                            ], width="auto")
                        ])
                    ]),
                    dbc.CardBody([
                        html.Div(id="tabela-despesas")
                    ])
                ])
            ], md=6)
        ]),
        
        # Modal para nova movimentação
        dbc.Modal([
            dbc.ModalHeader([
                dbc.ModalTitle(id="modal-financeiro-title")
            ]),
            dbc.ModalBody([
                html.Div(id="modal-financeiro-content")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", color="secondary", id="btn-cancelar-financeiro"),
                dbc.Button("Salvar", color="primary", id="btn-salvar-financeiro")
            ])
        ], id="modal-financeiro", size="lg"),
        
        # Store para dados
        dcc.Store(id='store-tipo-movimentacao')
    ])

@callback(
    Output('kpis-financeiros', 'children'),
    [Input('btn-filtrar-financeiro', 'n_clicks'),
     Input('date-picker-range-financeiro', 'start_date'),
     Input('date-picker-range-financeiro', 'end_date')]
)
def update_kpis_financeiros(n_clicks, start_date, end_date):
    """Atualiza KPIs financeiros"""
    
    try:
        # Receitas do período
        receitas = db_manager.execute_query('''
            SELECT COALESCE(SUM(valor), 0) as total FROM financeiro 
            WHERE tipo = 'receita' AND DATE(data_vencimento) BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        # Despesas do período
        despesas = db_manager.execute_query('''
            SELECT COALESCE(SUM(valor), 0) as total FROM financeiro 
            WHERE tipo = 'despesa' AND DATE(data_vencimento) BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        # Receitas pagas
        receitas_pagas = db_manager.execute_query('''
            SELECT COALESCE(SUM(valor), 0) as total FROM financeiro 
            WHERE tipo = 'receita' AND status = 'pago' 
            AND DATE(data_vencimento) BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        # Contas em atraso
        hoje = datetime.now().date()
        contas_vencidas = db_manager.execute_query('''
            SELECT COUNT(*) as total FROM financeiro 
            WHERE status = 'pendente' AND DATE(data_vencimento) < ?
        ''', (hoje,))
        
        total_receitas = receitas.iloc[0]['total'] or 0
        total_despesas = despesas.iloc[0]['total'] or 0
        saldo = total_receitas - total_despesas
        
        stats = [
            {
                'value': f"R$ {total_receitas:,.2f}",
                'label': 'Receitas do período',
                'icon': 'fa-arrow-up'
            },
            {
                'value': f"R$ {total_despesas:,.2f}",
                'label': 'Despesas do período',
                'icon': 'fa-arrow-down'
            },
            {
                'value': f"R$ {saldo:,.2f}",
                'label': 'Saldo do período',
                'icon': 'fa-balance-scale'
            },
            {
                'value': f"{(contas_vencidas.iloc[0]['total'] or 0):,}",
                'label': 'Contas vencidas',
                'icon': 'fa-exclamation-triangle'
            }
        ]
        
        return create_stats_cards(stats)
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar KPIs: {str(e)}", color="danger")

@callback(
    Output('grafico-fluxo-caixa', 'figure'),
    [Input('btn-filtrar-financeiro', 'n_clicks'),
     Input('date-picker-range-financeiro', 'start_date'),
     Input('date-picker-range-financeiro', 'end_date')]
)
def update_grafico_fluxo_caixa(n_clicks, start_date, end_date):
    """Atualiza gráfico de fluxo de caixa"""
    
    try:
        # Buscar movimentações do período
        movimentacoes = db_manager.execute_query('''
            SELECT 
                DATE(data_vencimento) as data,
                tipo,
                SUM(valor) as valor
            FROM financeiro 
            WHERE DATE(data_vencimento) BETWEEN ? AND ?
            GROUP BY DATE(data_vencimento), tipo
            ORDER BY data
        ''', (start_date, end_date))
        
        if movimentacoes.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhuma movimentação encontrada",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Preparar dados para o gráfico
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        receitas_diarias = []
        despesas_diarias = []
        saldo_acumulado = []
        saldo_atual = 0
        
        for data in dates:
            data_str = data.strftime('%Y-%m-%d')
            
            # Receitas do dia
            receita_dia = movimentacoes[
                (movimentacoes['data'] == data_str) & 
                (movimentacoes['tipo'] == 'receita')
            ]['valor'].sum()
            
            # Despesas do dia
            despesa_dia = movimentacoes[
                (movimentacoes['data'] == data_str) & 
                (movimentacoes['tipo'] == 'despesa')
            ]['valor'].sum()
            
            receitas_diarias.append(receita_dia)
            despesas_diarias.append(-despesa_dia)  # Negativo para visualização
            
            saldo_atual += receita_dia - despesa_dia
            saldo_acumulado.append(saldo_atual)
        
        # Criar gráfico
        fig = go.Figure()
        
        # Receitas
        fig.add_trace(go.Bar(
            x=dates,
            y=receitas_diarias,
            name='Receitas',
            marker_color='green',
            opacity=0.7
        ))
        
        # Despesas
        fig.add_trace(go.Bar(
            x=dates,
            y=despesas_diarias,
            name='Despesas',
            marker_color='red',
            opacity=0.7
        ))
        
        # Saldo acumulado
        fig.add_trace(go.Scatter(
            x=dates,
            y=saldo_acumulado,
            mode='lines+markers',
            name='Saldo Acumulado',
            line=dict(color='blue', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Fluxo de Caixa Diário',
            xaxis_title='Data',
            yaxis_title='Valor (R$)',
            yaxis2=dict(
                title='Saldo Acumulado (R$)',
                overlaying='y',
                side='right'
            ),
            barmode='relative',
            height=400,
            showlegend=True
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
    Output('grafico-receitas-despesas', 'figure'),
    [Input('btn-filtrar-financeiro', 'n_clicks'),
     Input('date-picker-range-financeiro', 'start_date'),
     Input('date-picker-range-financeiro', 'end_date')]
)
def update_grafico_receitas_despesas(n_clicks, start_date, end_date):
    """Atualiza gráfico de receitas vs despesas"""
    
    try:
        # Buscar totais por tipo
        totais = db_manager.execute_query('''
            SELECT 
                tipo,
                SUM(valor) as total
            FROM financeiro 
            WHERE DATE(data_vencimento) BETWEEN ? AND ?
            GROUP BY tipo
        ''', (start_date, end_date))
        
        if totais.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Criar gráfico de pizza
        colors = {'receita': '#28a745', 'despesa': '#dc3545'}
        
        fig = px.pie(
            totais,
            values='total',
            names='tipo',
            title='Distribuição Receitas vs Despesas',
            color='tipo',
            color_discrete_map=colors
        )
        
        fig.update_layout(height=400)
        
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
    Output('tabela-receitas', 'children'),
    [Input('btn-filtrar-financeiro', 'n_clicks'),
     Input('date-picker-range-financeiro', 'start_date'),
     Input('date-picker-range-financeiro', 'end_date')]
)
def update_tabela_receitas(n_clicks, start_date, end_date):
    """Atualiza tabela de receitas"""
    
    try:
        receitas = db_manager.execute_query('''
            SELECT * FROM financeiro 
            WHERE tipo = 'receita' AND DATE(data_vencimento) BETWEEN ? AND ?
            ORDER BY data_vencimento DESC
        ''', (start_date, end_date))
        
        if receitas.empty:
            return html.P("Nenhuma receita encontrada", className="text-muted text-center p-3")
        
        # Criar tabela
        rows = []
        for _, receita in receitas.iterrows():
            data_venc = pd.to_datetime(receita['data_vencimento']).strftime('%d/%m/%Y')
            
            status_color = {
                'pendente': 'warning',
                'pago': 'success',
                'vencido': 'danger'
            }.get(receita['status'], 'secondary')
            
            row = html.Tr([
                html.Td(data_venc),
                html.Td(receita['descricao']),
                html.Td(f"R$ {receita['valor']:.2f}"),
                html.Td([
                    dbc.Badge(receita['status'].title(), color=status_color, pill=True)
                ]),
                html.Td([
                    dbc.ButtonGroup([
                        dbc.Button([
                            html.I(className="fas fa-edit")
                        ], color="outline-primary", size="sm",
                        id={'type': 'btn-editar-receita', 'index': receita['id']}),
                        dbc.Button([
                            html.I(className="fas fa-check")
                        ], color="outline-success", size="sm",
                        id={'type': 'btn-pagar-receita', 'index': receita['id']})
                    ], size="sm")
                ])
            ])
            rows.append(row)
        
        table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Data"),
                    html.Th("Descrição"),
                    html.Th("Valor"),
                    html.Th("Status"),
                    html.Th("Ações")
                ])
            ]),
            html.Tbody(rows)
        ], striped=True, hover=True, responsive=True, size="sm")
        
        return table
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar receitas: {str(e)}", color="danger")

@callback(
    Output('tabela-despesas', 'children'),
    [Input('btn-filtrar-financeiro', 'n_clicks'),
     Input('date-picker-range-financeiro', 'start_date'),
     Input('date-picker-range-financeiro', 'end_date')]
)
def update_tabela_despesas(n_clicks, start_date, end_date):
    """Atualiza tabela de despesas"""
    
    try:
        despesas = db_manager.execute_query('''
            SELECT * FROM financeiro 
            WHERE tipo = 'despesa' AND DATE(data_vencimento) BETWEEN ? AND ?
            ORDER BY data_vencimento DESC
        ''', (start_date, end_date))
        
        if despesas.empty:
            return html.P("Nenhuma despesa encontrada", className="text-muted text-center p-3")
        
        # Criar tabela
        rows = []
        for _, despesa in despesas.iterrows():
            data_venc = pd.to_datetime(despesa['data_vencimento']).strftime('%d/%m/%Y')
            
            status_color = {
                'pendente': 'warning',
                'pago': 'success',
                'vencido': 'danger'
            }.get(despesa['status'], 'secondary')
            
            row = html.Tr([
                html.Td(data_venc),
                html.Td(despesa['descricao']),
                html.Td(f"R$ {despesa['valor']:.2f}"),
                html.Td([
                    dbc.Badge(despesa['status'].title(), color=status_color, pill=True)
                ]),
                html.Td([
                    dbc.ButtonGroup([
                        dbc.Button([
                            html.I(className="fas fa-edit")
                        ], color="outline-primary", size="sm",
                        id={'type': 'btn-editar-despesa', 'index': despesa['id']}),
                        dbc.Button([
                            html.I(className="fas fa-check")
                        ], color="outline-success", size="sm",
                        id={'type': 'btn-pagar-despesa', 'index': despesa['id']})
                    ], size="sm")
                ])
            ])
            rows.append(row)
        
        table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Data"),
                    html.Th("Descrição"),
                    html.Th("Valor"),
                    html.Th("Status"),
                    html.Th("Ações")
                ])
            ]),
            html.Tbody(rows)
        ], striped=True, hover=True, responsive=True, size="sm")
        
        return table
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar despesas: {str(e)}", color="danger")

@callback(
    [Output('modal-financeiro', 'is_open'),
     Output('modal-financeiro-title', 'children'),
     Output('modal-financeiro-content', 'children'),
     Output('store-tipo-movimentacao', 'data')],
    [Input('btn-nova-receita', 'n_clicks'),
     Input('btn-nova-despesa', 'n_clicks'),
     Input('btn-add-receita', 'n_clicks'),
     Input('btn-add-despesa', 'n_clicks'),
     Input('btn-cancelar-financeiro', 'n_clicks')],
    State('modal-financeiro', 'is_open')
)
def toggle_modal_financeiro(n1, n2, n3, n4, n5, is_open):
    """Controla modal financeiro"""
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, "", "", None
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id in ['btn-nova-receita', 'btn-add-receita']:
        return True, "Nova Receita", create_form_movimentacao('receita'), 'receita'
    elif button_id in ['btn-nova-despesa', 'btn-add-despesa']:
        return True, "Nova Despesa", create_form_movimentacao('despesa'), 'despesa'
    elif button_id == 'btn-cancelar-financeiro':
        return False, "", "", None
    
    return is_open, "", "", None

def create_form_movimentacao(tipo):
    """Cria formulário para nova movimentação financeira"""
    
    return dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Label("Descrição:"),
                dbc.Input(
                    id='input-descricao-financeiro',
                    placeholder="Descrição da movimentação"
                )
            ], md=8),
            dbc.Col([
                dbc.Label("Valor (R$):"),
                dbc.Input(
                    id='input-valor-financeiro',
                    type='number',
                    step=0.01,
                    min=0,
                    placeholder="0.00"
                )
            ], md=4)
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Label("Data de Vencimento:"),
                dcc.DatePickerSingle(
                    id='date-picker-vencimento',
                    date=datetime.now().date(),
                    display_format='DD/MM/YYYY'
                )
            ], md=4),
            dbc.Col([
                dbc.Label("Categoria:"),
                dcc.Dropdown(
                    id='dropdown-categoria-financeiro',
                    options=[
                        {'label': 'Consultas', 'value': 'consultas'},
                        {'label': 'Medicamentos', 'value': 'medicamentos'},
                        {'label': 'Equipamentos', 'value': 'equipamentos'},
                        {'label': 'Aluguel', 'value': 'aluguel'},
                        {'label': 'Outros', 'value': 'outros'}
                    ],
                    placeholder="Selecione a categoria"
                )
            ], md=4),
            dbc.Col([
                dbc.Label("Status:"),
                dcc.Dropdown(
                    id='dropdown-status-movimentacao',
                    options=[
                        {'label': 'Pendente', 'value': 'pendente'},
                        {'label': 'Pago', 'value': 'pago'}
                    ],
                    value='pendente'
                )
            ], md=4)
        ])
    ])

@callback(
    Output('financeiro-alerts', 'children'),
    Input('btn-salvar-financeiro', 'n_clicks'),
    [State('input-descricao-financeiro', 'value'),
     State('input-valor-financeiro', 'value'),
     State('date-picker-vencimento', 'date'),
     State('dropdown-categoria-financeiro', 'value'),
     State('dropdown-status-movimentacao', 'value'),
     State('store-tipo-movimentacao', 'data')]
)
def salvar_movimentacao_financeira(n_clicks, descricao, valor, data_vencimento, categoria, status, tipo):
    """Salva nova movimentação financeira"""
    
    if not n_clicks or not tipo:
        return ""
    
    try:
        # Validações
        if not all([descricao, valor, data_vencimento]):
            return create_alert("Preencha todos os campos obrigatórios.", "warning")
        
        # Inserir no banco
        query = '''
            INSERT INTO financeiro (tipo, descricao, valor, data_vencimento, categoria, status)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        db_manager.execute_insert(query, (
            tipo, descricao, valor, data_vencimento, 
            categoria or 'outros', status or 'pendente'
        ))
        
        tipo_label = "Receita" if tipo == 'receita' else "Despesa"
        return create_alert(f"{tipo_label} cadastrada com sucesso!", "success")
        
    except Exception as e:
        return create_alert(f"Erro ao salvar movimentação: {str(e)}", "danger")
