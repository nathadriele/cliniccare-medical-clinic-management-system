#!/usr/bin/env python3
"""
Página de Gestão de Médicos - CRUD Completo
Sistema para cadastro, edição, listagem e exclusão de médicos
"""

import dash
from dash import dcc, html, Input, Output, State, callback, dash_table, ALL
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, date
import json

from utils.db_manager import db_manager
from utils.relational_checks import integrity_checker, validate_doctor, can_delete_doctor

def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("👨‍⚕️ Gestão de Médicos", className="mb-4"),
                
                dbc.Button(
                    "➕ Novo Médico",
                    id="btn-novo-medico",
                    color="success",
                    className="mb-3"
                )
            ])
        ]),
        
        # Filtros e busca
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("🔍 Buscar Médico:"),
                                dbc.Input(
                                    id="search-medico",
                                    placeholder="Nome, CRM ou especialidade...",
                                    debounce=True
                                )
                            ], md=6),
                            
                            dbc.Col([
                                dbc.Label("🏥 Especialidade:"),
                                dcc.Dropdown(
                                    id="filter-especialidade-medico",
                                    placeholder="Todas as especialidades"
                                )
                            ], md=3),
                            
                            dbc.Col([
                                dbc.Label(" "),
                                dbc.Button(
                                    "🔄 Atualizar",
                                    id="btn-refresh-medicos",
                                    color="primary",
                                    outline=True,
                                    className="d-block"
                                )
                            ], md=3)
                        ])
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # Tabela de médicos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📋 Lista de Médicos", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="tabela-medicos")
                    ])
                ])
            ])
        ]),
        
        # Modal para cadastro/edição
        dbc.Modal([
            dbc.ModalHeader([
                html.H4(id="modal-medico-title")
            ]),
            dbc.ModalBody([
                # Alertas
                html.Div(id="alert-medico"),
                
                # Formulário
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Nome Completo *:"),
                            dbc.Input(
                                id="input-nome-medico",
                                placeholder="Nome completo do médico",
                                required=True
                            )
                        ], md=8),
                        
                        dbc.Col([
                            dbc.Label("CRM *:"),
                            dbc.Input(
                                id="input-crm-medico",
                                placeholder="CRM/UF 123456",
                                required=True
                            )
                        ], md=4)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Especialidade *:"),
                            dcc.Dropdown(
                                id="input-especialidade-medico",
                                options=[
                                    {'label': 'Cardiologia', 'value': 'Cardiologia'},
                                    {'label': 'Dermatologia', 'value': 'Dermatologia'},
                                    {'label': 'Endocrinologia', 'value': 'Endocrinologia'},
                                    {'label': 'Gastroenterologia', 'value': 'Gastroenterologia'},
                                    {'label': 'Ginecologia', 'value': 'Ginecologia'},
                                    {'label': 'Neurologia', 'value': 'Neurologia'},
                                    {'label': 'Oftalmologia', 'value': 'Oftalmologia'},
                                    {'label': 'Ortopedia', 'value': 'Ortopedia'},
                                    {'label': 'Pediatria', 'value': 'Pediatria'},
                                    {'label': 'Psiquiatria', 'value': 'Psiquiatria'},
                                    {'label': 'Clínica Geral', 'value': 'Clínica Geral'},
                                    {'label': 'Outra', 'value': 'Outra'}
                                ],
                                placeholder="Selecione a especialidade",
                                searchable=True
                            )
                        ], md=6),
                        
                        dbc.Col([
                            dbc.Label("Especialidade Personalizada:"),
                            dbc.Input(
                                id="input-especialidade-custom-medico",
                                placeholder="Digite se selecionou 'Outra'"
                            )
                        ], md=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Telefone *:"),
                            dbc.Input(
                                id="input-telefone-medico",
                                placeholder="(11) 99999-9999",
                                required=True
                            )
                        ], md=6),
                        
                        dbc.Col([
                            dbc.Label("Email:"),
                            dbc.Input(
                                id="input-email-medico",
                                type="email",
                                placeholder="email@exemplo.com"
                            )
                        ], md=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Valor Consulta (R$):"),
                            dbc.Input(
                                id="input-valor-consulta-medico",
                                type="number",
                                step=0.01,
                                placeholder="150.00"
                            )
                        ], md=4),
                        
                        dbc.Col([
                            dbc.Label("Duração Consulta (min):"),
                            dbc.Input(
                                id="input-duracao-consulta-medico",
                                type="number",
                                placeholder="30",
                                value=30
                            )
                        ], md=4),
                        
                        dbc.Col([
                            dbc.Label("Status:"),
                            dcc.Dropdown(
                                id="input-status-medico",
                                options=[
                                    {'label': '✅ Ativo', 'value': 1},
                                    {'label': '❌ Inativo', 'value': 0}
                                ],
                                value=1
                            )
                        ], md=4)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Horário de Atendimento:"),
                            dbc.Textarea(
                                id="input-horario-medico",
                                placeholder="Ex: Segunda a Sexta: 08:00 às 18:00",
                                rows=2
                            )
                        ], md=8),
                        
                        dbc.Col([
                            dbc.Label("Convênios Aceitos:"),
                            dbc.Textarea(
                                id="input-convenios-medico",
                                placeholder="Unimed, Bradesco, SulAmérica...",
                                rows=2
                            )
                        ], md=4)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Observações:"),
                            dbc.Textarea(
                                id="input-observacoes-medico",
                                placeholder="Informações adicionais sobre o médico",
                                rows=3
                            )
                        ])
                    ])
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "💾 Salvar",
                    id="btn-salvar-medico",
                    color="success",
                    className="me-2"
                ),
                dbc.Button(
                    "🧹 Limpar",
                    id="btn-limpar-medico",
                    color="secondary",
                    outline=True,
                    className="me-2"
                ),
                dbc.Button(
                    "❌ Cancelar",
                    id="btn-cancelar-medico",
                    color="danger",
                    outline=True
                )
            ])
        ], id="modal-medico", size="lg", is_open=False),
        
        # Modal de confirmação de exclusão
        dbc.Modal([
            dbc.ModalHeader("⚠️ Confirmar Exclusão"),
            dbc.ModalBody([
                html.Div(id="confirm-delete-message-medico")
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "🗑️ Confirmar Exclusão",
                    id="btn-confirm-delete-medico",
                    color="danger",
                    className="me-2"
                ),
                dbc.Button(
                    "❌ Cancelar",
                    id="btn-cancel-delete-medico",
                    color="secondary"
                )
            ])
        ], id="modal-confirm-delete-medico", is_open=False),
        
        # Stores para dados
        dcc.Store(id='medico-edit-id', data=None),
        dcc.Store(id='medico-delete-id', data=None),
        dcc.Store(id='medicos-data', data=[]),
        
        # Toast para notificações
        html.Div(id="toast-container-medicos")
        
    ], fluid=True)

