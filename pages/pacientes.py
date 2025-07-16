#!/usr/bin/env python3
"""
Página de Gestão de Pacientes - CRUD Completo
Sistema para cadastro, edição, listagem e exclusão de pacientes
"""

import dash
from dash import dcc, html, Input, Output, State, callback, dash_table, ALL
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, date
import json

from utils.db_manager import db_manager
from utils.relational_checks import integrity_checker, validate_patient, can_delete_patient

def create_layout():
    return dbc.Container([
        # Título da página
        dbc.Row([
            dbc.Col([
                html.H2("👥 Gestão de Pacientes", className="mb-4"),
                
                # Botão para novo paciente
                dbc.Button(
                    "➕ Novo Paciente",
                    id="btn-novo-paciente",
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
                                dbc.Label("🔍 Buscar Paciente:"),
                                dbc.Input(
                                    id="search-paciente",
                                    placeholder="Nome, CPF ou telefone...",
                                    debounce=True
                                )
                            ], md=6),
                            
                            dbc.Col([
                                dbc.Label("📊 Status:"),
                                dcc.Dropdown(
                                    id="filter-status-paciente",
                                    options=[
                                        {'label': 'Todos', 'value': 'todos'},
                                        {'label': '✅ Ativos', 'value': 'ativo'},
                                        {'label': '❌ Inativos', 'value': 'inativo'}
                                    ],
                                    value='todos'
                                )
                            ], md=3),
                            
                            dbc.Col([
                                dbc.Label(" "),
                                dbc.Button(
                                    "🔄 Atualizar",
                                    id="btn-refresh-pacientes",
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
        
        # Tabela de pacientes
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📋 Lista de Pacientes", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="tabela-pacientes")
                    ])
                ])
            ])
        ]),
        
        # Modal para cadastro/edição
        dbc.Modal([
            dbc.ModalHeader([
                html.H4(id="modal-paciente-title")
            ]),
            dbc.ModalBody([
                # Alertas
                html.Div(id="alert-paciente"),
                
                # Formulário
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Nome Completo *:"),
                            dbc.Input(
                                id="input-nome-paciente",
                                placeholder="Nome completo do paciente",
                                required=True
                            )
                        ], md=8),
                        
                        dbc.Col([
                            dbc.Label("CPF *:"),
                            dbc.Input(
                                id="input-cpf-paciente",
                                placeholder="000.000.000-00",
                                required=True
                            )
                        ], md=4)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Data de Nascimento *:"),
                            dcc.DatePickerSingle(
                                id="input-nascimento-paciente",
                                display_format='DD/MM/YYYY',
                                placeholder="Selecione a data"
                            )
                        ], md=4),
                        
                        dbc.Col([
                            dbc.Label("Gênero *:"),
                            dcc.Dropdown(
                                id="input-genero-paciente",
                                options=[
                                    {'label': 'Masculino', 'value': 'M'},
                                    {'label': 'Feminino', 'value': 'F'},
                                    {'label': 'Outro', 'value': 'O'}
                                ],
                                placeholder="Selecione o gênero"
                            )
                        ], md=4),
                        
                        dbc.Col([
                            dbc.Label("Estado Civil:"),
                            dcc.Dropdown(
                                id="input-estado-civil-paciente",
                                options=[
                                    {'label': 'Solteiro(a)', 'value': 'solteiro'},
                                    {'label': 'Casado(a)', 'value': 'casado'},
                                    {'label': 'Divorciado(a)', 'value': 'divorciado'},
                                    {'label': 'Viúvo(a)', 'value': 'viuvo'}
                                ],
                                placeholder="Estado civil"
                            )
                        ], md=4)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Telefone *:"),
                            dbc.Input(
                                id="input-telefone-paciente",
                                placeholder="(11) 99999-9999",
                                required=True
                            )
                        ], md=6),
                        
                        dbc.Col([
                            dbc.Label("Email:"),
                            dbc.Input(
                                id="input-email-paciente",
                                type="email",
                                placeholder="email@exemplo.com"
                            )
                        ], md=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Endereço:"),
                            dbc.Textarea(
                                id="input-endereco-paciente",
                                placeholder="Endereço completo",
                                rows=2
                            )
                        ], md=8),
                        
                        dbc.Col([
                            dbc.Label("Status:"),
                            dcc.Dropdown(
                                id="input-status-paciente",
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
                            dbc.Label("Observações:"),
                            dbc.Textarea(
                                id="input-observacoes-paciente",
                                placeholder="Observações médicas, alergias, etc.",
                                rows=3
                            )
                        ])
                    ])
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "💾 Salvar",
                    id="btn-salvar-paciente",
                    color="success",
                    className="me-2"
                ),
                dbc.Button(
                    "🧹 Limpar",
                    id="btn-limpar-paciente",
                    color="secondary",
                    outline=True,
                    className="me-2"
                ),
                dbc.Button(
                    "❌ Cancelar",
                    id="btn-cancelar-paciente",
                    color="danger",
                    outline=True
                )
            ])
        ], id="modal-paciente", size="lg", is_open=False),
        
        # Modal de confirmação de exclusão
        dbc.Modal([
            dbc.ModalHeader("⚠️ Confirmar Exclusão"),
            dbc.ModalBody([
                html.Div(id="confirm-delete-message-paciente")
            ]),
            dbc.ModalFooter([
                dbc.Button(
                    "🗑️ Confirmar Exclusão",
                    id="btn-confirm-delete-paciente",
                    color="danger",
                    className="me-2"
                ),
                dbc.Button(
                    "❌ Cancelar",
                    id="btn-cancel-delete-paciente",
                    color="secondary"
                )
            ])
        ], id="modal-confirm-delete-paciente", is_open=False),
        
        # Stores para dados
        dcc.Store(id='paciente-edit-id', data=None),
        dcc.Store(id='paciente-delete-id', data=None),
        dcc.Store(id='pacientes-data', data=[]),
        
        # Toast para notificações
        html.Div(id="toast-container-pacientes")
        
    ], fluid=True)

