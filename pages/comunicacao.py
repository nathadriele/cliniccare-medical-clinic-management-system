import dash
from dash import html, dcc, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import pandas as pd
from utils.db_manager import db_manager
from components.navbar import create_page_header, create_alert

def create_layout():
    """Cria o layout da página de comunicação"""
    
    return html.Div([
        # Cabeçalho da página
        create_page_header(
            title="Comunicação com Pacientes",
            subtitle="Envie lembretes, mensagens e notificações",
            actions=[
                dbc.Button([
                    html.I(className="fas fa-paper-plane me-1"),
                    "Nova Mensagem"
                ], color="primary", id="btn-nova-mensagem"),
                dbc.Button([
                    html.I(className="fas fa-bell me-1"),
                    "Lembrete Automático"
                ], color="outline-primary", id="btn-lembrete-automatico")
            ]
        ),
        
        # Alertas
        html.Div(id="comunicacao-alerts"),
        
        # Estatísticas de comunicação
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📧", className="text-primary mb-2"),
                        html.H5(id="total-mensagens", className="mb-1"),
                        html.P("Mensagens enviadas", className="text-muted mb-0")
                    ])
                ], className="text-center")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("🔔", className="text-warning mb-2"),
                        html.H5(id="total-lembretes", className="mb-1"),
                        html.P("Lembretes ativos", className="text-muted mb-0")
                    ])
                ], className="text-center")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("✅", className="text-success mb-2"),
                        html.H5(id="mensagens-entregues", className="mb-1"),
                        html.P("Taxa de entrega", className="text-muted mb-0")
                    ])
                ], className="text-center")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("⏰", className="text-info mb-2"),
                        html.H5(id="lembretes-hoje", className="mb-1"),
                        html.P("Lembretes hoje", className="text-muted mb-0")
                    ])
                ], className="text-center")
            ], md=3)
        ], className="mb-4"),
        
        # Abas de comunicação
        dbc.Tabs([
            dbc.Tab(label="📧 Mensagens", tab_id="tab-mensagens"),
            dbc.Tab(label="🔔 Lembretes", tab_id="tab-lembretes"),
            dbc.Tab(label="📊 Relatórios", tab_id="tab-relatorios")
        ], id="tabs-comunicacao", active_tab="tab-mensagens"),
        
        # Conteúdo das abas
        html.Div(id="conteudo-tab-comunicacao", className="mt-4"),
        
        # Modal para nova mensagem
        dbc.Modal([
            dbc.ModalHeader([
                dbc.ModalTitle("Nova Mensagem")
            ]),
            dbc.ModalBody([
                html.Div(id="modal-mensagem-content")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", color="secondary", id="btn-cancelar-mensagem"),
                dbc.Button("Enviar", color="primary", id="btn-enviar-mensagem")
            ])
        ], id="modal-nova-mensagem", size="lg"),
        
        # Interval para atualização
        dcc.Interval(
            id='interval-comunicacao',
            interval=60*1000,  # Atualiza a cada minuto
            n_intervals=0
        )
    ])

@callback(
    [Output('total-mensagens', 'children'),
     Output('total-lembretes', 'children'),
     Output('mensagens-entregues', 'children'),
     Output('lembretes-hoje', 'children')],
    Input('interval-comunicacao', 'n_intervals')
)
def update_stats_comunicacao(n):
    """Atualiza estatísticas de comunicação"""
    
    try:
        hoje = datetime.now().date()
        
        # Total de mensagens
        total_msg = db_manager.execute_query('''
            SELECT COUNT(*) as total FROM comunicacao
        ''').iloc[0]['total'] or 0

        # Lembretes ativos
        lembretes_ativos = db_manager.execute_query('''
            SELECT COUNT(*) as total FROM comunicacao
            WHERE tipo = 'lembrete' AND status = 'pendente'
        ''').iloc[0]['total'] or 0

        # Taxa de entrega (simulada)
        entregues = db_manager.execute_query('''
            SELECT COUNT(*) as total FROM comunicacao
            WHERE status = 'enviado'
        ''').iloc[0]['total'] or 0

        taxa_entrega = (entregues / max(total_msg, 1)) * 100 if total_msg > 0 else 0

        # Lembretes de hoje
        lembretes_hoje = db_manager.execute_query('''
            SELECT COUNT(*) as total FROM comunicacao
            WHERE tipo = 'lembrete' AND DATE(data_envio) = ?
        ''', (hoje,)).iloc[0]['total'] or 0
        
        return (
            f"{total_msg:,}",
            f"{lembretes_ativos:,}",
            f"{taxa_entrega:.1f}%",
            f"{lembretes_hoje:,}"
        )
        
    except Exception as e:
        return "0", "0", "0%", "0"

