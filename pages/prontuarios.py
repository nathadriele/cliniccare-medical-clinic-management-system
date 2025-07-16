import dash
from dash import html, dcc, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from datetime import datetime
import pandas as pd
from utils.db_manager import db_manager
from components.navbar import create_page_header, create_alert

def create_layout():
    """Cria o layout da página de prontuários eletrônicos"""
    
    return html.Div([
        # Cabeçalho da página
        create_page_header(
            title="Prontuários Eletrônicos",
            subtitle="Gerencie histórico médico e registros de consultas",
            actions=[
                dbc.Button([
                    html.I(className="fas fa-plus me-1"),
                    "Novo Prontuário"
                ], color="primary", id="btn-novo-prontuario"),
                dbc.Button([
                    html.I(className="fas fa-search me-1"),
                    "Buscar Paciente"
                ], color="outline-primary", id="btn-buscar-paciente")
            ]
        ),
        
        # Alertas
        html.Div(id="prontuarios-alerts"),
        
        # Barra de busca e filtros
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id="input-busca-paciente",
                                placeholder="Digite o nome ou CPF do paciente...",
                                type="text"
                            ),
                            dbc.Button([
                                html.I(className="fas fa-search")
                            ], color="outline-primary", id="btn-executar-busca")
                        ])
                    ], md=8),
                    dbc.Col([
                        dcc.Dropdown(
                            id="dropdown-filtro-medico",
                            placeholder="Filtrar por médico",
                            clearable=True
                        )
                    ], md=4)
                ])
            ])
        ], className="mb-4"),
        
        # Conteúdo principal
        dbc.Row([
            # Lista de pacientes
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("👥 Pacientes", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="lista-pacientes")
                    ])
                ])
            ], md=4),
            
            # Detalhes do prontuário
            dbc.Col([
                html.Div(id="detalhes-prontuario")
            ], md=8)
        ]),
        
        # Modal para novo prontuário
        dbc.Modal([
            dbc.ModalHeader([
                dbc.ModalTitle("Novo Registro no Prontuário")
            ]),
            dbc.ModalBody([
                html.Div(id="modal-novo-prontuario-content")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", color="secondary", id="btn-cancelar-prontuario"),
                dbc.Button("Salvar", color="primary", id="btn-salvar-prontuario")
            ])
        ], id="modal-novo-prontuario", size="xl"),
        
        # Store para dados
        dcc.Store(id='store-paciente-selecionado'),
        dcc.Store(id='store-consulta-selecionada')
    ])

@callback(
    Output('dropdown-filtro-medico', 'options'),
    Input('btn-buscar-paciente', 'n_clicks')
)
def update_medicos_options(n_clicks):
    """Atualiza opções de médicos para filtro"""
    
    try:
        medicos = db_manager.get_medicos()
        options = [{'label': medico['nome'], 'value': medico['id']} 
                  for _, medico in medicos.iterrows()]
        return options
    except:
        return []

@callback(
    Output('lista-pacientes', 'children'),
    [Input('btn-executar-busca', 'n_clicks'),
     Input('input-busca-paciente', 'n_submit')],
    [State('input-busca-paciente', 'value'),
     State('dropdown-filtro-medico', 'value')]
)
def update_lista_pacientes(n_clicks, n_submit, busca, medico_id):
    """Atualiza lista de pacientes"""
    
    try:
        # Buscar pacientes
        if busca:
            query = '''
                SELECT DISTINCT p.* FROM pacientes p
                WHERE p.ativo = 1 AND (
                    p.nome LIKE ? OR p.cpf LIKE ?
                )
                ORDER BY p.nome
            '''
            pacientes = db_manager.execute_query(query, (f'%{busca}%', f'%{busca}%'))
        else:
            pacientes = db_manager.get_pacientes()
        
        if pacientes.empty:
            return create_empty_state_pacientes()
        
        # Criar lista de pacientes
        items = []
        for _, paciente in pacientes.iterrows():
            # Contar consultas do paciente
            consultas_count = db_manager.execute_query('''
                SELECT COUNT(*) as total FROM consultas WHERE paciente_id = ?
            ''', (paciente['id'],))
            
            total_consultas = consultas_count.iloc[0]['total']
            
            item = dbc.ListGroupItem([
                dbc.Row([
                    dbc.Col([
                        html.H6(paciente['nome'], className="mb-1"),
                        html.P([
                            html.Small([
                                html.I(className="fas fa-id-card me-1"),
                                paciente['cpf']
                            ], className="text-muted")
                        ], className="mb-1"),
                        html.P([
                            html.Small([
                                html.I(className="fas fa-calendar me-1"),
                                f"{total_consultas} consulta(s)"
                            ], className="text-muted")
                        ], className="mb-0")
                    ], width=True),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-eye")
                        ], color="outline-primary", size="sm",
                        id={'type': 'btn-ver-prontuario', 'index': paciente['id']})
                    ], width="auto")
                ])
            ], action=True, id={'type': 'item-paciente', 'index': paciente['id']})
            
            items.append(item)
        
        return dbc.ListGroup(items)
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar pacientes: {str(e)}", color="danger")

