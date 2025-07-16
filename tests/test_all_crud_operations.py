#!/usr/bin/env python3
"""
Script para testar todas as operações CRUD do sistema
"""

from utils.db_manager import db_manager
from datetime import datetime, date
import traceback

def test_medico_crud():
    """Testa operações CRUD de médicos"""
    print("🏥 Testando CRUD de Médicos...")
    
    try:
        # CREATE - Inserir médico
        medico_id = db_manager.execute_insert('''
            INSERT INTO medicos
            (nome, crm, especialidade, telefone, email, valor_consulta,
             duracao_consulta, horario_atendimento, convenios_aceitos,
             observacoes, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("Dr. Teste Silva", "CRM/SP 999999", "Cardiologia", "11999887766",
              "teste@email.com", 300.00, 45, "Segunda a sexta: 8h às 17h",
              "Unimed, Bradesco", "Médico de teste", True, datetime.now().isoformat()))
        
        print(f"   ✅ CREATE: Médico inserido com ID {medico_id}")
        
        # READ - Buscar médico
        medicos = db_manager.execute_query("SELECT * FROM medicos WHERE id = ?", (medico_id,))
        if not medicos.empty:
            medico = medicos.iloc[0]
            print(f"   ✅ READ: Médico encontrado - {medico['nome']}")
        else:
            print("   ❌ READ: Médico não encontrado")
            return False
        
        # UPDATE - Atualizar médico
        db_manager.execute_insert('''
            UPDATE medicos SET nome = ?, valor_consulta = ? WHERE id = ?
        ''', ("Dr. Teste Silva Atualizado", 350.00, medico_id))
        
        # Verificar atualização
        medicos_updated = db_manager.execute_query("SELECT * FROM medicos WHERE id = ?", (medico_id,))
        if not medicos_updated.empty and medicos_updated.iloc[0]['valor_consulta'] == 350.00:
            print("   ✅ UPDATE: Médico atualizado com sucesso")
        else:
            print("   ❌ UPDATE: Falha na atualização")
            return False
        
        # DELETE - Excluir médico
        db_manager.execute_insert("DELETE FROM medicos WHERE id = ?", (medico_id,))
        
        # Verificar exclusão
        medicos_deleted = db_manager.execute_query("SELECT * FROM medicos WHERE id = ?", (medico_id,))
        if medicos_deleted.empty:
            print("   ✅ DELETE: Médico excluído com sucesso")
        else:
            print("   ❌ DELETE: Falha na exclusão")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        traceback.print_exc()
        return False

def test_paciente_crud():
    """Testa operações CRUD de pacientes"""
    print("\n👥 Testando CRUD de Pacientes...")
    
    try:
        # CREATE - Inserir paciente
        paciente_id = db_manager.execute_insert('''
            INSERT INTO pacientes
            (nome, cpf, data_nascimento, genero, telefone, email,
             endereco, estado_civil, observacoes, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("Maria Teste Santos", "99988877766", "1985-05-15", "Feminino",
              "11988776655", "maria.teste@email.com", "Rua Teste, 123",
              "Casada", "Paciente de teste", True, datetime.now().isoformat()))
        
        print(f"   ✅ CREATE: Paciente inserido com ID {paciente_id}")
        
        # READ - Buscar paciente
        pacientes = db_manager.execute_query("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        if not pacientes.empty:
            paciente = pacientes.iloc[0]
            print(f"   ✅ READ: Paciente encontrado - {paciente['nome']}")
        else:
            print("   ❌ READ: Paciente não encontrado")
            return False
        
        # UPDATE - Atualizar paciente
        db_manager.execute_insert('''
            UPDATE pacientes SET nome = ?, telefone = ? WHERE id = ?
        ''', ("Maria Teste Santos Atualizada", "11999888777", paciente_id))
        
        # Verificar atualização
        pacientes_updated = db_manager.execute_query("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        if not pacientes_updated.empty and pacientes_updated.iloc[0]['telefone'] == "11999888777":
            print("   ✅ UPDATE: Paciente atualizado com sucesso")
        else:
            print("   ❌ UPDATE: Falha na atualização")
            return False
        
        # DELETE - Excluir paciente
        db_manager.execute_insert("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
        
        # Verificar exclusão
        pacientes_deleted = db_manager.execute_query("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        if pacientes_deleted.empty:
            print("   ✅ DELETE: Paciente excluído com sucesso")
        else:
            print("   ❌ DELETE: Falha na exclusão")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        traceback.print_exc()
        return False

def test_consulta_crud():
    """Testa operações CRUD de consultas"""
    print("\n📅 Testando CRUD de Consultas...")
    
    try:
        # Primeiro, criar médico e paciente para a consulta
        medico_id = db_manager.execute_insert('''
            INSERT INTO medicos (nome, crm, especialidade, ativo)
            VALUES (?, ?, ?, ?)
        ''', ("Dr. Consulta Teste", "CRM/SP 888888", "Clínico Geral", True))
        
        paciente_id = db_manager.execute_insert('''
            INSERT INTO pacientes (nome, cpf, ativo)
            VALUES (?, ?, ?)
        ''', ("Paciente Consulta Teste", "88877766655", True))
        
        # CREATE - Inserir consulta
        consulta_id = db_manager.execute_insert('''
            INSERT INTO consultas
            (paciente_id, medico_id, data_consulta, status, valor, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (paciente_id, medico_id, "2024-12-20 10:00:00", "agendado", 200.00, "Consulta de teste"))
        
        print(f"   ✅ CREATE: Consulta inserida com ID {consulta_id}")
        
        # READ - Buscar consulta
        consultas = db_manager.execute_query("SELECT * FROM consultas WHERE id = ?", (consulta_id,))
        if not consultas.empty:
            consulta = consultas.iloc[0]
            print(f"   ✅ READ: Consulta encontrada - Status: {consulta['status']}")
        else:
            print("   ❌ READ: Consulta não encontrada")
            return False
        
        # UPDATE - Atualizar consulta
        db_manager.execute_insert('''
            UPDATE consultas SET status = ?, valor = ? WHERE id = ?
        ''', ("confirmado", 250.00, consulta_id))
        
        # Verificar atualização
        consultas_updated = db_manager.execute_query("SELECT * FROM consultas WHERE id = ?", (consulta_id,))
        if not consultas_updated.empty and consultas_updated.iloc[0]['status'] == "confirmado":
            print("   ✅ UPDATE: Consulta atualizada com sucesso")
        else:
            print("   ❌ UPDATE: Falha na atualização")
            return False
        
        # Limpar dados de teste
        db_manager.execute_insert("DELETE FROM consultas WHERE id = ?", (consulta_id,))
        db_manager.execute_insert("DELETE FROM medicos WHERE id = ?", (medico_id,))
        db_manager.execute_insert("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
        
        print("   ✅ DELETE: Dados de teste limpos")
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        traceback.print_exc()
        return False

def test_database_structure():
    """Testa a estrutura do banco de dados"""
    print("\n🗄️ Testando Estrutura do Banco...")
    
    try:
        # Verificar tabelas principais
        tables = ['medicos', 'pacientes', 'consultas', 'prontuarios', 'comunicacao']
        
        for table in tables:
            result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result.iloc[0]['count']
            print(f"   ✅ Tabela {table}: {count} registros")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏥 ClinicCare - Teste Completo de CRUD")
    print("=" * 60)
    
    # Executar todos os testes
    tests = [
        ("Estrutura do Banco", test_database_structure),
        ("CRUD Médicos", test_medico_crud),
        ("CRUD Pacientes", test_paciente_crud),
        ("CRUD Consultas", test_consulta_crud)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 Resumo dos Testes:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   • {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM! O sistema está funcionando corretamente.")
        print("✅ O erro de SQL foi corrigido com sucesso!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM. Verifique os erros acima.")
    
    print("\n💡 Próximos passos:")
    print("   1. Teste o cadastro de médicos na interface web")
    print("   2. Teste o cadastro de pacientes na interface web")
    print("   3. Verifique se não há mais erros de SQL em outras páginas")
