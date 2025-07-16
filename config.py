# Configurações do Sistema ClinicCare

import os

# Configurações do servidor
SERVER_CONFIG = {
    'host': os.getenv('HOST', '127.0.0.1'),
    'port': int(os.getenv('PORT', 8050)),
    'debug': os.getenv('DASH_DEBUG', 'False').lower() == 'true',
    'dev_tools_hot_reload': False,  # Desabilitado para evitar problemas de callbacks
    'dev_tools_ui': os.getenv('DASH_DEBUG', 'False').lower() == 'true'
}

# Configurações do banco de dados
DATABASE_CONFIG = {
    'path': 'data/clinic_system.db',
    'backup_enabled': True,
    'backup_interval_hours': 24
}

# Configurações da aplicação
APP_CONFIG = {
    'title': 'ClinicCare - Sistema de Gestão Clínica',
    'version': '1.0.0',
    'company': 'ClinicCare Solutions',
    'support_email': 'suporte@cliniccare.com'
}

# Configurações de interface
UI_CONFIG = {
    'theme': 'bootstrap',
    'sidebar_width': 2,
    'content_width': 10,
    'enable_mobile_navbar': True,
    'auto_refresh_interval': 30  # segundos
}

# Configurações de segurança
SECURITY_CONFIG = {
    'enable_auth': False,  # Para desenvolvimento
    'session_timeout': 3600,  # segundos
    'max_login_attempts': 3
}

# Configurações de comunicação
COMMUNICATION_CONFIG = {
    'enable_email': False,  # Para desenvolvimento
    'enable_sms': False,    # Para desenvolvimento
    'reminder_advance_days': 1,
    'reminder_time': '09:00'
}

# Configurações de relatórios
REPORTS_CONFIG = {
    'default_period_days': 30,
    'enable_pdf_export': True,
    'enable_excel_export': True,
    'max_records_per_report': 10000
}

# Configurações de logs
LOGGING_CONFIG = {
    'level': 'INFO',
    'file': 'logs/cliniccare.log',
    'max_size_mb': 10,
    'backup_count': 5
}
