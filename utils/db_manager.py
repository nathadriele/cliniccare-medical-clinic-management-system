import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

class DatabaseManager:
    def __init__(self, db_path='data/clinic_system.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Cria conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de pacientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                data_nascimento DATE,
                genero TEXT,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                estado_civil TEXT,
                convenio TEXT,
                numero_convenio TEXT,
                observacoes TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabela de médicos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                crm TEXT UNIQUE NOT NULL,
                especialidade TEXT,
                telefone TEXT,
                email TEXT,
                valor_consulta DECIMAL(10,2),
                duracao_consulta INTEGER DEFAULT 30,
                horario_atendimento TEXT,
                convenios_aceitos TEXT,
                observacoes TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabela de consultas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                medico_id INTEGER,
                data_consulta DATETIME,
                status TEXT DEFAULT 'agendado',
                valor DECIMAL(10,2),
                observacoes TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                FOREIGN KEY (medico_id) REFERENCES medicos (id)
            )
        ''')
        
        # Tabela de prontuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prontuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                consulta_id INTEGER,
                anamnese TEXT,
                exame_fisico TEXT,
                diagnostico TEXT,
                prescricao TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                FOREIGN KEY (consulta_id) REFERENCES consultas (id)
            )
        ''')
        
        # Tabela financeira
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financeiro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL, -- 'receita' ou 'despesa'
                descricao TEXT NOT NULL,
                valor DECIMAL(10,2) NOT NULL,
                data_vencimento DATE,
                data_pagamento DATE,
                status TEXT DEFAULT 'pendente',
                categoria TEXT,
                consulta_id INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (consulta_id) REFERENCES consultas (id)
            )
        ''')
        
        # Tabela de comunicação
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comunicacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                tipo TEXT NOT NULL, -- 'lembrete', 'mensagem', 'notificacao'
                assunto TEXT,
                mensagem TEXT NOT NULL,
                data_envio TIMESTAMP,
                status TEXT DEFAULT 'pendente',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Inserir dados de exemplo se o banco estiver vazio
        self.insert_sample_data()
    
    def insert_sample_data(self):
        """Insere dados de exemplo para demonstração"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar se já existem dados
        cursor.execute("SELECT COUNT(*) FROM pacientes")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Inserir médicos de exemplo
        medicos_sample = [
            ('Dr. João Silva', 'CRM12345', 'Cardiologia', '(11) 99999-1111', 'joao@clinica.com'),
            ('Dra. Maria Santos', 'CRM67890', 'Dermatologia', '(11) 99999-2222', 'maria@clinica.com'),
            ('Dr. Pedro Costa', 'CRM11111', 'Clínico Geral', '(11) 99999-3333', 'pedro@clinica.com')
        ]
        
        cursor.executemany('''
            INSERT INTO medicos (nome, crm, especialidade, telefone, email)
            VALUES (?, ?, ?, ?, ?)
        ''', medicos_sample)
        
        # Inserir pacientes de exemplo
        pacientes_sample = [
            ('Ana Paula Silva', '123.456.789-01', '1985-03-15', '(11) 98888-1111', 'ana@email.com', 'Rua A, 123', 'Unimed', '123456'),
            ('Carlos Oliveira', '987.654.321-02', '1978-07-22', '(11) 98888-2222', 'carlos@email.com', 'Rua B, 456', 'Bradesco', '789012'),
            ('Fernanda Costa', '456.789.123-03', '1992-11-08', '(11) 98888-3333', 'fernanda@email.com', 'Rua C, 789', 'SulAmérica', '345678')
        ]
        
        cursor.executemany('''
            INSERT INTO pacientes (nome, cpf, data_nascimento, telefone, email, endereco, convenio, numero_convenio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', pacientes_sample)
        
        # Inserir consultas de exemplo
        consultas_sample = [
            (1, 1, '2024-01-15 09:00:00', 'confirmado', 150.00, 'Consulta de rotina'),
            (2, 2, '2024-01-16 14:30:00', 'agendado', 200.00, 'Avaliação dermatológica'),
            (3, 3, '2024-01-17 10:15:00', 'concluido', 120.00, 'Check-up geral')
        ]
        
        cursor.executemany('''
            INSERT INTO consultas (paciente_id, medico_id, data_consulta, status, valor, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', consultas_sample)
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=None):
        """Executa uma query e retorna os resultados"""
        conn = self.get_connection()
        try:
            if params:
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query(query, conn)
            return df
        finally:
            conn.close()
    
    def execute_insert(self, query, params):
        """Executa uma inserção no banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def execute_update(self, query, params):
        """Executa uma atualização no banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    # Métodos específicos para cada entidade
    def get_pacientes(self):
        """Retorna todos os pacientes ativos"""
        return self.execute_query("SELECT * FROM pacientes WHERE ativo = 1 ORDER BY nome")
    
    def get_medicos(self):
        """Retorna todos os médicos ativos"""
        return self.execute_query("SELECT * FROM medicos WHERE ativo = 1 ORDER BY nome")
    
    def get_consultas_periodo(self, data_inicio, data_fim):
        """Retorna consultas em um período específico"""
        query = '''
            SELECT c.*, p.nome as paciente_nome, m.nome as medico_nome, m.especialidade
            FROM consultas c
            JOIN pacientes p ON c.paciente_id = p.id
            JOIN medicos m ON c.medico_id = m.id
            WHERE DATE(c.data_consulta) BETWEEN ? AND ?
            ORDER BY c.data_consulta
        '''
        return self.execute_query(query, (data_inicio, data_fim))
    
    def get_kpis_dashboard(self):
        """Retorna KPIs para o dashboard"""
        try:
            hoje = datetime.now().date()
            inicio_mes = hoje.replace(day=1)

            # Total de consultas do mês
            consultas_mes = self.execute_query('''
                SELECT COUNT(*) as total FROM consultas
                WHERE DATE(data_consulta) >= ?
            ''', (inicio_mes,))

            # Taxa de comparecimento
            comparecimento = self.execute_query('''
                SELECT
                    COUNT(*) as total,
                    COALESCE(SUM(CASE WHEN status = 'concluido' THEN 1 ELSE 0 END), 0) as concluidas
                FROM consultas
                WHERE DATE(data_consulta) >= ?
            ''', (inicio_mes,))

            # Receita do mês
            receita_mes = self.execute_query('''
                SELECT COALESCE(SUM(valor), 0) as receita FROM consultas
                WHERE DATE(data_consulta) >= ? AND status = 'concluido'
            ''', (inicio_mes,))

            # Pacientes ativos
            pacientes_ativos = self.execute_query('SELECT COUNT(*) as total FROM pacientes WHERE ativo = 1')

            # Tratar valores None para evitar erros de divisão
            total_consultas = comparecimento.iloc[0]['total']
            consultas_concluidas = comparecimento.iloc[0]['concluidas']

            # Garantir que os valores sejam numéricos
            if total_consultas is None:
                total_consultas = 0
            if consultas_concluidas is None:
                consultas_concluidas = 0

            # Converter para int para garantir tipo correto
            total_consultas = int(total_consultas)
            consultas_concluidas = int(consultas_concluidas)

            # Calcular taxa de comparecimento com segurança
            if total_consultas > 0:
                taxa_comparecimento = (consultas_concluidas / total_consultas) * 100
            else:
                taxa_comparecimento = 0.0

            # Garantir que todos os valores sejam numéricos
            consultas_mes_val = consultas_mes.iloc[0]['total']
            receita_mes_val = receita_mes.iloc[0]['receita']
            pacientes_ativos_val = pacientes_ativos.iloc[0]['total']

            return {
                'consultas_mes': int(consultas_mes_val) if consultas_mes_val is not None else 0,
                'taxa_comparecimento': float(taxa_comparecimento),
                'receita_mes': float(receita_mes_val) if receita_mes_val is not None else 0.0,
                'pacientes_ativos': int(pacientes_ativos_val) if pacientes_ativos_val is not None else 0
            }

        except Exception as e:
            print(f"Erro em get_kpis_dashboard: {str(e)}")
            print(f"Tipo do erro: {type(e)}")
            # Retornar valores padrão em caso de erro
            return {
                'consultas_mes': 0,
                'taxa_comparecimento': 0.0,
                'receita_mes': 0.0,
                'pacientes_ativos': 0
            }

# Instância global do gerenciador de banco
db_manager = DatabaseManager()