# Callback para carregar especialidades no filtro
@callback(
    Output('filter-especialidade-medico', 'options'),
    Input('filter-especialidade-medico', 'id')
)
def load_especialidades_filter(trigger):
    """Carrega especialidades para o filtro"""
    try:
        especialidades = db_manager.execute_query('''
            SELECT DISTINCT especialidade FROM medicos 
            WHERE especialidade IS NOT NULL 
            ORDER BY especialidade
        ''')
        
        options = [{'label': 'Todas', 'value': 'todas'}]
        
        for _, row in especialidades.iterrows():
            options.append({
                'label': row['especialidade'],
                'value': row['especialidade']
            })
        
        return options
        
    except Exception:
        return [{'label': 'Todas', 'value': 'todas'}]

# Callback para carregar dados dos médicos
@callback(
    Output('medicos-data', 'data'),
    [Input('btn-refresh-medicos', 'n_clicks'),
     Input('search-medico', 'value'),
     Input('filter-especialidade-medico', 'value')],
    prevent_initial_call=False
)
def load_medicos_data(refresh_clicks, search_term, especialidade_filter):
    """Carrega dados dos médicos com filtros"""
    try:
        # Query base
        query = '''
            SELECT 
                id, nome, crm, especialidade, telefone, email,
                valor_consulta, duracao_consulta, horario_atendimento,
                convenios_aceitos, observacoes, ativo, data_cadastro
            FROM medicos
            WHERE 1=1
        '''
        params = []
        
        # Filtro por especialidade
        if especialidade_filter and especialidade_filter != 'todas':
            query += ' AND especialidade = ?'
            params.append(especialidade_filter)
        
        # Filtro por busca
        if search_term:
            query += ' AND (nome LIKE ? OR crm LIKE ? OR especialidade LIKE ?)'
            search_param = f'%{search_term}%'
            params.extend([search_param, search_param, search_param])
        
        query += ' ORDER BY nome'
        
        df = db_manager.execute_query(query, params)
        
        if df.empty:
            return []
        
        # Formatar dados para exibição
        medicos = []
        for _, row in df.iterrows():
            medico = {
                'id': row['id'],
                'nome': row['nome'],
                'crm': row['crm'],
                'especialidade': row['especialidade'],
                'telefone': row['telefone'],
                'email': row['email'] or '',
                'valor_consulta': row['valor_consulta'] or 0,
                'duracao_consulta': row['duracao_consulta'] or 30,
                'horario_atendimento': row['horario_atendimento'] or '',
                'convenios_aceitos': row['convenios_aceitos'] or '',
                'observacoes': row['observacoes'] or '',
                'ativo': row['ativo'],
                'data_cadastro': row['data_cadastro']
            }
            medicos.append(medico)
        
        return medicos
        
    except Exception as e:
        print(f"Erro ao carregar médicos: {e}")
        return []