# Callback para carregar dados dos pacientes
@callback(
    Output('pacientes-data', 'data'),
    [Input('btn-refresh-pacientes', 'n_clicks'),
     Input('search-paciente', 'value'),
     Input('filter-status-paciente', 'value')],
    prevent_initial_call=False
)
def load_pacientes_data(refresh_clicks, search_term, status_filter):
    """Carrega dados dos pacientes com filtros"""
    try:
        # Query base
        query = '''
            SELECT 
                id, nome, cpf, data_nascimento, genero, telefone, 
                email, endereco, estado_civil, observacoes, ativo,
                data_cadastro
            FROM pacientes
            WHERE 1=1
        '''
        params = []
        
        # Filtro por status
        if status_filter != 'todos':
            query += ' AND ativo = ?'
            params.append(1 if status_filter == 'ativo' else 0)
        
        # Filtro por busca
        if search_term:
            query += ' AND (nome LIKE ? OR cpf LIKE ? OR telefone LIKE ?)'
            search_param = f'%{search_term}%'
            params.extend([search_param, search_param, search_param])
        
        query += ' ORDER BY nome'
        
        df = db_manager.execute_query(query, params)
        
        if df.empty:
            return []
        
        # Formatar dados para exibição
        pacientes = []
        for _, row in df.iterrows():
            paciente = {
                'id': row['id'],
                'nome': row['nome'],
                'cpf': integrity_checker.format_cpf(row['cpf']),
                'cpf_raw': row['cpf'],
                'data_nascimento': row['data_nascimento'],
                'genero': row['genero'],
                'telefone': row['telefone'],
                'email': row['email'] or '',
                'endereco': row['endereco'] or '',
                'estado_civil': row['estado_civil'] or '',
                'observacoes': row['observacoes'] or '',
                'ativo': row['ativo'],
                'data_cadastro': row['data_cadastro']
            }
            pacientes.append(paciente)
        
        return pacientes
        
    except Exception as e:
        print(f"Erro ao carregar pacientes: {e}")
        return []

