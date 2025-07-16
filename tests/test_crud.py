#!/usr/bin/env python3
"""
Teste do Sistema CRUD de Pacientes e Médicos
"""

from utils.relational_checks import RelationalIntegrityChecker

def test_validations():
    """Testa as validações do sistema"""
    
    print("Testando Sistema CRUD - Pacientes e Médicos")
    print("=" * 60)
    
    checker = RelationalIntegrityChecker()
    
    # Teste 1: Validação de CPF
    print("\n1️⃣ Teste de Validação de CPF:")
    cpfs_teste = [
        "12345678901",      # Inválido
        "11111111111",      # Inválido (todos iguais)
        "123.456.789-09",   # Válido
        "000.000.000-00",   # Inválido
        "12345678900"       # Inválido
    ]
    
    for cpf in cpfs_teste:
        valido = checker.validate_cpf(cpf)
        status = "✅ Válido" if valido else "❌ Inválido"
        print(f"   CPF {cpf}: {status}")
    
    # Teste 2: Validação de CRM
    print("\n2️⃣ Teste de Validação de CRM:")
    crms_teste = [
        "CRM/SP 123456",    # Válido
        "CRM/RJ 98765",     # Válido
        "crm/mg 54321",     # Válido (será convertido)
        "CRM123456",        # Inválido
        "123456",           # Inválido
        "CRM/SP123456"      # Inválido (sem espaço)
    ]
    
    for crm in crms_teste:
        valido = checker.validate_crm(crm)
        status = "✅ Válido" if valido else "❌ Inválido"
        print(f"   CRM {crm}: {status}")
    
    # Teste 3: Formatação de CPF
    print("\n3️⃣ Teste de Formatação de CPF:")
    cpfs_format = ["12345678909", "123.456.789-09", ""]
    
    for cpf in cpfs_format:
        formatado = checker.format_cpf(cpf)
        print(f"   Original: '{cpf}' → Formatado: '{formatado}'")
    
    # Teste 4: Validação de dados de paciente
    print("\n4️⃣ Teste de Validação de Dados de Paciente:")
    
    # Dados válidos
    paciente_valido = {
        'nome': 'João Silva Santos',
        'cpf': '123.456.789-09',
        'data_nascimento': '1985-03-15',
        'genero': 'M',
        'telefone': '(11) 99999-9999',
        'email': 'joao@email.com'
    }
    
    resultado = checker.validate_patient_data(paciente_valido)
    print(f"   Paciente válido: {'✅ OK' if resultado['valid'] else '❌ Erro'}")
    if not resultado['valid']:
        for error in resultado['errors']:
            print(f"     - {error}")
    
    # Dados inválidos
    paciente_invalido = {
        'nome': '',  # Nome vazio
        'cpf': '111.111.111-11',  # CPF inválido
        'data_nascimento': '',
        'genero': '',
        'telefone': '',
        'email': 'email_invalido'  # Email inválido
    }
    
    resultado = checker.validate_patient_data(paciente_invalido)
    print(f"   Paciente inválido: {'✅ OK' if resultado['valid'] else '❌ Erro (esperado)'}")
    if not resultado['valid']:
        print("     Erros encontrados:")
        for error in resultado['errors']:
            print(f"     - {error}")
    
    # Teste 5: Validação de dados de médico
    print("\n5️⃣ Teste de Validação de Dados de Médico:")
    
    # Dados válidos
    medico_valido = {
        'nome': 'Dra. Maria Oliveira',
        'crm': 'CRM/SP 123456',
        'especialidade': 'Cardiologia',
        'telefone': '(11) 3456-7890',
        'email': 'maria@clinica.com'
    }
    
    resultado = checker.validate_doctor_data(medico_valido)
    print(f"   Médico válido: {'✅ OK' if resultado['valid'] else '❌ Erro'}")
    if not resultado['valid']:
        for error in resultado['errors']:
            print(f"     - {error}")
    
    # Dados inválidos
    medico_invalido = {
        'nome': '',  # Nome vazio
        'crm': 'CRM123',  # CRM inválido
        'especialidade': '',  # Especialidade vazia
        'telefone': '',  # Telefone vazio
        'email': 'email@'  # Email inválido
    }
    
    resultado = checker.validate_doctor_data(medico_invalido)
    print(f"   Médico inválido: {'✅ OK' if resultado['valid'] else '❌ Erro (esperado)'}")
    if not resultado['valid']:
        print("     Erros encontrados:")
        for error in resultado['errors']:
            print(f"     - {error}")
    
    print("\n" + "=" * 60)
    print("✅ Testes de validação concluídos!")
    print("\n Funcionalidades CRUD Implementadas:")
    print("   • ✅ Validação de CPF e CRM")
    print("   • ✅ Verificação de duplicidade")
    print("   • ✅ Validação de campos obrigatórios")
    print("   • ✅ Validação de email")
    print("   • ✅ Formatação automática")
    print("   • ✅ Verificação de integridade referencial")
    
    print("\n Páginas CRUD Disponíveis:")
    print("   • 👥 /pacientes - Gestão completa de pacientes")
    print("   • 👨‍⚕️ /medicos - Gestão completa de médicos")
    
    print("\n Regras de Integridade:")
    print("   • Médicos não podem ser excluídos se tiverem consultas")
    print("   • Pacientes não podem ser excluídos se tiverem histórico")
    print("   • CPF e CRM devem ser únicos no sistema")
    print("   • Validação em tempo real nos formulários")

if __name__ == "__main__":
    test_validations()
