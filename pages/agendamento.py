import dash
from dash import html, dcc, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta, date
import pandas as pd
from utils.db_manager import db_manager
from components.navbar import create_page_header, create_alert

def create_layout():
    """Cria o layout da página de agendamento"""
    
    return html.Div([
        # Cabeçalho da página
        create_page_header(
            title="Agendamento de Consultas",
            subtitle="Gerencie consultas, horários e disponibilidade médica",
            actions=[
                dbc.Button([
                    html.I(className="fas fa-plus me-1"),
                    "Nova Consulta"
                ], color="primary", id="btn-nova-consulta"),
                dbc.Button([
                    html.I(className="fas fa-calendar-week me-1"),
                    "Visualizar Agenda"
                ], color="outline-primary", id="btn-visualizar-agenda")
            ]
        ),
        
        # Alertas
        html.Div(id="agendamento-alerts"),
        
        # Filtros e controles
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Data:"),
                        dcc.DatePickerSingle(
                            id='date-picker-agendamento',
                            date=datetime.now().date(),
                            display_format='DD/MM/YYYY',
                            style={'width': '100%'}
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Médico:"),
                        dcc.Dropdown(
                            id='dropdown-medico-filtro',
                            placeholder="Todos os médicos",
                            clearable=True
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Status:"),
                        dcc.Dropdown(
                            id='dropdown-status-filtro',
                            options=[
                                {'label': 'Todos', 'value': 'todos'},
                                {'label': 'Agendado', 'value': 'agendado'},
                                {'label': 'Confirmado', 'value': 'confirmado'},
                                {'label': 'Concluído', 'value': 'concluido'},
                                {'label': 'Cancelado', 'value': 'cancelado'}
                            ],
                            value='todos'
                        )
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Ações:"),
                        html.Br(),
                        dbc.Button([
                            html.I(className="fas fa-search me-1"),
                            "Filtrar"
                        ], color="outline-primary", size="sm", id="btn-filtrar", type="button")
                    ], md=3)
                ])
            ])
        ], className="mb-4"),
        
        # Lista de consultas
        html.Div(id="lista-consultas"),
        
        # Modal para nova consulta
        dbc.Modal([
            dbc.ModalHeader([
                dbc.ModalTitle("Nova Consulta")
            ]),
            dbc.ModalBody([
                html.Div(id="modal-nova-consulta-content")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", color="secondary", id="btn-cancelar-consulta"),
                dbc.Button("Agendar", color="primary", id="btn-confirmar-consulta")
            ])
        ], id="modal-nova-consulta", size="lg"),
        
        # Modal para editar consulta
        dbc.Modal([
            dbc.ModalHeader([
                dbc.ModalTitle("Editar Consulta")
            ]),
            dbc.ModalBody([
                html.Div(id="modal-editar-consulta-content")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", color="secondary", id="btn-cancelar-edicao"),
                dbc.Button("Salvar", color="primary", id="btn-salvar-edicao")
            ])
        ], id="modal-editar-consulta", size="lg"),

        # Modal para visualizar agenda
        dbc.Modal([
            dbc.ModalHeader([
                dbc.ModalTitle("📅 Visualizar Agenda")
            ]),
            dbc.ModalBody([
                html.Div(id="modal-agenda-content")
            ]),
            dbc.ModalFooter([
                dbc.Button("Fechar", color="secondary", id="btn-fechar-agenda")
            ])
        ], id="modal-visualizar-agenda", size="xl"),

        # Store para dados
        dcc.Store(id='store-consulta-editando')
    ])

@callback(
    Output('dropdown-medico-filtro', 'options'),
    Input('date-picker-agendamento', 'date')
)
def update_medicos_options(selected_date):
    """Atualiza opções de médicos"""
    
    try:
        medicos = db_manager.get_medicos()
        options = [{'label': medico['nome'], 'value': medico['id']} 
                  for _, medico in medicos.iterrows()]
        return options
    except:
        return []