# Callback para renderizar tabela
@callback(
    Output('tabela-pacientes', 'children'),
    Input('pacientes-data', 'data')
)
def render_pacientes_table(pacientes_data):
    """Renderiza tabela de pacientes"""
    if not pacientes_data:
        return dbc.Alert("Nenhum paciente encontrado.", color="info", className="text-center")
    
    # Criar linhas da tabela
    table_rows = []
    for index, paciente in enumerate(pacientes_data, 1):  # Começar numeração em 1
        # Status badge
        status_badge = html.Span(
            "✅ Ativo" if paciente['ativo'] else "❌ Inativo",
            className=f"badge bg-{'success' if paciente['ativo'] else 'danger'}"
        )

        # Gênero
        genero_map = {'M': 'Masculino', 'F': 'Feminino', 'O': 'Outro'}
        genero_display = genero_map.get(paciente['genero'], paciente['genero'])

        # Botões de ação
        action_buttons = dbc.ButtonGroup([
            dbc.Button(
                "✏️",
                id={'type': 'btn-edit-paciente', 'index': paciente['id']},
                color="primary",
                size="sm",
                title="Editar paciente"
            ),
            dbc.Button(
                "🗑️",
                id={'type': 'btn-delete-paciente', 'index': paciente['id']},
                color="danger",
                size="sm",
                title="Excluir paciente"
            )
        ])

        row = html.Tr([
            html.Td(index),  # ID sequencial na interface
            html.Td(paciente['nome']),
            html.Td(paciente['cpf']),
            html.Td(genero_display),
            html.Td(paciente['telefone']),
            html.Td(paciente['email']),
            html.Td(status_badge),
            html.Td(paciente['data_cadastro'][:10] if paciente['data_cadastro'] else ''),
            html.Td(action_buttons)
        ])
        table_rows.append(row)
    
    # Tabela completa
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("ID"),
                html.Th("Nome Completo"),
                html.Th("CPF"),
                html.Th("Gênero"),
                html.Th("Telefone"),
                html.Th("Email"),
                html.Th("Status"),
                html.Th("Cadastro"),
                html.Th("Ações")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, bordered=True, hover=True, responsive=True)
    
    return table

# Callback para abrir modal de novo paciente
@callback(
    [Output('modal-paciente', 'is_open'),
     Output('modal-paciente-title', 'children'),
     Output('paciente-edit-id', 'data')],
    [Input('btn-novo-paciente', 'n_clicks'),
     Input('btn-cancelar-paciente', 'n_clicks')],
    [State('modal-paciente', 'is_open')],
    prevent_initial_call=True
)
def toggle_modal_novo_paciente(novo_clicks, cancelar_clicks, is_open):
    """Controla abertura/fechamento do modal para novo paciente"""
    ctx = dash.callback_context

    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'btn-novo-paciente':
            return True, "➕ Novo Paciente", None
        elif button_id == 'btn-cancelar-paciente':
            return False, "", None

    return is_open, "", None

# Callback para editar paciente
@callback(
    [Output('modal-paciente', 'is_open', allow_duplicate=True),
     Output('modal-paciente-title', 'children', allow_duplicate=True),
     Output('paciente-edit-id', 'data', allow_duplicate=True),
     Output('input-nome-paciente', 'value'),
     Output('input-cpf-paciente', 'value'),
     Output('input-nascimento-paciente', 'date'),
     Output('input-genero-paciente', 'value'),
     Output('input-telefone-paciente', 'value'),
     Output('input-email-paciente', 'value'),
     Output('input-endereco-paciente', 'value'),
     Output('input-estado-civil-paciente', 'value'),
     Output('input-status-paciente', 'value'),
     Output('input-observacoes-paciente', 'value')],
    Input({'type': 'btn-edit-paciente', 'index': ALL}, 'n_clicks'),
    [State('pacientes-data', 'data')],
    prevent_initial_call=True
)
def edit_paciente(edit_clicks, pacientes_data):
    """Abre modal para edição de paciente"""
    ctx = dash.callback_context

    if not ctx.triggered or not any(edit_clicks):
        return dash.no_update

    # Identificar qual botão foi clicado
    button_id = ctx.triggered[0]['prop_id']
    paciente_id = eval(button_id.split('.')[0])['index']

    # Encontrar dados do paciente
    paciente = next((p for p in pacientes_data if p['id'] == paciente_id), None)

    if not paciente:
        return dash.no_update

    return (
        True,  # modal aberto
        f"✏️ Editar Paciente: {paciente['nome']}",
        paciente_id,
        paciente['nome'],
        paciente['cpf'],
        paciente['data_nascimento'],
        paciente['genero'],
        paciente['telefone'],
        paciente['email'],
        paciente['endereco'],
        paciente['estado_civil'],
        paciente['ativo'],
        paciente['observacoes']
    )

# Callback para limpar formulário
@callback(
    [Output('input-nome-paciente', 'value', allow_duplicate=True),
     Output('input-cpf-paciente', 'value', allow_duplicate=True),
     Output('input-nascimento-paciente', 'date', allow_duplicate=True),
     Output('input-genero-paciente', 'value', allow_duplicate=True),
     Output('input-telefone-paciente', 'value', allow_duplicate=True),
     Output('input-email-paciente', 'value', allow_duplicate=True),
     Output('input-endereco-paciente', 'value', allow_duplicate=True),
     Output('input-estado-civil-paciente', 'value', allow_duplicate=True),
     Output('input-status-paciente', 'value', allow_duplicate=True),
     Output('input-observacoes-paciente', 'value', allow_duplicate=True)],
    Input('btn-limpar-paciente', 'n_clicks'),
    prevent_initial_call=True
)
def limpar_formulario_paciente(limpar_clicks):
    """Limpa todos os campos do formulário"""
    if limpar_clicks:
        return "", "", None, None, "", "", "", None, 1, ""
    return dash.no_update

