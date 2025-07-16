import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime

def create_navbar():
    """Cria a navbar superior do sistema"""
    
    navbar = dbc.Navbar(
        dbc.Container([
            dbc.Row([
                # Título da página atual
                dbc.Col([
                    html.H4(id="page-title", className="mb-0 text-primary")
                ], width="auto"),
                
                # Espaçador
                dbc.Col(width=True),
                
                # Informações do usuário e controles
                dbc.Col([
                    dbc.Row([
                        # Data atual
                        dbc.Col([
                            html.Div([
                                html.Small(
                                    datetime.now().strftime("%d/%m/%Y"),
                                    className="text-muted d-block"
                                )
                            ], className="text-center")
                        ], width="auto", className="me-3"),

                        # Controle de tema
                        dbc.Col([
                            html.Div([
                                html.I(id="theme-icon-navbar", className="fas fa-moon me-1"),
                                html.Small(id="theme-text-navbar", children="Escuro", className="d-none d-lg-inline")
                            ],
                            id="theme-toggle-navbar",
                            className="theme-toggle-navbar d-flex align-items-center px-2 py-1 rounded cursor-pointer",
                            style={
                                "border": "1px solid #dee2e6",
                                "background": "transparent",
                                "transition": "all 0.3s ease",
                                "cursor": "pointer"
                            })
                        ], width="auto", className="me-3"),

                        # Notificações
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-bell me-1"),
                                dbc.Badge("3", color="danger", pill=True, className="position-absolute top-0 start-100 translate-middle")
                            ],
                            color="light",
                            outline=True,
                            size="sm",
                            id="notifications-btn",
                            className="position-relative me-2",
                            style={"min-width": "40px"})
                        ], width="auto"),

                        # Menu do usuário
                        dbc.Col([
                            dbc.DropdownMenu([
                                dbc.DropdownMenuItem([
                                    html.I(className="fas fa-user me-2"),
                                    "Perfil"
                                ]),
                                dbc.DropdownMenuItem([
                                    html.I(className="fas fa-cog me-2"),
                                    "Configurações"
                                ]),
                                dbc.DropdownMenuItem(divider=True),
                                dbc.DropdownMenuItem([
                                    html.I(className="fas fa-sign-out-alt me-2"),
                                    "Sair"
                                ]),
                            ],
                            label=[
                                html.I(className="fas fa-user-circle me-1"),
                                "Dr. Admin"
                            ],
                            color="primary",
                            size="sm")
                        ], width="auto"),
                    ], align="center", className="g-0")
                ], width="auto")
            ], align="center", className="w-100")
        ], fluid=True),
        color="light",
        className="shadow-sm mb-4 d-none d-md-block"
    )
    
    return navbar

def create_breadcrumb(items):
    """Cria breadcrumb de navegação"""
    
    breadcrumb_items = []
    for i, item in enumerate(items):
        if i == len(items) - 1:  # Último item (ativo)
            breadcrumb_items.append(
                dbc.BreadcrumbItem(item['label'], active=True)
            )
        else:
            breadcrumb_items.append(
                dbc.BreadcrumbItem(item['label'], href=item['href'])
            )
    
    return dbc.Breadcrumb(breadcrumb_items, className="bg-light p-2 rounded")

def create_page_header(title, subtitle=None, actions=None):
    """Cria cabeçalho padrão das páginas"""
    
    header_content = [
        dbc.Col([
            html.H2(title, className="mb-1"),
            html.P(subtitle, className="text-muted mb-0") if subtitle else None
        ], width=True)
    ]
    
    if actions:
        header_content.append(
            dbc.Col([
                dbc.ButtonGroup(actions, size="sm")
            ], width="auto")
        )
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row(header_content, align="center")
        ])
    ], className="mb-4 border-0 shadow-sm")

def create_stats_cards(stats):
    """Cria cards de estatísticas"""
    
    cards = []
    colors = ['primary', 'success', 'info', 'warning']
    
    for i, stat in enumerate(stats):
        color = colors[i % len(colors)]
        
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H3(stat['value'], className="mb-1"),
                            html.P(stat['label'], className="mb-0 small")
                        ], width=8),
                        dbc.Col([
                            html.I(className=f"fas {stat['icon']} fa-2x text-{color}")
                        ], width=4, className="text-end")
                    ])
                ])
            ], color=color, outline=True, className="h-100")
        ], md=3, sm=6, className="mb-3")
        
        cards.append(card)
    
    return dbc.Row(cards)

def create_loading_spinner(text="Carregando..."):
    """Cria spinner de carregamento"""
    
    return html.Div([
        dbc.Spinner(size="lg", color="primary"),
        html.P(text, className="mt-2 text-muted")
    ], className="text-center p-4")

def create_empty_state(title, description, icon="fas fa-inbox", action=None):
    """Cria estado vazio para listas/tabelas"""
    
    content = [
        html.I(className=f"{icon} fa-3x text-muted mb-3"),
        html.H5(title, className="text-muted"),
        html.P(description, className="text-muted mb-3")
    ]
    
    if action:
        content.append(action)
    
    return html.Div(content, className="text-center p-5")

def create_alert(message, color="info", dismissible=True):
    """Cria alerta personalizado"""
    
    return dbc.Alert(
        message,
        color=color,
        dismissable=dismissible,
        className="mb-3"
    )
