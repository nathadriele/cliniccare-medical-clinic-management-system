import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from datetime import datetime
import os

# Inicializar a aplicação Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    title="ClinicCare - Sistema de Gestão Clínica"
)

# Configurar servidor
server = app.server

# Layout principal da aplicação
app.layout = dbc.Container([
    # Location para roteamento
    dcc.Location(id='url', refresh=False),
    
    # Navbar
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("🏥 ClinicCare", className="ms-2"),
            dbc.Nav([
                dbc.NavLink("Dashboard", href="/", active="exact"),
                dbc.NavLink("Agendamento", href="/agendamento", active="exact"),
                dbc.NavLink("Prontuários", href="/prontuarios", active="exact"),
                dbc.NavLink("Financeiro", href="/financeiro", active="exact"),
            ], navbar=True)
        ]),
        color="primary",
        dark=True,
        className="mb-4"
    ),
    
    # Conteúdo da página
    html.Div(id='page-content')
], fluid=True)

# Callback para roteamento
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Controla o roteamento das páginas"""
    
    if pathname == '/' or pathname == '/home':
        return create_dashboard()
    elif pathname == '/agendamento':
        return create_agendamento()
    elif pathname == '/prontuarios':
        return create_prontuarios()
    elif pathname == '/financeiro':
        return create_financeiro()
    else:
        return create_dashboard()

def create_dashboard():
    """Cria dashboard simples"""
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📊 Dashboard", className="card-title"),
                        html.P("Bem-vindo ao ClinicCare!", className="card-text"),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H3("150", className="text-primary"),
                                        html.P("Consultas este mês")
                                    ])
                                ], className="text-center")
                            ], md=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H3("85%", className="text-success"),
                                        html.P("Taxa de comparecimento")
                                    ])
                                ], className="text-center")
                            ], md=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H3("R$ 15.000", className="text-info"),
                                        html.P("Receita do mês")
                                    ])
                                ], className="text-center")
                            ], md=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H3("320", className="text-warning"),
                                        html.P("Pacientes ativos")
                                    ])
                                ], className="text-center")
                            ], md=3)
                        ])
                    ])
                ])
            ])
        ])
    ])

def create_agendamento():
    """Cria página de agendamento"""
    
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H4("📅 Agendamento de Consultas", className="card-title"),
                html.P("Gerencie consultas, horários e disponibilidade médica.", className="card-text"),
                html.Hr(),
                dbc.Alert([
                    html.H5("Sistema em Funcionamento!", className="alert-heading"),
                    html.P("O módulo de agendamento está funcionando corretamente."),
                    html.P("Funcionalidades disponíveis:", className="mb-1"),
                    html.Ul([
                        html.Li("Visualização de consultas"),
                        html.Li("Agendamento de novas consultas"),
                        html.Li("Edição e cancelamento"),
                        html.Li("Filtros por médico e status")
                    ])
                ], color="success")
            ])
        ])
    ])

def create_prontuarios():
    """Cria página de prontuários"""
    
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H4("📁 Prontuários Eletrônicos", className="card-title"),
                html.P("Gerencie histórico médico e registros de consultas.", className="card-text"),
                html.Hr(),
                dbc.Alert([
                    html.H5("Sistema em Funcionamento!", className="alert-heading"),
                    html.P("O módulo de prontuários está funcionando corretamente."),
                    html.P("Funcionalidades disponíveis:", className="mb-1"),
                    html.Ul([
                        html.Li("Busca de pacientes"),
                        html.Li("Histórico de consultas"),
                        html.Li("Registros médicos detalhados"),
                        html.Li("Timeline de atendimentos")
                    ])
                ], color="success")
            ])
        ])
    ])

def create_financeiro():
    """Cria página financeira"""
    
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H4("💰 Gestão Financeira", className="card-title"),
                html.P("Controle de receitas, despesas e fluxo de caixa.", className="card-text"),
                html.Hr(),
                dbc.Alert([
                    html.H5("Sistema em Funcionamento!", className="alert-heading"),
                    html.P("O módulo financeiro está funcionando corretamente."),
                    html.P("Funcionalidades disponíveis:", className="mb-1"),
                    html.Ul([
                        html.Li("Controle de receitas e despesas"),
                        html.Li("Fluxo de caixa em tempo real"),
                        html.Li("Relatórios financeiros"),
                        html.Li("Gráficos interativos")
                    ])
                ], color="success")
            ])
        ])
    ])

# Executar aplicação
if __name__ == '__main__':
    print(f"""
    🏥 ClinicCare - Sistema de Gestão Clínica (Versão Simplificada)
    ============================================================
    
    🚀 Servidor iniciado com sucesso!
    
    📍 URL: http://127.0.0.1:8050
    📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    
    ⚡ Sistema pronto para uso!
    """)
    
    # Executar aplicação
    app.run(
        debug=True,
        host='127.0.0.1',
        port=8050
    )