# Callback para renderizar tabela
@callback(
    Output('tabela-medicos', 'children'),
    Input('medicos-data', 'data')
)
def render_medicos_table(medicos_data):
    """Renderiza tabela de médicos"""
    if not medicos_data:
        return dbc.Alert("Nenhum médico encontrado.", color="info", className="text-center")

    # Criar linhas da tabela
    table_rows = []
    for index, medico in enumerate(medicos_data, 1):  # Começar numeração em 1
        # Status badge
        status_badge = html.Span(
            "✅ Ativo" if medico['ativo'] else "❌ Inativo",
            className=f"badge bg-{'success' if medico['ativo'] else 'danger'}"
        )

        # Valor da consulta
        valor_display = f"R$ {medico['valor_consulta']:.2f}" if medico['valor_consulta'] else "Não informado"

        # Botões de ação
        action_buttons = dbc.ButtonGroup([
            dbc.Button(
                "✏️",
                id={'type': 'btn-edit-medico', 'index': medico['id']},
                color="primary",
                size="sm",
                title="Editar médico"
            ),
            dbc.Button(
                "🗑️",
                id={'type': 'btn-delete-medico', 'index': medico['id']},
                color="danger",
                size="sm",
                title="Excluir médico"
            )
        ])

        row = html.Tr([
            html.Td(index),  # ID sequencial na interface
            html.Td(medico['nome']),
            html.Td(medico['crm']),
            html.Td(medico['especialidade']),
            html.Td(medico['telefone']),
            html.Td(valor_display),
            html.Td(status_badge),
            html.Td(medico['data_cadastro'][:10] if medico['data_cadastro'] else ''),
            html.Td(action_buttons)
        ])
        table_rows.append(row)

    # Tabela completa
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("ID"),
                html.Th("Nome Completo"),
                html.Th("CRM"),
                html.Th("Especialidade"),
                html.Th("Telefone"),
                html.Th("Valor Consulta"),
                html.Th("Status"),
                html.Th("Cadastro"),
                html.Th("Ações")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, bordered=True, hover=True, responsive=True)

    return table