@callback(
    Output('lista-consultas', 'children'),
    [Input('btn-filtrar', 'n_clicks'),
     Input('date-picker-agendamento', 'date')],
    [State('dropdown-medico-filtro', 'value'),
     State('dropdown-status-filtro', 'value')]
)
def update_lista_consultas(n_clicks, selected_date, medico_id, status):
    """Atualiza lista de consultas"""

    try:
        # Se não há data selecionada, usar data atual
        if not selected_date:
            data_consulta = datetime.now().date()
        elif isinstance(selected_date, str):
            data_consulta = datetime.strptime(selected_date, '%Y-%m-%d').date()
        else:
            data_consulta = selected_date

        # Buscar consultas do dia
        consultas = db_manager.get_consultas_periodo(data_consulta, data_consulta)

        # Aplicar filtros
        if medico_id:
            consultas = consultas[consultas['medico_id'] == medico_id]

        if status and status != 'todos':
            consultas = consultas[consultas['status'] == status]

        if consultas.empty:
            return create_empty_state_consultas()

        # Criar cards das consultas
        cards = []
        for _, consulta in consultas.iterrows():
            card = create_consulta_card(consulta)
            cards.append(card)

        return html.Div(cards)

    except Exception as e:
        return dbc.Alert(f"Erro ao carregar consultas: {str(e)}", color="danger")

def create_empty_state_consultas():
    """Cria estado vazio para consultas"""
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className="fas fa-calendar-times fa-3x text-muted mb-3"),
                html.H5("Nenhuma consulta encontrada", className="text-muted"),
                html.P("Não há consultas agendadas para os filtros selecionados.", 
                      className="text-muted"),
                dbc.Button([
                    html.I(className="fas fa-plus me-1"),
                    "Agendar Nova Consulta"
                ], color="primary", id="btn-nova-consulta-empty")
            ], className="text-center p-4")
        ])
    ])

def create_consulta_card(consulta):
    """Cria card individual da consulta"""
    
    data_consulta = pd.to_datetime(consulta['data_consulta'])
    
    # Cores por status
    status_colors = {
        'agendado': 'info',
        'confirmado': 'success',
        'concluido': 'primary',
        'cancelado': 'danger'
    }
    
    status_color = status_colors.get(consulta['status'], 'secondary')
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        html.I(className="fas fa-user me-2"),
                        consulta['paciente_nome']
                    ], className="mb-1"),
                    html.P([
                        html.I(className="fas fa-user-md me-2"),
                        f"{consulta['medico_nome']} - {consulta['especialidade']}"
                    ], className="text-muted mb-1"),
                    html.P([
                        html.I(className="fas fa-clock me-2"),
                        data_consulta.strftime('%H:%M')
                    ], className="text-muted mb-0")
                ], md=6),
                dbc.Col([
                    dbc.Badge(
                        consulta['status'].title(),
                        color=status_color,
                        pill=True,
                        className="mb-2"
                    ),
                    html.P([
                        html.I(className="fas fa-dollar-sign me-1"),
                        f"R$ {consulta['valor']:.2f}"
                    ], className="text-muted mb-0")
                ], md=3),
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button([
                            html.I(className="fas fa-edit")
                        ], color="outline-primary", size="sm", 
                        id={'type': 'btn-editar-consulta', 'index': consulta['id']}),
                        dbc.Button([
                            html.I(className="fas fa-trash")
                        ], color="outline-danger", size="sm",
                        id={'type': 'btn-cancelar-consulta', 'index': consulta['id']})
                    ], size="sm")
                ], md=3, className="text-end")
            ])
        ])
    ], className="mb-3 shadow-sm")

@callback(
    [Output('modal-nova-consulta', 'is_open'),
     Output('modal-nova-consulta-content', 'children')],
    [Input('btn-nova-consulta', 'n_clicks'),
     Input('btn-nova-consulta-empty', 'n_clicks'),
     Input('btn-cancelar-consulta', 'n_clicks')],
    State('modal-nova-consulta', 'is_open'),
    prevent_initial_call=True
)
def toggle_modal_nova_consulta(n1, n2, n3, is_open):
    """Controla modal de nova consulta"""

    ctx = dash.callback_context
    if not ctx.triggered:
        return False, ""

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Apenas botões específicos devem abrir a modal
    if button_id in ['btn-nova-consulta', 'btn-nova-consulta-empty']:
        return True, create_form_nova_consulta()
    elif button_id == 'btn-cancelar-consulta':
        return False, ""

    # Para qualquer outro botão, manter estado atual
    return is_open, ""

