#!/usr/bin/env python3
"""
Script para verificar a saúde geral do sistema e identificar possíveis problemas
"""

import os
import re
from utils.db_manager import db_manager

def check_database_consistency():
    """Verifica consistência do banco de dados"""
    print("🗄️ Verificando consistência do banco de dados...")
    
    issues = []
    
    try:
        # Verificar se todas as tabelas existem
        expected_tables = ['medicos', 'pacientes', 'consultas', 'prontuarios', 'comunicacao']
        
        for table in expected_tables:
            try:
                result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                count = result.iloc[0]['count']
                print(f"   ✅ Tabela {table}: {count} registros")
            except Exception as e:
                issues.append(f"Tabela {table}: {e}")
                print(f"   ❌ Tabela {table}: ERRO - {e}")
        
        # Verificar integridade referencial básica
        try:
            # Consultas com médicos inexistentes
            orphan_consultas_medicos = db_manager.execute_query('''
                SELECT COUNT(*) as count FROM consultas c
                LEFT JOIN medicos m ON c.medico_id = m.id
                WHERE m.id IS NULL
            ''')
            
            if orphan_consultas_medicos.iloc[0]['count'] > 0:
                issues.append(f"Consultas com médicos inexistentes: {orphan_consultas_medicos.iloc[0]['count']}")
            else:
                print("   ✅ Integridade referencial consultas-médicos: OK")
            
            # Consultas com pacientes inexistentes
            orphan_consultas_pacientes = db_manager.execute_query('''
                SELECT COUNT(*) as count FROM consultas c
                LEFT JOIN pacientes p ON c.paciente_id = p.id
                WHERE p.id IS NULL
            ''')
            
            if orphan_consultas_pacientes.iloc[0]['count'] > 0:
                issues.append(f"Consultas com pacientes inexistentes: {orphan_consultas_pacientes.iloc[0]['count']}")
            else:
                print("   ✅ Integridade referencial consultas-pacientes: OK")
                
        except Exception as e:
            issues.append(f"Erro ao verificar integridade referencial: {e}")
    
    except Exception as e:
        issues.append(f"Erro geral na verificação do banco: {e}")
    
    return issues

def check_code_patterns():
    """Verifica padrões problemáticos no código"""
    print("\n🔍 Verificando padrões de código...")
    
    issues = []
    
    # Diretórios para verificar
    directories = ['pages', 'utils', 'components']
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        for filename in os.listdir(directory):
            if filename.endswith('.py'):
                filepath = os.path.join(directory, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar uso incorreto de execute_query para INSERT/UPDATE/DELETE
                    incorrect_patterns = [
                        (r'execute_query.*INSERT', 'execute_query usado para INSERT'),
                        (r'execute_query.*UPDATE', 'execute_query usado para UPDATE'),
                        (r'execute_query.*DELETE', 'execute_query usado para DELETE')
                    ]
                    
                    for pattern, description in incorrect_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            issues.append(f"{filepath}: {description} - {len(matches)} ocorrência(s)")
                    
                    # Verificar imports problemáticos
                    if 'from utils.db_manager import db_manager' in content:
                        print(f"   ✅ {filepath}: Import correto do db_manager")
                    elif 'db_manager' in content and 'import' in content:
                        issues.append(f"{filepath}: Possível import incorreto do db_manager")
                
                except Exception as e:
                    issues.append(f"Erro ao ler {filepath}: {e}")
    
    return issues

def check_table_structures():
    """Verifica se as estruturas das tabelas estão corretas"""
    print("\n📋 Verificando estruturas das tabelas...")
    
    issues = []
    
    # Estruturas esperadas
    expected_structures = {
        'medicos': [
            'id', 'nome', 'crm', 'especialidade', 'telefone', 'email',
            'valor_consulta', 'duracao_consulta', 'horario_atendimento',
            'convenios_aceitos', 'observacoes', 'data_cadastro', 'ativo'
        ],
        'pacientes': [
            'id', 'nome', 'cpf', 'data_nascimento', 'genero', 'telefone',
            'email', 'endereco', 'estado_civil', 'convenio', 'numero_convenio',
            'observacoes', 'data_cadastro', 'ativo'
        ],
        'consultas': [
            'id', 'paciente_id', 'medico_id', 'data_consulta', 'status',
            'valor', 'observacoes', 'data_criacao'
        ]
    }
    
    for table_name, expected_columns in expected_structures.items():
        try:
            # Obter estrutura atual da tabela
            result = db_manager.execute_query(f"PRAGMA table_info({table_name})")
            actual_columns = result['name'].tolist()
            
            # Verificar colunas faltando
            missing_columns = [col for col in expected_columns if col not in actual_columns]
            if missing_columns:
                issues.append(f"Tabela {table_name}: Colunas faltando - {missing_columns}")
            else:
                print(f"   ✅ Tabela {table_name}: Estrutura completa ({len(actual_columns)} colunas)")
            
            # Verificar colunas extras (não é necessariamente um problema)
            extra_columns = [col for col in actual_columns if col not in expected_columns]
            if extra_columns:
                print(f"   ℹ️ Tabela {table_name}: Colunas extras - {extra_columns}")
        
        except Exception as e:
            issues.append(f"Erro ao verificar estrutura da tabela {table_name}: {e}")
    
    return issues

def check_file_permissions():
    """Verifica permissões de arquivos importantes"""
    print("\n🔐 Verificando permissões de arquivos...")
    
    issues = []
    
    important_files = [
        'data/clinic_system.db',
        'app.py',
        'utils/db_manager.py'
    ]
    
    for filepath in important_files:
        try:
            if os.path.exists(filepath):
                if os.access(filepath, os.R_OK):
                    print(f"   ✅ {filepath}: Leitura OK")
                else:
                    issues.append(f"{filepath}: Sem permissão de leitura")
                
                if filepath.endswith('.db'):
                    if os.access(filepath, os.W_OK):
                        print(f"   ✅ {filepath}: Escrita OK")
                    else:
                        issues.append(f"{filepath}: Sem permissão de escrita")
            else:
                issues.append(f"{filepath}: Arquivo não encontrado")
        
        except Exception as e:
            issues.append(f"Erro ao verificar {filepath}: {e}")
    
    return issues

def main():
    """Função principal"""
    print("🏥 ClinicCare - Verificação de Saúde do Sistema")
    print("=" * 60)
    
    all_issues = []
    
    # Executar todas as verificações
    checks = [
        ("Consistência do Banco de Dados", check_database_consistency),
        ("Padrões de Código", check_code_patterns),
        ("Estruturas das Tabelas", check_table_structures),
        ("Permissões de Arquivos", check_file_permissions)
    ]
    
    for check_name, check_func in checks:
        try:
            issues = check_func()
            all_issues.extend(issues)
        except Exception as e:
            all_issues.append(f"Erro na verificação {check_name}: {e}")
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 Relatório Final:")
    
    if not all_issues:
        print("🎉 SISTEMA SAUDÁVEL! Nenhum problema encontrado.")
        print("✅ Todas as verificações passaram com sucesso.")
    else:
        print(f"⚠️ {len(all_issues)} problema(s) encontrado(s):")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
    
    print("\n💡 Recomendações:")
    print("   • Teste regularmente as funcionalidades principais")
    print("   • Mantenha backups regulares do banco de dados")
    print("   • Monitore logs de erro durante o uso")
    print("   • Execute este script periodicamente")

if __name__ == "__main__":
    main()
