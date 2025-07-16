#!/usr/bin/env python3
"""
Página de Prescrições Médicas
Sistema para gerar receitas médicas em PDF
"""

import dash
from dash import dcc, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, date
import os

from utils.db_manager import db_manager
from utils.prescription_generator import create_prescription_pdf

# Layout da página
def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("💊 Prescrições Médicas", className="mb-4"),
                
                # Formulário de Nova Prescrição
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📝 Nova Prescrição", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            # Dados do Paciente
                            dbc.Col([
                                html.H6("👤 Dados do Paciente", className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Paciente:"),
                                        dcc.Dropdown(
                                            id="select-paciente-prescricao",
                                            placeholder="Selecione um paciente...",
                                            className="mb-3"
                                        )
                                    ], md=8),
                                    
                                    dbc.Col([
                                        dbc.Label("Data da Consulta:"),
                                        dcc.DatePickerSingle(
                                            id="data-prescricao",
                                            date=date.today(),
                                            display_format='DD/MM/YYYY',
                                            className="mb-3"
                                        )
                                    ], md=4)
                                ]),
                                
                                # Informações do paciente selecionado
                                html.Div(id="info-paciente-prescricao", className="mb-3")
                                
                            ], md=6),
                            
                            # Dados do Médico
                            dbc.Col([
                                html.H6("👨‍⚕️ Dados do Médico", className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Médico:"),
                                        dbc.Input(
                                            id="nome-medico",
                                            placeholder="Nome do médico",
                                            value="Dr. João Silva",
                                            className="mb-3"
                                        )
                                    ], md=12)
                                ]),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("CRM:"),
                                        dbc.Input(
                                            id="crm-medico",
                                            placeholder="CRM/UF 123456",
                                            value="CRM/SP 123456",
                                            className="mb-3"
                                        )
                                    ], md=6),
                                    
                                    dbc.Col([
                                        dbc.Label("Especialidade:"),
                                        dbc.Input(
                                            id="especialidade-medico",
                                            placeholder="Especialidade",
                                            value="Clínica Geral",
                                            className="mb-3"
                                        )
                                    ], md=6)
                                ])
                                
                            ], md=6)
                        ]),
                        
                        html.Hr(),
                        
                        # Medicamentos
                        html.H6("💊 Medicamentos", className="mb-3"),
                        
                        # Formulário para adicionar medicamento
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Nome do Medicamento:"),
                                dbc.Input(
                                    id="nome-medicamento",
                                    placeholder="Ex: Paracetamol 500mg"
                                )
                            ], md=3),
                            
                            dbc.Col([
                                dbc.Label("Dosagem:"),
                                dbc.Input(
                                    id="dosagem-medicamento",
                                    placeholder="Ex: 1 comprimido"
                                )
                            ], md=2),
                            
                            dbc.Col([
                                dbc.Label("Frequência:"),
                                dbc.Input(
                                    id="frequencia-medicamento",
                                    placeholder="Ex: A cada 8 horas"
                                )
                            ], md=2),
                            
                            dbc.Col([
                                dbc.Label("Duração:"),
                                dbc.Input(
                                    id="duracao-medicamento",
                                    placeholder="Ex: 7 dias"
                                )
                            ], md=2),
                            
                            dbc.Col([
                                dbc.Label("Instruções:"),
                                dbc.Input(
                                    id="instrucoes-medicamento",
                                    placeholder="Ex: Tomar com água"
                                )
                            ], md=2),
                            
                            dbc.Col([
                                dbc.Label(" "),
                                dbc.Button(
                                    "➕ Adicionar",
                                    id="btn-adicionar-medicamento",
                                    color="success",
                                    size="sm",
                                    className="d-block"
                                )
                            ], md=1)
                        ], className="mb-3"),
                        
                        # Lista de medicamentos adicionados
                        html.Div(id="lista-medicamentos", className="mb-3"),
                        
                        html.Hr(),
                        
                        # Observações
                        html.H6("📋 Observações", className="mb-3"),
                        dbc.Textarea(
                            id="observacoes-prescricao",
                            placeholder="Observações médicas, instruções especiais, retorno...",
                            rows=3,
                            className="mb-3"
                        ),
                        
                        # Botões de ação
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "📄 Gerar Prescrição PDF",
                                    id="btn-gerar-prescricao",
                                    color="primary",
                                    size="lg",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "🔄 Limpar Formulário",
                                    id="btn-limpar-prescricao",
                                    color="secondary",
                                    outline=True,
                                    size="lg"
                                )
                            ])
                        ])
                    ])
                ], className="mb-4"),
                
                # Histórico de Prescrições
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📚 Histórico de Prescrições", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="historico-prescricoes")
                    ])
                ])
            ])
        ]),
        
        # Stores para dados
        dcc.Store(id='medicamentos-store', data=[]),
        dcc.Store(id='prescricao-gerada-store'),
        
        # Modal para confirmação
        dbc.Modal([
            dbc.ModalHeader("✅ Prescrição Gerada com Sucesso!"),
            dbc.ModalBody([
                html.P("A prescrição foi gerada e salva com sucesso."),
                html.Div(id="modal-prescricao-info")
            ]),
            dbc.ModalFooter([
                dbc.Button("📥 Download PDF", id="btn-download-pdf", color="primary", className="me-2"),
                dbc.Button("Fechar", id="btn-fechar-modal", color="secondary")
            ])
        ], id="modal-prescricao-sucesso", is_open=False)
        
    ], fluid=True)