# Callback para abrir modal de novo médico
@callback(
    [Output('modal-medico', 'is_open'),
     Output('modal-medico-title', 'children'),
     Output('medico-edit-id', 'data')],
    [Input('btn-novo-medico', 'n_clicks'),
     Input('btn-cancelar-medico', 'n_clicks')],
    [State('modal-medico', 'is_open')],
    prevent_initial_call=True
)
def toggle_modal_novo_medico(novo_clicks, cancelar_clicks, is_open):
    """Controla abertura/fechamento do modal para novo médico"""
    ctx = dash.callback_context

    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'btn-novo-medico':
            return True, "➕ Novo Médico", None
        elif button_id == 'btn-cancelar-medico':
            return False, "", None

    return is_open, "", None

# Callback para editar médico
@callback(
    [Output('modal-medico', 'is_open', allow_duplicate=True),
     Output('modal-medico-title', 'children', allow_duplicate=True),
     Output('medico-edit-id', 'data', allow_duplicate=True),
     Output('input-nome-medico', 'value'),
     Output('input-crm-medico', 'value'),
     Output('input-especialidade-medico', 'value'),
     Output('input-especialidade-custom-medico', 'value'),
     Output('input-telefone-medico', 'value'),
     Output('input-email-medico', 'value'),
     Output('input-valor-consulta-medico', 'value'),
     Output('input-duracao-consulta-medico', 'value'),
     Output('input-horario-medico', 'value'),
     Output('input-convenios-medico', 'value'),
     Output('input-status-medico', 'value'),
     Output('input-observacoes-medico', 'value')],
    Input({'type': 'btn-edit-medico', 'index': ALL}, 'n_clicks'),
    [State('medicos-data', 'data')],
    prevent_initial_call=True
)
def edit_medico(edit_clicks, medicos_data):
    """Abre modal para edição de médico"""
    ctx = dash.callback_context

    if not ctx.triggered or not any(edit_clicks):
        return dash.no_update

    # Identificar qual botão foi clicado
    button_id = ctx.triggered[0]['prop_id']
    medico_id = eval(button_id.split('.')[0])['index']

    # Encontrar dados do médico
    medico = next((m for m in medicos_data if m['id'] == medico_id), None)

    if not medico:
        return dash.no_update

    # Verificar se é especialidade personalizada
    especialidades_padrao = ['Cardiologia', 'Dermatologia', 'Endocrinologia',
                           'Gastroenterologia', 'Ginecologia', 'Neurologia',
                           'Oftalmologia', 'Ortopedia', 'Pediatria', 'Psiquiatria', 'Clínica Geral']

    if medico['especialidade'] in especialidades_padrao:
        especialidade_select = medico['especialidade']
        especialidade_custom = ""
    else:
        especialidade_select = "Outra"
        especialidade_custom = medico['especialidade']

    return (
        True,  # modal aberto
        f"✏️ Editar Médico: {medico['nome']}",
        medico_id,
        medico['nome'],
        medico['crm'],
        especialidade_select,
        especialidade_custom,
        medico['telefone'],
        medico['email'],
        medico['valor_consulta'],
        medico['duracao_consulta'],
        medico['horario_atendimento'],
        medico['convenios_aceitos'],
        medico['ativo'],
        medico['observacoes']
    )

# Callback para limpar formulário
@callback(
    [Output('input-nome-medico', 'value', allow_duplicate=True),
     Output('input-crm-medico', 'value', allow_duplicate=True),
     Output('input-especialidade-medico', 'value', allow_duplicate=True),
     Output('input-especialidade-custom-medico', 'value', allow_duplicate=True),
     Output('input-telefone-medico', 'value', allow_duplicate=True),
     Output('input-email-medico', 'value', allow_duplicate=True),
     Output('input-valor-consulta-medico', 'value', allow_duplicate=True),
     Output('input-duracao-consulta-medico', 'value', allow_duplicate=True),
     Output('input-horario-medico', 'value', allow_duplicate=True),
     Output('input-convenios-medico', 'value', allow_duplicate=True),
     Output('input-status-medico', 'value', allow_duplicate=True),
     Output('input-observacoes-medico', 'value', allow_duplicate=True)],
    Input('btn-limpar-medico', 'n_clicks'),
    prevent_initial_call=True
)
def limpar_formulario_medico(limpar_clicks):
    """Limpa todos os campos do formulário"""
    if limpar_clicks:
        return "", "", None, "", "", "", None, 30, "", "", 1, ""
    return dash.no_update