def create_form_nova_consulta():
    """Cria formulário para nova consulta"""
    
    try:
        pacientes = db_manager.get_pacientes()
        medicos = db_manager.get_medicos()
        
        pacientes_options = [{'label': p['nome'], 'value': p['id']} 
                           for _, p in pacientes.iterrows()]
        medicos_options = [{'label': f"{m['nome']} - {m['especialidade']}", 'value': m['id']} 
                         for _, m in medicos.iterrows()]
        
        return dbc.Form([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Paciente:"),
                    dcc.Dropdown(
                        id='dropdown-paciente-nova',
                        options=pacientes_options,
                        placeholder="Selecione o paciente"
                    )
                ], md=6),
                dbc.Col([
                    dbc.Label("Médico:"),
                    dcc.Dropdown(
                        id='dropdown-medico-nova',
                        options=medicos_options,
                        placeholder="Selecione o médico"
                    )
                ], md=6)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data:"),
                    dcc.DatePickerSingle(
                        id='date-picker-nova-consulta',
                        date=datetime.now().date(),
                        display_format='DD/MM/YYYY'
                    )
                ], md=4),
                dbc.Col([
                    dbc.Label("Horário:"),
                    dbc.Input(
                        id='input-horario-nova',
                        type='time',
                        value='09:00'
                    )
                ], md=4),
                dbc.Col([
                    dbc.Label("Valor (R$):"),
                    dbc.Input(
                        id='input-valor-nova',
                        type='number',
                        step=0.01,
                        min=0,
                        placeholder="0.00"
                    )
                ], md=4)
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Observações:"),
                    dbc.Textarea(
                        id='textarea-observacoes-nova',
                        placeholder="Observações sobre a consulta...",
                        rows=3
                    )
                ])
            ])
        ])
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar formulário: {str(e)}", color="danger")

@callback(
    Output('agendamento-alerts', 'children'),
    Input('btn-confirmar-consulta', 'n_clicks'),
    [State('dropdown-paciente-nova', 'value'),
     State('dropdown-medico-nova', 'value'),
     State('date-picker-nova-consulta', 'date'),
     State('input-horario-nova', 'value'),
     State('input-valor-nova', 'value'),
     State('textarea-observacoes-nova', 'value')]
)
def agendar_consulta(n_clicks, paciente_id, medico_id, data, horario, valor, observacoes):
    """Agenda nova consulta"""
    
    if not n_clicks:
        return ""
    
    try:
        # Validações
        if not all([paciente_id, medico_id, data, horario]):
            return create_alert("Preencha todos os campos obrigatórios.", "warning")
        
        # Combinar data e horário
        data_consulta = f"{data} {horario}:00"
        
        # Inserir no banco
        query = '''
            INSERT INTO consultas (paciente_id, medico_id, data_consulta, valor, observacoes, status)
            VALUES (?, ?, ?, ?, ?, 'agendado')
        '''
        
        db_manager.execute_insert(query, (
            paciente_id, medico_id, data_consulta, 
            valor or 0, observacoes or ""
        ))
        
        return create_alert("Consulta agendada com sucesso!", "success")
        
    except Exception as e:
        return create_alert(f"Erro ao agendar consulta: {str(e)}", "danger")

# Callback para modal de visualizar agenda
@callback(
    [Output('modal-visualizar-agenda', 'is_open'),
     Output('modal-agenda-content', 'children')],
    [Input('btn-visualizar-agenda', 'n_clicks'),
     Input('btn-fechar-agenda', 'n_clicks')],
    State('modal-visualizar-agenda', 'is_open')
)
def toggle_modal_agenda(btn_visualizar, btn_fechar, is_open):
    """Controla modal de visualizar agenda"""

    ctx = dash.callback_context
    if not ctx.triggered:
        return False, ""

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'btn-visualizar-agenda' and btn_visualizar:
        # Abrir modal e carregar conteúdo da agenda
        agenda_content = criar_conteudo_agenda()
        return True, agenda_content
    elif trigger_id == 'btn-fechar-agenda':
        return False, ""

    return is_open, ""