def create_empty_state_pacientes():
    """Cria estado vazio para lista de pacientes"""
    
    return html.Div([
        html.I(className="fas fa-users fa-2x text-muted mb-2"),
        html.P("Nenhum paciente encontrado", className="text-muted"),
        html.P("Use a busca para encontrar pacientes", className="text-muted small")
    ], className="text-center p-4")

@callback(
    [Output('detalhes-prontuario', 'children'),
     Output('store-paciente-selecionado', 'data')],
    Input({'type': 'btn-ver-prontuario', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def show_detalhes_prontuario(n_clicks_list):
    """Mostra detalhes do prontuário do paciente"""
    
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks_list):
        return "", None
    
    # Identificar qual botão foi clicado
    button_id = ctx.triggered[0]['prop_id']
    paciente_id = eval(button_id.split('.')[0])['index']
    
    try:
        # Buscar dados do paciente
        paciente = db_manager.execute_query(
            'SELECT * FROM pacientes WHERE id = ?', (paciente_id,)
        ).iloc[0]
        
        # Buscar consultas do paciente
        consultas = db_manager.execute_query('''
            SELECT c.*, m.nome as medico_nome, m.especialidade,
                   pr.anamnese, pr.exame_fisico, pr.diagnostico, pr.prescricao
            FROM consultas c
            JOIN medicos m ON c.medico_id = m.id
            LEFT JOIN prontuarios pr ON c.id = pr.consulta_id
            WHERE c.paciente_id = ?
            ORDER BY c.data_consulta DESC
        ''', (paciente_id,))
        
        # Criar layout dos detalhes
        content = [
            # Informações do paciente
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-user me-2"),
                        "Informações do Paciente"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P([html.Strong("Nome: "), paciente['nome']]),
                            html.P([html.Strong("CPF: "), paciente['cpf']]),
                            html.P([html.Strong("Data de Nascimento: "), 
                                   paciente['data_nascimento'] or "Não informado"])
                        ], md=6),
                        dbc.Col([
                            html.P([html.Strong("Telefone: "), 
                                   paciente['telefone'] or "Não informado"]),
                            html.P([html.Strong("Email: "), 
                                   paciente['email'] or "Não informado"]),
                            html.P([html.Strong("Convênio: "), 
                                   paciente['convenio'] or "Particular"])
                        ], md=6)
                    ])
                ])
            ], className="mb-4"),
            
            # Histórico de consultas
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col([
                            html.H5([
                                html.I(className="fas fa-history me-2"),
                                "Histórico de Consultas"
                            ], className="mb-0")
                        ], width=True),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-plus me-1"),
                                "Novo Registro"
                            ], color="primary", size="sm", 
                            id="btn-novo-registro-prontuario")
                        ], width="auto")
                    ])
                ]),
                dbc.CardBody([
                    create_historico_consultas(consultas)
                ])
            ])
        ]
        
        return content, paciente_id
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar prontuário: {str(e)}", color="danger"), None

def create_historico_consultas(consultas):
    """Cria histórico de consultas do paciente"""
    
    if consultas.empty:
        return html.Div([
            html.I(className="fas fa-calendar-times fa-2x text-muted mb-2"),
            html.P("Nenhuma consulta registrada", className="text-muted"),
            html.P("Clique em 'Novo Registro' para adicionar", className="text-muted small")
        ], className="text-center p-4")
    
    # Criar timeline de consultas
    timeline_items = []
    
    for _, consulta in consultas.iterrows():
        data_consulta = pd.to_datetime(consulta['data_consulta'])
        
        # Status da consulta
        status_colors = {
            'agendado': 'info',
            'confirmado': 'warning',
            'concluido': 'success',
            'cancelado': 'danger'
        }
        
        status_color = status_colors.get(consulta['status'], 'secondary')
        
        # Conteúdo do prontuário
        prontuario_content = []
        if consulta['anamnese']:
            prontuario_content.append(
                html.Div([
                    html.Strong("Anamnese: "),
                    html.P(consulta['anamnese'], className="mt-1")
                ])
            )
        
        if consulta['exame_fisico']:
            prontuario_content.append(
                html.Div([
                    html.Strong("Exame Físico: "),
                    html.P(consulta['exame_fisico'], className="mt-1")
                ])
            )
        
        if consulta['diagnostico']:
            prontuario_content.append(
                html.Div([
                    html.Strong("Diagnóstico: "),
                    html.P(consulta['diagnostico'], className="mt-1")
                ])
            )
        
        if consulta['prescricao']:
            prontuario_content.append(
                html.Div([
                    html.Strong("Prescrição: "),
                    html.P(consulta['prescricao'], className="mt-1")
                ])
            )
        
        # Item da timeline
        timeline_item = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6([
                            data_consulta.strftime('%d/%m/%Y %H:%M'),
                            dbc.Badge(consulta['status'].title(), 
                                    color=status_color, pill=True, className="ms-2")
                        ]),
                        html.P([
                            html.I(className="fas fa-user-md me-1"),
                            f"{consulta['medico_nome']} - {consulta['especialidade']}"
                        ], className="text-muted mb-2"),
                        
                        # Observações da consulta
                        html.Div([
                            html.Strong("Observações: "),
                            html.P(consulta['observacoes'] or "Nenhuma observação registrada")
                        ]) if consulta['observacoes'] else None,
                        
                        # Conteúdo do prontuário
                        html.Div(prontuario_content) if prontuario_content else html.Div([
                            html.P("Prontuário não preenchido", className="text-muted fst-italic")
                        ])
                    ], width=True),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button([
                                html.I(className="fas fa-edit")
                            ], color="outline-primary", size="sm",
                            id={'type': 'btn-editar-prontuario', 'index': consulta['id']}),
                            dbc.Button([
                                html.I(className="fas fa-print")
                            ], color="outline-secondary", size="sm",
                            id={'type': 'btn-imprimir-prontuario', 'index': consulta['id']})
                        ], size="sm")
                    ], width="auto")
                ])
            ])
        ], className="mb-3 border-start border-primary border-3")
        
        timeline_items.append(timeline_item)
    
    return html.Div(timeline_items)