# Callbacks
@callback(
    Output('select-paciente-prescricao', 'options'),
    Input('select-paciente-prescricao', 'id')
)
def load_pacientes_options(trigger):
    """Carrega opções de pacientes"""
    try:
        pacientes = db_manager.execute_query('''
            SELECT id, nome, cpf FROM pacientes 
            WHERE ativo = 1 
            ORDER BY nome
        ''')
        
        options = [
            {
                'label': f"{row['nome']} - CPF: {row['cpf']}", 
                'value': row['id']
            }
            for _, row in pacientes.iterrows()
        ]
        
        return options
        
    except Exception as e:
        return []

@callback(
    Output('info-paciente-prescricao', 'children'),
    Input('select-paciente-prescricao', 'value')
)
def show_patient_info(paciente_id):
    """Mostra informações do paciente selecionado"""
    if not paciente_id:
        return ""
    
    try:
        paciente = db_manager.execute_query('''
            SELECT nome, cpf, data_nascimento, telefone, endereco 
            FROM pacientes WHERE id = ?
        ''', (paciente_id,))
        
        if not paciente.empty:
            p = paciente.iloc[0]
            
            return dbc.Alert([
                html.Strong(f"👤 {p['nome']}"), html.Br(),
                f"📄 CPF: {p['cpf']}", html.Br(),
                f"🎂 Nascimento: {p['data_nascimento']}", html.Br(),
                f"📞 Telefone: {p['telefone']}", html.Br(),
                f"🏠 Endereço: {p['endereco']}"
            ], color="info", className="mb-0")
        
        return ""
        
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar dados: {str(e)}", color="danger")

@callback(
    [Output('medicamentos-store', 'data'),
     Output('nome-medicamento', 'value'),
     Output('dosagem-medicamento', 'value'),
     Output('frequencia-medicamento', 'value'),
     Output('duracao-medicamento', 'value'),
     Output('instrucoes-medicamento', 'value')],
    Input('btn-adicionar-medicamento', 'n_clicks'),
    [State('medicamentos-store', 'data'),
     State('nome-medicamento', 'value'),
     State('dosagem-medicamento', 'value'),
     State('frequencia-medicamento', 'value'),
     State('duracao-medicamento', 'value'),
     State('instrucoes-medicamento', 'value')],
    prevent_initial_call=True
)
def add_medication(n_clicks, medicamentos_atuais, nome, dosagem, frequencia, duracao, instrucoes):
    """Adiciona medicamento à lista"""
    if not n_clicks or not nome:
        return medicamentos_atuais, "", "", "", "", ""
    
    novo_medicamento = {
        'name': nome,
        'dosage': dosagem or "",
        'frequency': frequencia or "",
        'duration': duracao or "",
        'instructions': instrucoes or ""
    }
    
    medicamentos_atuais.append(novo_medicamento)
    
    # Limpar campos
    return medicamentos_atuais, "", "", "", "", ""