@callback(
    Output('conteudo-tab-comunicacao', 'children'),
    Input('tabs-comunicacao', 'active_tab')
)
def render_tab_content(active_tab):
    """Renderiza conteúdo das abas"""
    
    if active_tab == "tab-mensagens":
        return create_tab_mensagens()
    elif active_tab == "tab-lembretes":
        return create_tab_lembretes()
    elif active_tab == "tab-relatorios":
        return create_tab_relatorios()
    
    return html.Div()

def create_tab_mensagens():
    """Cria conteúdo da aba de mensagens"""
    
    try:
        mensagens = db_manager.execute_query('''
            SELECT c.*, p.nome as paciente_nome
            FROM comunicacao c
            JOIN pacientes p ON c.paciente_id = p.id
            WHERE c.tipo = 'mensagem'
            ORDER BY c.data_criacao DESC
            LIMIT 50
        ''')
        
        if mensagens.empty:
            return create_empty_state_mensagens()
        
        # Criar lista de mensagens
        cards = []
        for _, msg in mensagens.iterrows():
            data_criacao = pd.to_datetime(msg['data_criacao'])
            
            status_color = {
                'pendente': 'warning',
                'enviado': 'success',
                'erro': 'danger'
            }.get(msg['status'], 'secondary')
            
            card = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6([
                                html.I(className="fas fa-user me-2"),
                                msg['paciente_nome']
                            ], className="mb-1"),
                            html.P([
                                html.Strong("Assunto: "),
                                msg['assunto'] or "Sem assunto"
                            ], className="mb-1"),
                            html.P(msg['mensagem'][:100] + "..." if len(msg['mensagem']) > 100 else msg['mensagem'], 
                                  className="text-muted mb-0")
                        ], md=8),
                        dbc.Col([
                            dbc.Badge(msg['status'].title(), color=status_color, pill=True, className="mb-2"),
                            html.P([
                                html.I(className="fas fa-clock me-1"),
                                data_criacao.strftime('%d/%m/%Y %H:%M')
                            ], className="text-muted small mb-0")
                        ], md=4, className="text-end")
                    ])
                ])
            ], className="mb-3")
            
            cards.append(card)
        
        return html.Div(cards)
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar mensagens: {str(e)}", color="danger")

def create_empty_state_mensagens():
    """Estado vazio para mensagens"""
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className="fas fa-envelope fa-3x text-muted mb-3"),
                html.H5("Nenhuma mensagem enviada", className="text-muted"),
                html.P("Comece enviando sua primeira mensagem para os pacientes.", 
                      className="text-muted"),
                dbc.Button([
                    html.I(className="fas fa-plus me-1"),
                    "Enviar Primeira Mensagem"
                ], color="primary", id="btn-primeira-mensagem")
            ], className="text-center p-4")
        ])
    ])

def create_tab_lembretes():
    """Cria conteúdo da aba de lembretes"""
    
    return dbc.Row([
        # Lembretes automáticos
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("🤖 Lembretes Automáticos", className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Lembrar consultas com antecedência de:"),
                                dbc.Select(
                                    id="select-antecedencia",
                                    options=[
                                        {"label": "1 dia", "value": 1},
                                        {"label": "2 dias", "value": 2},
                                        {"label": "3 dias", "value": 3},
                                        {"label": "1 semana", "value": 7}
                                    ],
                                    value=1
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("Horário de envio:"),
                                dbc.Input(
                                    id="input-horario-lembrete",
                                    type="time",
                                    value="09:00"
                                )
                            ], md=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Mensagem padrão:"),
                                dbc.Textarea(
                                    id="textarea-mensagem-padrao",
                                    value="Olá! Este é um lembrete da sua consulta marcada para {data} às {hora}. Clínica ClinicCare.",
                                    rows=3
                                )
                            ])
                        ], className="mb-3"),
                        
                        dbc.Button([
                            html.I(className="fas fa-save me-1"),
                            "Salvar Configurações"
                        ], color="primary", id="btn-salvar-config-lembrete")
                    ])
                ])
            ])
        ], md=6),
        
        # Próximos lembretes
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("📅 Próximos Lembretes", className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id="proximos-lembretes")
                ])
            ])
        ], md=6)
    ])

