#!/usr/bin/env python3
"""
Script para testar o cadastro de médicos
"""

from utils.db_manager import db_manager
from datetime import datetime

def test_medico_cadastro():
    """Testa o cadastro de um médico"""
    
    print("Testando cadastro de médico...")
    
    # Dados de teste
    nome = "Dr. João Silva"
    crm = "CRM/SP 123456"
    especialidade = "Cardiologia"
    telefone = "11999887766"
    email = "joao.silva@email.com"
    valor_consulta = 250.00
    duracao_consulta = 45
    horario_atendimento = "Segunda a sexta: 8h às 17h"
    convenios_aceitos = "Unimed, Bradesco Saúde"
    observacoes = "Especialista em cardiologia preventiva"
    ativo = True
    data_cadastro = datetime.now()
    
    try:
        # Tentar inserir o médico
        medico_id = db_manager.execute_insert('''
            INSERT INTO medicos
            (nome, crm, especialidade, telefone, email, valor_consulta,
             duracao_consulta, horario_atendimento, convenios_aceitos,
             observacoes, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, crm, especialidade, telefone, email, valor_consulta,
              duracao_consulta, horario_atendimento, convenios_aceitos,
              observacoes, ativo, data_cadastro))
        
        print("✅ Médico cadastrado com sucesso!")
        
        # Verificar se foi inserido
        medicos_df = db_manager.execute_query("SELECT * FROM medicos WHERE crm = ?", (crm,))
        if not medicos_df.empty:
            medico = medicos_df.iloc[0]
            print(f"Médico encontrado: {medico['nome']} - {medico['crm']}")
            print(f"Email: {medico['email']}")
            print(f"Valor consulta: R$ {medico['valor_consulta']}")
            print(f"Duração: {medico['duracao_consulta']} minutos")
        else:
            print("❌ Médico não encontrado após inserção")
            
    except Exception as e:
        print(f"❌ Erro ao cadastrar médico: {e}")
        return False
    
    return True

def test_paciente_cadastro():
    """Testa o cadastro de um paciente"""
    
    print("\n Testando cadastro de paciente...")
    
    # Dados de teste
    nome = "Maria Santos"
    cpf = "12345678901"
    data_nascimento = "1985-05-15"
    genero = "Feminino"
    telefone = "11988776655"
    email = "maria.santos@email.com"
    endereco = "Rua das Flores, 123 - São Paulo/SP"
    estado_civil = "Casada"
    observacoes = "Paciente com histórico de hipertensão"
    ativo = True
    data_cadastro = datetime.now()
    
    try:
        # Tentar inserir o paciente
        paciente_id = db_manager.execute_insert('''
            INSERT INTO pacientes
            (nome, cpf, data_nascimento, genero, telefone, email,
             endereco, estado_civil, observacoes, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, cpf, data_nascimento, genero, telefone, email,
              endereco, estado_civil, observacoes, ativo, data_cadastro))
        
        print("✅ Paciente cadastrado com sucesso!")
        
        # Verificar se foi inserido
        pacientes_df = db_manager.execute_query("SELECT * FROM pacientes WHERE cpf = ?", (cpf,))
        if not pacientes_df.empty:
            paciente = pacientes_df.iloc[0]
            print(f"Paciente encontrado: {paciente['nome']} - {paciente['cpf']}")
            print(f"Email: {paciente['email']}")
            print(f"Endereço: {paciente['endereco']}")
        else:
            print("❌ Paciente não encontrado após inserção")
            
    except Exception as e:
        print(f"❌ Erro ao cadastrar paciente: {e}")
        return False
    
    return True

def cleanup_test_data():
    """Remove os dados de teste"""
    print("\n🧹 Limpando dados de teste...")
    
    try:
        db_manager.execute_insert("DELETE FROM medicos WHERE crm = ?", ("CRM/SP 123456",))
        db_manager.execute_insert("DELETE FROM pacientes WHERE cpf = ?", ("12345678901",))
        print("✅ Dados de teste removidos")
    except Exception as e:
        print(f"⚠️ Erro ao limpar dados de teste: {e}")

if __name__ == "__main__":
    print("ClinicCare - Teste de Cadastros")
    print("=" * 50)
    
    # Testar cadastro de médico
    medico_ok = test_medico_cadastro()
    
    # Testar cadastro de paciente
    paciente_ok = test_paciente_cadastro()
    
    # Limpar dados de teste
    cleanup_test_data()
    
    print("\n" + "=" * 50)
    print("Resumo dos testes:")
    print(f"   • Cadastro de médico: {'✅ OK' if medico_ok else '❌ FALHOU'}")
    print(f"   • Cadastro de paciente: {'✅ OK' if paciente_ok else '❌ FALHOU'}")
    
    if medico_ok and paciente_ok:
        print("\n🎉 Todos os testes passaram! O sistema está funcionando corretamente.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os erros acima.")