@callback(
    Output('lista-medicamentos', 'children'),
    Input('medicamentos-store', 'data')
)
def update_medications_list(medicamentos):
    """Atualiza a lista de medicamentos"""
    if not medicamentos:
        return dbc.Alert("Nenhum medicamento adicionado.", color="light", className="text-center")
    
    items = []
    for i, med in enumerate(medicamentos):
        card = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6(f"💊 {med['name']}", className="mb-1"),
                        html.Small([
                            f"Dosagem: {med['dosage']}" if med['dosage'] else "",
                            f" | Frequência: {med['frequency']}" if med['frequency'] else "",
                            f" | Duração: {med['duration']}" if med['duration'] else "",
                            html.Br() if med['instructions'] else "",
                            f"Instruções: {med['instructions']}" if med['instructions'] else ""
                        ], className="text-muted")
                    ], md=10),
                    dbc.Col([
                        dbc.Button(
                            "🗑️",
                            id={'type': 'btn-remover-med', 'index': i},
                            color="danger",
                            size="sm",
                            outline=True
                        )
                    ], md=2, className="text-end")
                ])
            ])
        ], className="mb-2")
        
        items.append(card)
    
    return items

# Callback para gerar prescrição
@callback(
    [Output('modal-prescricao-sucesso', 'is_open'),
     Output('prescricao-gerada-store', 'data'),
     Output('modal-prescricao-info', 'children')],
    Input('btn-gerar-prescricao', 'n_clicks'),
    [State('select-paciente-prescricao', 'value'),
     State('data-prescricao', 'date'),
     State('nome-medico', 'value'),
     State('crm-medico', 'value'),
     State('especialidade-medico', 'value'),
     State('medicamentos-store', 'data'),
     State('observacoes-prescricao', 'value')],
    prevent_initial_call=True
)
def generate_prescription(n_clicks, paciente_id, data_consulta, nome_medico, crm_medico, 
                         especialidade_medico, medicamentos, observacoes):
    """Gera a prescrição em PDF"""
    if not n_clicks or not paciente_id:
        return False, None, ""
    
    try:
        # Buscar dados do paciente
        paciente = db_manager.execute_query('''
            SELECT nome, cpf, data_nascimento, endereco 
            FROM pacientes WHERE id = ?
        ''', (paciente_id,)).iloc[0]
        
        # Preparar dados para o PDF
        prescription_data = {
            'clinic': {
                'name': 'ClinicCare - Centro Médico',
                'address': 'Av. Paulista, 1000 - Bela Vista - São Paulo/SP - CEP: 01310-100',
                'phone': '(11) 3456-7890',
                'email': 'contato@cliniccare.com.br'
            },
            'patient': {
                'name': paciente['nome'],
                'cpf': paciente['cpf'],
                'birth_date': paciente['data_nascimento'],
                'address': paciente['endereco']
            },
            'doctor': {
                'name': nome_medico,
                'crm': crm_medico,
                'specialty': especialidade_medico
            },
            'medications': medicamentos,
            'observations': observacoes or "",
            'date': datetime.strptime(data_consulta, '%Y-%m-%d').strftime('%d/%m/%Y')
        }
        
        # Gerar PDF
        pdf_path = create_prescription_pdf(prescription_data)
        
        # Salvar no histórico (opcional - implementar tabela de prescrições)
        
        modal_info = html.Div([
            html.P(f"📄 Arquivo: {os.path.basename(pdf_path)}"),
            html.P(f"👤 Paciente: {paciente['nome']}"),
            html.P(f"📅 Data: {prescription_data['date']}")
        ])
        
        return True, {'pdf_path': pdf_path}, modal_info
        
    except Exception as e:
        modal_info = dbc.Alert(f"Erro ao gerar prescrição: {str(e)}", color="danger")
        return True, None, modal_info

@callback(
    Output('modal-prescricao-sucesso', 'is_open', allow_duplicate=True),
    Input('btn-fechar-modal', 'n_clicks'),
    prevent_initial_call=True
)
def close_modal(n_clicks):
    """Fecha o modal"""
    if n_clicks:
        return False
    return dash.no_update
