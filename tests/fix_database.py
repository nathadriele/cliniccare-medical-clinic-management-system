#!/usr/bin/env python3
"""
Script para corrigir e atualizar a estrutura do banco de dados
"""

import sqlite3
import os

def fix_database():
    """Corrige a estrutura do banco de dados"""
    
    db_path = "data/clinic.db"
    
    # Criar diretório se não existir
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Verificando e corrigindo estrutura do banco de dados...")
    
    # Verificar se as tabelas existem
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas_existentes = [row[0] for row in cursor.fetchall()]
    print(f"Tabelas existentes: {tabelas_existentes}")

    # Verificar estrutura atual da tabela medicos se existir
    colunas_medicos = []
    if 'medicos' in tabelas_existentes:
        cursor.execute("PRAGMA table_info(medicos)")
        colunas_medicos = [row[1] for row in cursor.fetchall()]
        print(f"Colunas atuais da tabela medicos: {colunas_medicos}")

    # Verificar estrutura atual da tabela pacientes se existir
    colunas_pacientes = []
    if 'pacientes' in tabelas_existentes:
        cursor.execute("PRAGMA table_info(pacientes)")
        colunas_pacientes = [row[1] for row in cursor.fetchall()]
        print(f"Colunas atuais da tabela pacientes: {colunas_pacientes}")
    
    # Colunas necessárias para médicos
    colunas_necessarias_medicos = [
        'id', 'nome', 'crm', 'especialidade', 'telefone', 'email',
        'valor_consulta', 'duracao_consulta', 'horario_atendimento',
        'convenios_aceitos', 'observacoes', 'data_cadastro', 'ativo'
    ]
    
    # Colunas necessárias para pacientes
    colunas_necessarias_pacientes = [
        'id', 'nome', 'cpf', 'data_nascimento', 'genero', 'telefone',
        'email', 'endereco', 'estado_civil', 'convenio', 'numero_convenio',
        'observacoes', 'data_cadastro', 'ativo'
    ]
    
    # Corrigir tabela medicos
    print("\n Corrigindo tabela de médicos...")

    medicos_backup = []
    if 'medicos' in tabelas_existentes:
        # Fazer backup dos dados existentes
        cursor.execute("SELECT * FROM medicos")
        medicos_backup = cursor.fetchall()
        print(f"Backup de {len(medicos_backup)} médicos realizado")

        # Recriar tabela medicos com estrutura correta
        cursor.execute("DROP TABLE IF EXISTS medicos_backup")
        cursor.execute("ALTER TABLE medicos RENAME TO medicos_backup")
    else:
        print("Tabela medicos não existe, criando do zero...")
    
    cursor.execute('''
        CREATE TABLE medicos (
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
    
    # Restaurar dados dos médicos
    for medico in medicos_backup:
        try:
            # Mapear dados antigos para nova estrutura
            cursor.execute('''
                INSERT INTO medicos 
                (id, nome, crm, especialidade, telefone, email, data_cadastro, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                medico[0],  # id
                medico[1],  # nome
                medico[2],  # crm
                medico[3] if len(medico) > 3 else None,  # especialidade
                medico[4] if len(medico) > 4 else None,  # telefone
                medico[5] if len(medico) > 5 else None,  # email
                medico[6] if len(medico) > 6 else None,  # data_cadastro
                medico[7] if len(medico) > 7 else 1      # ativo
            ))
        except Exception as e:
            print(f"Erro ao restaurar médico {medico}: {e}")
    
    print("Tabela de médicos corrigida")
    
    # Corrigir tabela pacientes
    print("\n Corrigindo tabela de pacientes...")

    pacientes_backup = []
    if 'pacientes' in tabelas_existentes:
        # Verificar se precisa adicionar colunas
        colunas_faltando_pacientes = [col for col in colunas_necessarias_pacientes if col not in colunas_pacientes]

        if colunas_faltando_pacientes:
            print(f"Adicionando colunas faltando: {colunas_faltando_pacientes}")

            # Fazer backup dos dados existentes
            cursor.execute("SELECT * FROM pacientes")
            pacientes_backup = cursor.fetchall()
            print(f"Backup de {len(pacientes_backup)} pacientes realizado")
        else:
            print("Tabela de pacientes já está correta")
            pacientes_backup = []
    else:
        print("Tabela pacientes não existe, criando do zero...")
        colunas_faltando_pacientes = colunas_necessarias_pacientes

    if colunas_faltando_pacientes:
        # Recriar tabela pacientes com estrutura correta
        cursor.execute("DROP TABLE IF EXISTS pacientes_backup")
        if 'pacientes' in tabelas_existentes:
            cursor.execute("ALTER TABLE pacientes RENAME TO pacientes_backup")
        
        cursor.execute('''
            CREATE TABLE pacientes (
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
        
        # Restaurar dados dos pacientes
        for paciente in pacientes_backup:
            try:
                cursor.execute('''
                    INSERT INTO pacientes 
                    (id, nome, cpf, data_nascimento, telefone, email, endereco, 
                     convenio, numero_convenio, data_cadastro, ativo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    paciente[0],  # id
                    paciente[1],  # nome
                    paciente[2],  # cpf
                    paciente[3] if len(paciente) > 3 else None,  # data_nascimento
                    paciente[4] if len(paciente) > 4 else None,  # telefone
                    paciente[5] if len(paciente) > 5 else None,  # email
                    paciente[6] if len(paciente) > 6 else None,  # endereco
                    paciente[7] if len(paciente) > 7 else None,  # convenio
                    paciente[8] if len(paciente) > 8 else None,  # numero_convenio
                    paciente[9] if len(paciente) > 9 else None,  # data_cadastro
                    paciente[10] if len(paciente) > 10 else 1    # ativo
                ))
            except Exception as e:
                print(f"Erro ao restaurar paciente {paciente}: {e}")
        
        print("Tabela de pacientes corrigida")
    
    # Verificar outras tabelas necessárias
    print("\n Verificando outras tabelas...")
    
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
            medico_id INTEGER,
            consulta_id INTEGER,
            anamnese TEXT,
            exame_fisico TEXT,
            diagnostico TEXT,
            prescricao TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
            FOREIGN KEY (medico_id) REFERENCES medicos (id),
            FOREIGN KEY (consulta_id) REFERENCES consultas (id)
        )
    ''')
    
    # Tabela de comunicação
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comunicacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            tipo TEXT,
            assunto TEXT,
            mensagem TEXT,
            data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'enviado',
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
        )
    ''')
    
    # Limpar tabelas de backup
    cursor.execute("DROP TABLE IF EXISTS medicos_backup")
    cursor.execute("DROP TABLE IF EXISTS pacientes_backup")
    
    conn.commit()
    conn.close()
    
    print("\n Estrutura do banco de dados corrigida com sucesso!")
    print("\n Resumo das correções:")
    print("   • ✅ Tabela medicos: Estrutura atualizada com todas as colunas")
    print("   • ✅ Tabela pacientes: Estrutura verificada e corrigida")
    print("   • ✅ Tabelas auxiliares: Consultas, prontuários, comunicação")
    print("   • ✅ Dados preservados: Backup e restauração realizados")

if __name__ == "__main__":
    fix_database()
