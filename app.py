import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import datetime
import os
from config import SERVER_CONFIG, APP_CONFIG

# Importar componentes
from components.sidebar import create_sidebar, create_mobile_navbar
from components.navbar import create_navbar

# Importar páginas
try:
    from pages import home, agendamento, pacientes, medicos, prontuarios, prescricoes, financeiro, convenios, comunicacao, relatorios
    print("✅ Todas as páginas importadas com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar páginas: {e}")
    # Importar páginas individualmente para debug
    try:
        from pages import home
        print("✅ Home importado")
    except Exception as e:
        print(f"❌ Erro no home: {e}")

    try:
        from pages import agendamento
        print("✅ Agendamento importado")
    except Exception as e:
        print(f"❌ Erro no agendamento: {e}")

    try:
        from pages import prontuarios
        print("✅ Prontuários importado")
    except Exception as e:
        print(f"❌ Erro nos prontuários: {e}")

    try:
        from pages import financeiro
        print("✅ Financeiro importado")
    except Exception as e:
        print(f"❌ Erro no financeiro: {e}")

    try:
        from pages import comunicacao
        print("✅ Comunicação importado")
    except Exception as e:
        print(f"❌ Erro na comunicação: {e}")

    try:
        from pages import relatorios
        print("✅ Relatórios importado")
    except Exception as e:
        print(f"❌ Erro nos relatórios: {e}")

# Inicializar a aplicação Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    title=APP_CONFIG['title'],
    update_title=None
)

# Configurar servidor
server = app.server

# Layout principal da aplicação
app.layout = dbc.Container([
    # Store para dados globais
    dcc.Store(id='session-store'),
    dcc.Store(id='theme-store', data='light'),

    # Location para roteamento
    dcc.Location(id='url', refresh=False),



    # Navbar mobile
    create_mobile_navbar(),
    
    # Layout principal
    dbc.Row([
        # Sidebar
        dbc.Col([
            create_sidebar()
        ], md=2, className="d-none d-md-block p-0"),
        
        # Conteúdo principal
        dbc.Col([
            # Navbar desktop
            create_navbar(),
            
            # Conteúdo da página
            html.Div(id='page-content', className="fade-in")
        ], md=10, className="p-0")
    ], className="g-0"),
    
    # Footer
    html.Footer([
        dbc.Container([
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.P([
                        "© 2024 ClinicCare Nathalia Adriele - Sistema de Gestão Clínica | ",
                        html.A("Suporte", href="mailto:suporte@cliniccare.com", className="text-decoration-none"),
                        " | Versão 1.0.0"
                    ], className="text-muted small mb-0")
                ], className="text-center")
            ])
        ])
    ], className="mt-5")
], fluid=True, className="p-0")

# Callback para roteamento
@app.callback(
    [Output('page-content', 'children'),
     Output('page-title', 'children')],
    Input('url', 'pathname')
)
def display_page(pathname):
    """Controla o roteamento das páginas"""
    
    if pathname == '/' or pathname == '/home':
        return home.create_layout(), "Visão Geral"
    elif pathname == '/agendamento':
        return agendamento.create_layout(), "Agendamento"
    elif pathname == '/pacientes':
        return pacientes.create_layout(), "Pacientes"
    elif pathname == '/medicos':
        return medicos.create_layout(), "Médicos"
    elif pathname == '/prontuarios':
        return prontuarios.create_layout(), "Prontuários"
    elif pathname == '/prescricoes':
        return prescricoes.create_layout(), "Prescrições"
    elif pathname == '/financeiro':
        return financeiro.create_layout(), "Financeiro"
    elif pathname == '/convenios':
        return convenios.create_layout(), "Convênios"
    elif pathname == '/comunicacao':
        return comunicacao.create_layout(), "Comunicação"
    elif pathname == '/relatorios':
        return relatorios.create_layout(), "Relatórios"
    elif pathname == '/pacientes':
        return create_page_pacientes(), "Pacientes"
    elif pathname == '/medicos':
        return create_page_medicos(), "Médicos"
    elif pathname == '/configuracoes':
        return create_page_configuracoes(), "Configurações"
    else:
        return create_page_404(), "Página não encontrada"

def create_page_pacientes():
    """Cria página de gerenciamento de pacientes"""
    
    return html.Div([
        dbc.Alert([
            html.H4("👥 Gerenciamento de Pacientes", className="alert-heading"),
            html.P("Esta funcionalidade está em desenvolvimento."),
            html.Hr(),
            html.P("Em breve você poderá cadastrar, editar e gerenciar todos os pacientes da clínica.", className="mb-0")
        ], color="info")
    ])