@callback(
    [Output('modal-novo-prontuario', 'is_open'),
     Output('modal-novo-prontuario-content', 'children')],
    [Input('btn-novo-registro-prontuario', 'n_clicks'),
     Input('btn-cancelar-prontuario', 'n_clicks')],
    [State('modal-novo-prontuario', 'is_open'),
     State('store-paciente-selecionado', 'data')]
)
def toggle_modal_novo_prontuario(n1, n2, is_open, paciente_id):
    """Controla modal de novo prontuário"""
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-novo-registro-prontuario' and paciente_id:
        return True, create_form_novo_prontuario(paciente_id)
    elif button_id == 'btn-cancelar-prontuario':
        return False, ""
    
    return is_open, ""

def create_form_novo_prontuario(paciente_id):
    """Cria formulário para novo registro no prontuário"""
    
    try:
        # Buscar consultas do paciente sem prontuário
        consultas = db_manager.execute_query('''
            SELECT c.id, c.data_consulta, m.nome as medico_nome, m.especialidade
            FROM consultas c
            JOIN medicos m ON c.medico_id = m.id
            LEFT JOIN prontuarios pr ON c.id = pr.consulta_id
            WHERE c.paciente_id = ? AND pr.id IS NULL AND c.status = 'concluido'
            ORDER BY c.data_consulta DESC
        ''', (paciente_id,))
        
        if consultas.empty:
            return dbc.Alert(
                "Não há consultas concluídas sem prontuário para este paciente.",
                color="info"
            )
        
        consultas_options = []
        for _, consulta in consultas.iterrows():
            data_consulta = pd.to_datetime(consulta['data_consulta'])
            label = f"{data_consulta.strftime('%d/%m/%Y %H:%M')} - {consulta['medico_nome']}"
            consultas_options.append({'label': label, 'value': consulta['id']})
        
        return dbc.Form([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Consulta:"),
                    dcc.Dropdown(
                        id='dropdown-consulta-prontuario',
                        options=consultas_options,
                        placeholder="Selecione a consulta"
                    )
                ])
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Anamnese:"),
                    dbc.Textarea(
                        id='textarea-anamnese',
                        placeholder="Histórico da doença atual, sintomas, queixas...",
                        rows=4
                    )
                ])
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Exame Físico:"),
                    dbc.Textarea(
                        id='textarea-exame-fisico',
                        placeholder="Achados do exame físico...",
                        rows=4
                    )
                ])
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Diagnóstico:"),
                    dbc.Textarea(
                        id='textarea-diagnostico',
                        placeholder="Diagnóstico clínico...",
                        rows=3
                    )
                ])
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Prescrição:"),
                    dbc.Textarea(
                        id='textarea-prescricao',
                        placeholder="Medicamentos, orientações, retorno...",
                        rows=4
                    )
                ])
            ])
        ])
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar formulário: {str(e)}", color="danger")

@callback(
    Output('prontuarios-alerts', 'children'),
    Input('btn-salvar-prontuario', 'n_clicks'),
    [State('dropdown-consulta-prontuario', 'value'),
     State('textarea-anamnese', 'value'),
     State('textarea-exame-fisico', 'value'),
     State('textarea-diagnostico', 'value'),
     State('textarea-prescricao', 'value'),
     State('store-paciente-selecionado', 'data')]
)
def salvar_prontuario(n_clicks, consulta_id, anamnese, exame_fisico, diagnostico, prescricao, paciente_id):
    """Salva novo registro no prontuário"""
    
    if not n_clicks or not consulta_id:
        return ""
    
    try:
        # Inserir prontuário
        query = '''
            INSERT INTO prontuarios (paciente_id, consulta_id, anamnese, exame_fisico, diagnostico, prescricao)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        db_manager.execute_insert(query, (
            paciente_id, consulta_id, anamnese or "", 
            exame_fisico or "", diagnostico or "", prescricao or ""
        ))
        
        return create_alert("Prontuário salvo com sucesso!", "success")
        
    except Exception as e:
        return create_alert(f"Erro ao salvar prontuário: {str(e)}", "danger")