def criar_conteudo_agenda():
    """Cria o conteúdo da visualização da agenda"""

    try:
        # Buscar consultas dos próximos 7 dias
        data_inicio = datetime.now().date()
        data_fim = data_inicio + timedelta(days=7)

        query = '''
            SELECT
                c.id,
                c.data_consulta,
                c.status,
                c.valor,
                c.observacoes,
                p.nome as paciente_nome,
                p.telefone as paciente_telefone,
                m.nome as medico_nome,
                m.especialidade as medico_especialidade
            FROM consultas c
            JOIN pacientes p ON c.paciente_id = p.id
            JOIN medicos m ON c.medico_id = m.id
            WHERE DATE(c.data_consulta) BETWEEN ? AND ?
            ORDER BY c.data_consulta ASC
        '''

        consultas_df = db_manager.execute_query(query, (data_inicio, data_fim))

        if consultas_df is None or consultas_df.empty:
            return dbc.Alert([
                html.I(className="fas fa-calendar-times me-2"),
                "Nenhuma consulta agendada para os próximos 7 dias."
            ], color="info")

        # Agrupar consultas por data
        consultas_por_data = {}

        for _, consulta in consultas_df.iterrows():
            data_consulta = pd.to_datetime(consulta['data_consulta'])
            data_str = data_consulta.strftime('%Y-%m-%d')
            data_display = data_consulta.strftime('%d/%m/%Y')

            if data_str not in consultas_por_data:
                consultas_por_data[data_str] = {
                    'data_display': data_display,
                    'consultas': []
                }

            consultas_por_data[data_str]['consultas'].append({
                'id': consulta['id'],
                'horario': data_consulta.strftime('%H:%M'),
                'paciente': consulta['paciente_nome'],
                'telefone': consulta['paciente_telefone'],
                'medico': consulta['medico_nome'],
                'especialidade': consulta['medico_especialidade'],
                'status': consulta['status'],
                'valor': consulta['valor'],
                'observacoes': consulta['observacoes']
            })

        # Criar cards para cada dia
        cards_dias = []

        for data_str in sorted(consultas_por_data.keys()):
            dia_info = consultas_por_data[data_str]

            # Determinar cor do header baseado no dia
            data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
            hoje = datetime.now().date()

            if data_obj == hoje:
                header_class = "bg-primary text-white"
                header_text = f"🗓️ Hoje - {dia_info['data_display']}"
            elif data_obj == hoje + timedelta(days=1):
                header_class = "bg-info text-white"
                header_text = f"📅 Amanhã - {dia_info['data_display']}"
            else:
                header_class = "bg-light text-dark"
                header_text = f"📆 {dia_info['data_display']}"

            # Criar lista de consultas do dia
            consultas_cards = []

            for consulta in dia_info['consultas']:
                # Cor do status
                status_colors = {
                    'agendado': 'success',
                    'confirmado': 'primary',
                    'em_andamento': 'warning',
                    'concluido': 'info',
                    'cancelado': 'danger',
                    'faltou': 'secondary'
                }

                status_color = status_colors.get(consulta['status'], 'secondary')

                consulta_card = dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6([
                                    html.I(className="fas fa-clock me-2"),
                                    consulta['horario']
                                ], className="mb-2"),
                                html.P([
                                    html.Strong("Paciente: "),
                                    consulta['paciente']
                                ], className="mb-1"),
                                html.P([
                                    html.Strong("Telefone: "),
                                    consulta['telefone']
                                ], className="mb-1"),
                                html.P([
                                    html.Strong("Médico: "),
                                    f"Dr(a). {consulta['medico']}"
                                ], className="mb-1"),
                                html.P([
                                    html.Strong("Especialidade: "),
                                    consulta['especialidade']
                                ], className="mb-1"),
                                html.P([
                                    html.Strong("Valor: "),
                                    f"R$ {consulta['valor']:.2f}"
                                ], className="mb-1"),
                                html.P([
                                    html.Strong("Observações: "),
                                    consulta['observacoes'] or "Nenhuma"
                                ], className="mb-0")
                            ], md=10),
                            dbc.Col([
                                dbc.Badge(
                                    consulta['status'].replace('_', ' ').title(),
                                    color=status_color,
                                    className="mb-2"
                                )
                            ], md=2, className="text-end")
                        ])
                    ])
                ], className="mb-2", outline=True)

                consultas_cards.append(consulta_card)

            # Card do dia
            dia_card = dbc.Card([
                dbc.CardHeader([
                    html.H5(header_text, className="mb-0")
                ], className=header_class),
                dbc.CardBody(consultas_cards)
            ], className="mb-3")

            cards_dias.append(dia_card)

        return html.Div([
            dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                f"Mostrando agenda dos próximos 7 dias ({len(consultas_df)} consulta(s) encontrada(s))"
            ], color="info", className="mb-3"),
            html.Div(cards_dias)
        ])

    except Exception as e:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Erro ao carregar agenda: {str(e)}"
        ], color="danger")
