import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def create_sidebar():
    """Cria a sidebar de navegação do sistema"""
    
    sidebar = dbc.Nav(
        [
            # Header da sidebar
            html.Div([
                html.H3("🏥 ClinicCare", className="sidebar-header"),
                html.Hr(style={'border-color': 'rgba(255,255,255,0.2)'})
            ]),
            
            # Links de navegação
            dbc.NavLink([
                html.I(className="fas fa-home me-2"),
                "Visão Geral"
            ], href="/", active="exact", className="nav-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-calendar-alt me-2"),
                "Agendamento"
            ], href="/agendamento", active="exact", className="nav-link"),

            dbc.NavLink([
                html.I(className="fas fa-users me-2"),
                "Pacientes"
            ], href="/pacientes", active="exact", className="nav-link"),

            dbc.NavLink([
                html.I(className="fas fa-user-md me-2"),
                "Médicos"
            ], href="/medicos", active="exact", className="nav-link"),

            dbc.NavLink([
                html.I(className="fas fa-folder-open me-2"),
                "Prontuários"
            ], href="/prontuarios", active="exact", className="nav-link"),

            dbc.NavLink([
                html.I(className="fas fa-prescription-bottle-alt me-2"),
                "Prescrições"
            ], href="/prescricoes", active="exact", className="nav-link"),

            dbc.NavLink([
                html.I(className="fas fa-dollar-sign me-2"),
                "Financeiro"
            ], href="/financeiro", active="exact", className="nav-link"),

            dbc.NavLink([
                html.I(className="fas fa-handshake me-2"),
                "Convênios"
            ], href="/convenios", active="exact", className="nav-link"),

            dbc.NavLink([
                html.I(className="fas fa-comments me-2"),
                "Comunicação"
            ], href="/comunicacao", active="exact", className="nav-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-chart-bar me-2"),
                "Relatórios"
            ], href="/relatorios", active="exact", className="nav-link"),
            
            # Separador
            html.Hr(style={'border-color': 'rgba(255,255,255,0.2)', 'margin': '20px 10px'}),
            
            # Links secundários
            dbc.NavLink([
                html.I(className="fas fa-users me-2"),
                "Pacientes"
            ], href="/pacientes", active="exact", className="nav-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-user-md me-2"),
                "Médicos"
            ], href="/medicos", active="exact", className="nav-link"),
            
            dbc.NavLink([
                html.I(className="fas fa-cog me-2"),
                "Configurações"
            ], href="/configuracoes", active="exact", className="nav-link"),
        ],
        vertical=True,
        pills=True,
        className="sidebar"
    )
    
    return sidebar

def create_mobile_navbar():
    """Cria navbar para dispositivos móveis"""
    
    navbar = dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        html.I(className="fas fa-bars"),
                        id="sidebar-toggle",
                        color="primary",
                        outline=True,
                        size="sm"
                    )
                ], width="auto"),
                dbc.Col([
                    dbc.NavbarBrand("🏥 ClinicCare", className="ms-2")
                ], width=True),
            ], align="center", className="g-0"),
        ], fluid=True),
        color="light",
        className="d-md-none shadow-sm"
    )
    
    return navbar