# Callback para salvar médico
@callback(
    [Output('alert-medico', 'children'),
     Output('modal-medico', 'is_open', allow_duplicate=True),
     Output('btn-refresh-medicos', 'n_clicks', allow_duplicate=True),
     Output('toast-container-medicos', 'children', allow_duplicate=True)],
    Input('btn-salvar-medico', 'n_clicks'),
    [State('medico-edit-id', 'data'),
     State('input-nome-medico', 'value'),
     State('input-crm-medico', 'value'),
     State('input-especialidade-medico', 'value'),
     State('input-especialidade-custom-medico', 'value'),
     State('input-telefone-medico', 'value'),
     State('input-email-medico', 'value'),
     State('input-valor-consulta-medico', 'value'),
     State('input-duracao-consulta-medico', 'value'),
     State('input-horario-medico', 'value'),
     State('input-convenios-medico', 'value'),
     State('input-status-medico', 'value'),
     State('input-observacoes-medico', 'value')],
    prevent_initial_call=True
)
def salvar_medico(salvar_clicks, edit_id, nome, crm, especialidade, especialidade_custom,
                 telefone, email, valor_consulta, duracao_consulta, horario_atendimento,
                 convenios_aceitos, status, observacoes):
    """Salva ou atualiza médico"""
    if not salvar_clicks:
        return "", dash.no_update, dash.no_update, dash.no_update

    # Determinar especialidade final
    especialidade_final = especialidade_custom if especialidade == "Outra" else especialidade

    # Preparar dados
    data = {
        'nome': nome or '',
        'crm': crm or '',
        'especialidade': especialidade_final or '',
        'telefone': telefone or ''
    }

    # Validar dados
    validation = validate_doctor(data, edit_id)

    if not validation['valid']:
        errors_html = [html.Li(error) for error in validation['errors']]
        alert = dbc.Alert([
            html.H6("❌ Erros de Validação:", className="mb-2"),
            html.Ul(errors_html)
        ], color="danger")
        return alert, dash.no_update, dash.no_update, dash.no_update

    try:
        if edit_id:
            # Atualizar médico existente
            db_manager.execute_insert('''
                UPDATE medicos SET
                    nome = ?, crm = ?, especialidade = ?, telefone = ?,
                    email = ?, valor_consulta = ?, duracao_consulta = ?,
                    horario_atendimento = ?, convenios_aceitos = ?,
                    observacoes = ?, ativo = ?
                WHERE id = ?
            ''', (nome, crm.upper(), especialidade_final, telefone, email,
                  valor_consulta, duracao_consulta, horario_atendimento,
                  convenios_aceitos, observacoes, status, edit_id))

            success_msg = f"Médico {nome} atualizado com sucesso!"
            action_type = "atualizado"
        else:
            # Criar novo médico
            db_manager.execute_insert('''
                INSERT INTO medicos
                (nome, crm, especialidade, telefone, email, valor_consulta,
                 duracao_consulta, horario_atendimento, convenios_aceitos,
                 observacoes, ativo, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, crm.upper(), especialidade_final, telefone, email,
                  valor_consulta, duracao_consulta, horario_atendimento,
                  convenios_aceitos, observacoes, status,
                  datetime.now().isoformat()))

            success_msg = f"Médico {nome} cadastrado com sucesso!"
            action_type = "cadastrado"

        # Criar toast de sucesso
        toast = dbc.Toast(
            success_msg,
            header="✅ Operação Realizada",
            is_open=True,
            dismissable=True,
            duration=4000,
            icon="success",
            style={
                "position": "fixed",
                "top": 66,
                "right": 10,
                "width": 350,
                "z-index": 9999
            }
        )

        # Fechar modal e atualizar lista
        return "", False, 1, toast

    except Exception as e:
        alert = dbc.Alert(f"❌ Erro ao salvar médico: {str(e)}", color="danger")
        return alert, dash.no_update, dash.no_update, dash.no_update

# Callback para confirmar exclusão
@callback(
    [Output('modal-confirm-delete-medico', 'is_open'),
     Output('confirm-delete-message-medico', 'children'),
     Output('medico-delete-id', 'data')],
    [Input({'type': 'btn-delete-medico', 'index': ALL}, 'n_clicks'),
     Input('btn-cancel-delete-medico', 'n_clicks')],
    [State('medicos-data', 'data'),
     State('modal-confirm-delete-medico', 'is_open')],
    prevent_initial_call=True
)
def confirm_delete_medico(delete_clicks, cancel_clicks, medicos_data, is_open):
    """Abre modal de confirmação de exclusão"""
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id']

    if 'btn-cancel-delete-medico' in button_id:
        return False, "", None

    if 'btn-delete-medico' in button_id and any(delete_clicks):
        # Identificar médico
        medico_id = eval(button_id.split('.')[0])['index']
        medico = next((m for m in medicos_data if m['id'] == medico_id), None)

        if not medico:
            return dash.no_update

        # Verificar dependências
        check_result = can_delete_doctor(medico_id)

        if check_result['can_delete']:
            message = html.Div([
                html.P(f"Tem certeza que deseja excluir o médico:"),
                html.H5(f"👨‍⚕️ {medico['nome']}", className="text-primary"),
                html.P(f"🏥 {medico['crm']} - {medico['especialidade']}"),
                html.Hr(),
                html.P("⚠️ Esta ação não pode ser desfeita!", className="text-warning")
            ])
        else:
            message = html.Div([
                html.P(f"❌ Não é possível excluir o médico:"),
                html.H5(f"👨‍⚕️ {medico['nome']}", className="text-danger"),
                html.P(f"🏥 {medico['crm']} - {medico['especialidade']}"),
                html.Hr(),
                html.P(check_result['message'], className="text-warning")
            ])

        return True, message, medico_id if check_result['can_delete'] else None

    return dash.no_update

# Callback para executar exclusão
@callback(
    [Output('modal-confirm-delete-medico', 'is_open', allow_duplicate=True),
     Output('btn-refresh-medicos', 'n_clicks', allow_duplicate=True),
     Output('toast-container-medicos', 'children')],
    Input('btn-confirm-delete-medico', 'n_clicks'),
    [State('medico-delete-id', 'data'),
     State('medicos-data', 'data')],
    prevent_initial_call=True
)
def execute_delete_medico(confirm_clicks, delete_id, medicos_data):
    """Executa exclusão do médico"""
    if not confirm_clicks or not delete_id:
        return dash.no_update

    try:
        # Encontrar nome do médico
        medico = next((m for m in medicos_data if m['id'] == delete_id), None)
        nome_medico = medico['nome'] if medico else 'Médico'

        # Executar exclusão
        db_manager.execute_insert('DELETE FROM medicos WHERE id = ?', (delete_id,))

        # Toast de sucesso
        toast = dbc.Toast(
            f"✅ Médico {nome_medico} excluído com sucesso!",
            header="Exclusão Realizada",
            is_open=True,
            dismissable=True,
            duration=4000,
            icon="success",
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, "z-index": 9999}
        )

        return False, 1, toast

    except Exception as e:
        # Toast de erro
        toast = dbc.Toast(
            f"❌ Erro ao excluir médico: {str(e)}",
            header="Erro na Exclusão",
            is_open=True,
            dismissable=True,
            duration=4000,
            icon="danger",
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, "z-index": 9999}
        )

        return False, dash.no_update, toast