# Callback para salvar paciente
@callback(
    [Output('alert-paciente', 'children'),
     Output('modal-paciente', 'is_open', allow_duplicate=True),
     Output('btn-refresh-pacientes', 'n_clicks', allow_duplicate=True),
     Output('toast-container-pacientes', 'children', allow_duplicate=True)],
    Input('btn-salvar-paciente', 'n_clicks'),
    [State('paciente-edit-id', 'data'),
     State('input-nome-paciente', 'value'),
     State('input-cpf-paciente', 'value'),
     State('input-nascimento-paciente', 'date'),
     State('input-genero-paciente', 'value'),
     State('input-telefone-paciente', 'value'),
     State('input-email-paciente', 'value'),
     State('input-endereco-paciente', 'value'),
     State('input-estado-civil-paciente', 'value'),
     State('input-status-paciente', 'value'),
     State('input-observacoes-paciente', 'value')],
    prevent_initial_call=True
)
def salvar_paciente(salvar_clicks, edit_id, nome, cpf, nascimento, genero,
                   telefone, email, endereco, estado_civil, status, observacoes):
    """Salva ou atualiza paciente"""
    if not salvar_clicks:
        return "", dash.no_update, dash.no_update, dash.no_update

    try:
        # Debug: Log dos valores recebidos
        print(f"DEBUG - Valores recebidos:")
        print(f"  edit_id: {edit_id} (tipo: {type(edit_id)})")
        print(f"  nome: {nome} (tipo: {type(nome)})")
        print(f"  cpf: {cpf} (tipo: {type(cpf)})")
        print(f"  nascimento: {nascimento} (tipo: {type(nascimento)})")
        print(f"  genero: {genero} (tipo: {type(genero)})")
        print(f"  status: {status} (tipo: {type(status)})")

        # Preparar dados com tratamento robusto de None
        data = {
            'nome': str(nome) if nome is not None else '',
            'cpf': str(cpf) if cpf is not None else '',
            'data_nascimento': str(nascimento) if nascimento is not None else '',
            'genero': str(genero) if genero is not None else '',
            'telefone': str(telefone) if telefone is not None else '',
            'email': str(email) if email is not None else '',
            'endereco': str(endereco) if endereco is not None else '',
            'estado_civil': str(estado_civil) if estado_civil is not None else '',
            'observacoes': str(observacoes) if observacoes is not None else ''
        }

        print(f"DEBUG - Dados preparados: {data}")

        # Validar dados com tratamento de erro
        validation = validate_patient(data, edit_id)
        print(f"DEBUG - Resultado da validação: {validation}")

        if validation is None:
            raise Exception("Função de validação retornou None")

        if not validation.get('valid', False):
            errors = validation.get('errors', ['Erro de validação desconhecido'])
            errors_html = [html.Li(error) for error in errors]
            alert = dbc.Alert([
                html.H6("❌ Erros de Validação:", className="mb-2"),
                html.Ul(errors_html)
            ], color="danger")
            return alert, dash.no_update, dash.no_update, dash.no_update

        # Limpar CPF
        cpf_clean = integrity_checker.clean_cpf(data['cpf'])
        print(f"DEBUG - CPF limpo: {cpf_clean}")

        if edit_id:
            # Atualizar paciente existente
            print(f"DEBUG - Atualizando paciente ID: {edit_id}")
            result = db_manager.execute_insert('''
                UPDATE pacientes SET
                    nome = ?, cpf = ?, data_nascimento = ?, genero = ?,
                    telefone = ?, email = ?, endereco = ?, estado_civil = ?,
                    observacoes = ?, ativo = ?
                WHERE id = ?
            ''', (data['nome'], cpf_clean, data['data_nascimento'], data['genero'],
                  data['telefone'], data['email'], data['endereco'], data['estado_civil'],
                  data['observacoes'], status, edit_id))

            print(f"DEBUG - Resultado do UPDATE: {result}")
            success_msg = f"Paciente {data['nome']} atualizado com sucesso!"
            action_type = "atualizado"
        else:
            # Criar novo paciente
            print(f"DEBUG - Criando novo paciente")
            result = db_manager.execute_insert('''
                INSERT INTO pacientes
                (nome, cpf, data_nascimento, genero, telefone, email,
                 endereco, estado_civil, observacoes, ativo, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['nome'], cpf_clean, data['data_nascimento'], data['genero'],
                  data['telefone'], data['email'], data['endereco'], data['estado_civil'],
                  data['observacoes'], status, datetime.now().isoformat()))

            print(f"DEBUG - Resultado do INSERT: {result}")
            success_msg = f"Paciente {data['nome']} cadastrado com sucesso!"
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
        import traceback
        error_details = traceback.format_exc()
        print(f"ERRO COMPLETO: {error_details}")

        alert = dbc.Alert([
            html.H6("❌ Erro ao salvar paciente:", className="mb-2"),
            html.P(str(e)),
            html.Details([
                html.Summary("Detalhes técnicos"),
                html.Pre(error_details, style={'font-size': '12px', 'max-height': '200px', 'overflow': 'auto'})
            ])
        ], color="danger")
        return alert, dash.no_update, dash.no_update, dash.no_update

# Callback para confirmar exclusão
@callback(
    [Output('modal-confirm-delete-paciente', 'is_open'),
     Output('confirm-delete-message-paciente', 'children'),
     Output('paciente-delete-id', 'data')],
    [Input({'type': 'btn-delete-paciente', 'index': ALL}, 'n_clicks'),
     Input('btn-cancel-delete-paciente', 'n_clicks')],
    [State('pacientes-data', 'data'),
     State('modal-confirm-delete-paciente', 'is_open')],
    prevent_initial_call=True
)
def confirm_delete_paciente(delete_clicks, cancel_clicks, pacientes_data, is_open):
    """Abre modal de confirmação de exclusão"""
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id']

    if 'btn-cancel-delete-paciente' in button_id:
        return False, "", None

    if 'btn-delete-paciente' in button_id and any(delete_clicks):
        # Identificar paciente
        paciente_id = eval(button_id.split('.')[0])['index']
        paciente = next((p for p in pacientes_data if p['id'] == paciente_id), None)

        if not paciente:
            return dash.no_update

        # Verificar dependências
        check_result = can_delete_patient(paciente_id)

        if check_result['can_delete']:
            message = html.Div([
                html.P(f"Tem certeza que deseja excluir o paciente:"),
                html.H5(f"👤 {paciente['nome']}", className="text-primary"),
                html.P(f"📄 CPF: {paciente['cpf']}"),
                html.Hr(),
                html.P("⚠️ Esta ação não pode ser desfeita!", className="text-warning")
            ])
        else:
            message = html.Div([
                html.P(f"❌ Não é possível excluir o paciente:"),
                html.H5(f"👤 {paciente['nome']}", className="text-danger"),
                html.Hr(),
                html.P(check_result['message'], className="text-warning")
            ])

        return True, message, paciente_id if check_result['can_delete'] else None

    return dash.no_update

# Callback para executar exclusão
@callback(
    [Output('modal-confirm-delete-paciente', 'is_open', allow_duplicate=True),
     Output('btn-refresh-pacientes', 'n_clicks', allow_duplicate=True),
     Output('toast-container-pacientes', 'children')],
    Input('btn-confirm-delete-paciente', 'n_clicks'),
    [State('paciente-delete-id', 'data'),
     State('pacientes-data', 'data')],
    prevent_initial_call=True
)
def execute_delete_paciente(confirm_clicks, delete_id, pacientes_data):
    """Executa exclusão do paciente"""
    if not confirm_clicks or not delete_id:
        return dash.no_update

    try:
        # Encontrar nome do paciente
        paciente = next((p for p in pacientes_data if p['id'] == delete_id), None)
        nome_paciente = paciente['nome'] if paciente else 'Paciente'

        # Executar exclusão
        db_manager.execute_insert('DELETE FROM pacientes WHERE id = ?', (delete_id,))

        # Toast de sucesso
        toast = dbc.Toast(
            f"✅ Paciente {nome_paciente} excluído com sucesso!",
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
            f"❌ Erro ao excluir paciente: {str(e)}",
            header="Erro na Exclusão",
            is_open=True,
            dismissable=True,
            duration=4000,
            icon="danger",
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, "z-index": 9999}
        )

        return False, dash.no_update, toast