def create_page_medicos():
    """Cria página de gerenciamento de médicos"""
    
    return html.Div([
        dbc.Alert([
            html.H4("👨‍⚕️ Gerenciamento de Médicos", className="alert-heading"),
            html.P("Esta funcionalidade está em desenvolvimento."),
            html.Hr(),
            html.P("Em breve você poderá cadastrar, editar e gerenciar todos os médicos da clínica.", className="mb-0")
        ], color="info")
    ])

def create_page_configuracoes():
    """Cria página de configurações"""
    
    return html.Div([
        dbc.Alert([
            html.H4("⚙️ Configurações do Sistema", className="alert-heading"),
            html.P("Esta funcionalidade está em desenvolvimento."),
            html.Hr(),
            html.P("Em breve você poderá configurar preferências, usuários, backup e outras configurações.", className="mb-0")
        ], color="info")
    ])

def create_page_404():
    """Cria página de erro 404"""
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("404", className="display-1 text-muted"),
                    html.H3("Página não encontrada"),
                    html.P("A página que você está procurando não existe.", className="text-muted"),
                    dbc.Button([
                        html.I(className="fas fa-home me-2"),
                        "Voltar à Visão Geral"
                    ], href="/", color="primary")
                ], className="text-center")
            ], md=6, className="mx-auto")
        ], className="justify-content-center", style={"min-height": "60vh"})
    ], className="d-flex align-items-center")

# Callback para toggle da sidebar mobile
@app.callback(
    Output('sidebar', 'className'),
    Input('sidebar-toggle', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks):
    """Toggle da sidebar em dispositivos móveis"""

    if n_clicks and n_clicks % 2 == 1:
        return "sidebar show"
    return "sidebar"

# Callback para controle de tema
@app.callback(
    [Output('theme-store', 'data'),
     Output('theme-icon-navbar', 'className'),
     Output('theme-text-navbar', 'children')],
    Input('theme-toggle-navbar', 'n_clicks'),
    State('theme-store', 'data'),
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme):
    """Alterna entre tema claro e escuro"""
    if n_clicks:
        new_theme = 'dark' if current_theme == 'light' else 'light'
        icon_class = 'fas fa-sun text-warning' if new_theme == 'dark' else 'fas fa-moon text-primary'
        text = 'Claro' if new_theme == 'dark' else 'Escuro'
        return new_theme, icon_class, text

    return current_theme, 'fas fa-moon text-primary', 'Escuro'

# Callback para aplicar o tema
app.clientside_callback(
    """
    function(theme) {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
        return '';
    }
    """,
    Output('session-store', 'data'),
    Input('theme-store', 'data'),
    prevent_initial_call=True
)

# Callback duplicado removido - o título já é atualizado no callback display_page

# Função para inicializar dados de exemplo
def init_sample_data():
    """Inicializa dados de exemplo se necessário"""
    
    try:
        from utils.db_manager import db_manager
        
        # Verificar se já existem dados
        pacientes = db_manager.execute_query("SELECT COUNT(*) as total FROM pacientes")
        
        if pacientes.iloc[0]['total'] == 0:
            print("Inicializando dados de exemplo...")
            # Os dados de exemplo já são criados no db_manager
            print("Dados de exemplo criados com sucesso!")
        else:
            print(f"Sistema já possui {pacientes.iloc[0]['total']} pacientes cadastrados.")
            
    except Exception as e:
        print(f"Erro ao inicializar dados: {str(e)}")

# Executar aplicação
if __name__ == '__main__':
    # Criar diretório de dados se não existir
    os.makedirs('data', exist_ok=True)
    
    # Inicializar dados de exemplo
    init_sample_data()
    
    # Configurações do servidor
    debug_mode = SERVER_CONFIG['debug']
    port = SERVER_CONFIG['port']
    host = SERVER_CONFIG['host']
    
    print(f"""
    🏥 ClinicCare - Sistema de Gestão Clínica
    ========================================
    
    🚀 Servidor iniciado com sucesso!
    
    📍 URL: http://{host}:{port}
    🔧 Debug: {'Ativado' if debug_mode else 'Desativado'}
    📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    
    📋 Funcionalidades disponíveis:
    • Dashboard com KPIs em tempo real
    • Agendamento de consultas
    • Prontuários eletrônicos
    • Prescrições médicas em PDF
    • Gestão financeira
    • Gestão de convênios
    • Comunicação com pacientes
    • Relatórios e análises
    
    ⚡ Sistema pronto para uso!
    """)
    
    # Executar aplicação
    app.run(
        debug=debug_mode,
        host=host,
        port=port,
        dev_tools_hot_reload=SERVER_CONFIG['dev_tools_hot_reload'],
        dev_tools_ui=SERVER_CONFIG['dev_tools_ui']
    )