def create_tab_relatorios():
    """Cria conteúdo da aba de relatórios"""
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("📊 Relatório de Comunicação", className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Período:"),
                                dcc.DatePickerRange(
                                    id='date-range-relatorio-comunicacao',
                                    start_date=(datetime.now() - timedelta(days=30)).date(),
                                    end_date=datetime.now().date(),
                                    display_format='DD/MM/YYYY'
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("Tipo:"),
                                dcc.Dropdown(
                                    id='dropdown-tipo-relatorio',
                                    options=[
                                        {'label': 'Todos', 'value': 'todos'},
                                        {'label': 'Mensagens', 'value': 'mensagem'},
                                        {'label': 'Lembretes', 'value': 'lembrete'}
                                    ],
                                    value='todos'
                                )
                            ], md=6)
                        ], className="mb-3"),
                        
                        dbc.Button([
                            html.I(className="fas fa-chart-bar me-1"),
                            "Gerar Relatório"
                        ], color="primary", id="btn-gerar-relatorio-comunicacao")
                    ])
                ])
            ])
        ])
    ])

@callback(
    [Output('modal-nova-mensagem', 'is_open'),
     Output('modal-mensagem-content', 'children')],
    [Input('btn-nova-mensagem', 'n_clicks'),
     Input('btn-primeira-mensagem', 'n_clicks'),
     Input('btn-cancelar-mensagem', 'n_clicks')],
    State('modal-nova-mensagem', 'is_open')
)
def toggle_modal_mensagem(n1, n2, n3, is_open):
    """Controla modal de nova mensagem"""
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id in ['btn-nova-mensagem', 'btn-primeira-mensagem']:
        return True, create_form_nova_mensagem()
    elif button_id == 'btn-cancelar-mensagem':
        return False, ""
    
    return is_open, ""

def create_form_nova_mensagem():
    """Cria formulário para nova mensagem"""
    
    try:
        pacientes = db_manager.get_pacientes()
        pacientes_options = [{'label': p['nome'], 'value': p['id']} 
                           for _, p in pacientes.iterrows()]
        
        return dbc.Form([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Destinatário:"),
                    dcc.Dropdown(
                        id='dropdown-destinatario',
                        options=pacientes_options,
                        placeholder="Selecione o paciente"
                    )
                ], md=8),
                dbc.Col([
                    dbc.Label("Tipo:"),
                    dcc.Dropdown(
                        id='dropdown-tipo-mensagem',
                        options=[
                            {'label': 'Mensagem', 'value': 'mensagem'},
                            {'label': 'Lembrete', 'value': 'lembrete'},
                            {'label': 'Notificação', 'value': 'notificacao'}
                        ],
                        value='mensagem'
                    )
                ], md=4)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Assunto:"),
                    dbc.Input(
                        id='input-assunto-mensagem',
                        placeholder="Assunto da mensagem"
                    )
                ])
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Mensagem:"),
                    dbc.Textarea(
                        id='textarea-mensagem',
                        placeholder="Digite sua mensagem aqui...",
                        rows=5
                    )
                ])
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Enviar em:"),
                    dcc.Dropdown(
                        id='dropdown-envio-quando',
                        options=[
                            {'label': 'Agora', 'value': 'agora'},
                            {'label': 'Agendar', 'value': 'agendar'}
                        ],
                        value='agora'
                    )
                ], md=6),
                dbc.Col([
                    dbc.Label("Data/Hora (se agendado):"),
                    dbc.Input(
                        id='input-data-agendamento',
                        type='datetime-local',
                        disabled=True
                    )
                ], md=6)
            ])
        ])
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar formulário: {str(e)}", color="danger")

@callback(
    Output('comunicacao-alerts', 'children'),
    Input('btn-enviar-mensagem', 'n_clicks'),
    [State('dropdown-destinatario', 'value'),
     State('dropdown-tipo-mensagem', 'value'),
     State('input-assunto-mensagem', 'value'),
     State('textarea-mensagem', 'value')]
)
def enviar_mensagem(n_clicks, paciente_id, tipo, assunto, mensagem):
    """Envia nova mensagem"""
    
    if not n_clicks:
        return ""
    
    try:
        # Validações
        if not all([paciente_id, mensagem]):
            return create_alert("Selecione o destinatário e digite a mensagem.", "warning")
        
        # Inserir mensagem
        query = '''
            INSERT INTO comunicacao (paciente_id, tipo, assunto, mensagem, data_envio, status)
            VALUES (?, ?, ?, ?, ?, 'enviado')
        '''
        
        db_manager.execute_insert(query, (
            paciente_id, tipo, assunto or "", mensagem, datetime.now()
        ))
        
        return create_alert("Mensagem enviada com sucesso!", "success")
        
    except Exception as e:
        return create_alert(f"Erro ao enviar mensagem: {str(e)}", "danger")
