#!/usr/bin/env python3
"""
Módulo de Validação de Integridade Relacional
Sistema para verificar vínculos entre médicos, pacientes e consultas
"""

import re
import sys
import os

# Adicionar o diretório pai ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_manager import db_manager

class RelationalIntegrityChecker:
    """Classe para verificação de integridade referencial"""
    
    @staticmethod
    def validate_cpf(cpf):
        """
        Valida CPF brasileiro
        
        Args:
            cpf (str): CPF a ser validado
            
        Returns:
            bool: True se válido, False caso contrário
        """
        if not cpf:
            return False
            
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
            
        # Verifica se não são todos iguais
        if cpf == cpf[0] * 11:
            return False
            
        # Calcula primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Calcula segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verifica se os dígitos estão corretos
        return cpf[9] == str(digito1) and cpf[10] == str(digito2)
    
    @staticmethod
    def validate_crm(crm):
        """
        Valida formato de CRM
        
        Args:
            crm (str): CRM a ser validado
            
        Returns:
            bool: True se válido, False caso contrário
        """
        if not crm:
            return False
            
        # Padrão: CRM/UF NNNNNN (ex: CRM/SP 123456)
        pattern = r'^CRM/[A-Z]{2}\s+\d{4,6}$'
        return bool(re.match(pattern, crm.upper()))
    
    @staticmethod
    def format_cpf(cpf):
        """
        Formata CPF para exibição
        
        Args:
            cpf (str): CPF sem formatação
            
        Returns:
            str: CPF formatado (000.000.000-00)
        """
        if not cpf:
            return ""
            
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    @staticmethod
    def clean_cpf(cpf):
        """
        Remove formatação do CPF
        
        Args:
            cpf (str): CPF formatado
            
        Returns:
            str: CPF apenas com números
        """
        return re.sub(r'[^0-9]', '', cpf) if cpf else ""
    
    @staticmethod
    def check_patient_dependencies(patient_id):
        """
        Verifica se paciente tem vínculos que impedem exclusão
        
        Args:
            patient_id (int): ID do paciente
            
        Returns:
            dict: {
                'can_delete': bool,
                'dependencies': list,
                'message': str
            }
        """
        try:
            dependencies = []
            
            # Verificar consultas
            consultas = db_manager.execute_query('''
                SELECT COUNT(*) as total FROM consultas 
                WHERE paciente_id = ?
            ''', (patient_id,))
            
            if consultas.iloc[0]['total'] > 0:
                dependencies.append(f"{consultas.iloc[0]['total']} consulta(s)")
            
            # Verificar prontuários
            prontuarios = db_manager.execute_query('''
                SELECT COUNT(*) as total FROM prontuarios 
                WHERE paciente_id = ?
            ''', (patient_id,))
            
            if prontuarios.iloc[0]['total'] > 0:
                dependencies.append(f"{prontuarios.iloc[0]['total']} prontuário(s)")
            
            # Verificar comunicações
            comunicacoes = db_manager.execute_query('''
                SELECT COUNT(*) as total FROM comunicacao 
                WHERE paciente_id = ?
            ''', (patient_id,))
            
            if comunicacoes.iloc[0]['total'] > 0:
                dependencies.append(f"{comunicacoes.iloc[0]['total']} comunicação(ões)")
            
            can_delete = len(dependencies) == 0
            
            if can_delete:
                message = "Paciente pode ser excluído com segurança."
            else:
                deps_text = ", ".join(dependencies)
                message = f"Não é possível excluir o paciente, pois está vinculado a: {deps_text}."
            
            return {
                'can_delete': can_delete,
                'dependencies': dependencies,
                'message': message
            }
            
        except Exception as e:
            return {
                'can_delete': False,
                'dependencies': [],
                'message': f"Erro ao verificar dependências: {str(e)}"
            }
    
    @staticmethod
    def check_doctor_dependencies(doctor_id):
        """
        Verifica se médico tem vínculos que impedem exclusão
        
        Args:
            doctor_id (int): ID do médico
            
        Returns:
            dict: {
                'can_delete': bool,
                'dependencies': list,
                'message': str
            }
        """
        try:
            dependencies = []
            
            # Verificar consultas
            consultas = db_manager.execute_query('''
                SELECT COUNT(*) as total FROM consultas 
                WHERE medico_id = ?
            ''', (doctor_id,))
            
            if consultas.iloc[0]['total'] > 0:
                dependencies.append(f"{consultas.iloc[0]['total']} consulta(s)")
            
            # Verificar prontuários
            prontuarios = db_manager.execute_query('''
                SELECT COUNT(*) as total FROM prontuarios 
                WHERE medico_id = ?
            ''', (doctor_id,))
            
            if prontuarios.iloc[0]['total'] > 0:
                dependencies.append(f"{prontuarios.iloc[0]['total']} prontuário(s)")
            
            can_delete = len(dependencies) == 0
            
            if can_delete:
                message = "Médico pode ser excluído com segurança."
            else:
                deps_text = ", ".join(dependencies)
                message = f"Não é possível excluir o médico, pois está vinculado a: {deps_text}."
            
            return {
                'can_delete': can_delete,
                'dependencies': dependencies,
                'message': message
            }
            
        except Exception as e:
            return {
                'can_delete': False,
                'dependencies': [],
                'message': f"Erro ao verificar dependências: {str(e)}"
            }
    
    @staticmethod
    def check_cpf_uniqueness(cpf, exclude_id=None):
        """
        Verifica se CPF já existe no banco
        
        Args:
            cpf (str): CPF a ser verificado
            exclude_id (int): ID a ser excluído da verificação (para edição)
            
        Returns:
            bool: True se único, False se duplicado
        """
        try:
            clean_cpf = RelationalIntegrityChecker.clean_cpf(cpf)
            
            if exclude_id:
                result = db_manager.execute_query('''
                    SELECT COUNT(*) as total FROM pacientes 
                    WHERE cpf = ? AND id != ?
                ''', (clean_cpf, exclude_id))
            else:
                result = db_manager.execute_query('''
                    SELECT COUNT(*) as total FROM pacientes 
                    WHERE cpf = ?
                ''', (clean_cpf,))
            
            return result.iloc[0]['total'] == 0
            
        except Exception:
            return False
    
    @staticmethod
    def check_crm_uniqueness(crm, exclude_id=None):
        """
        Verifica se CRM já existe no banco
        
        Args:
            crm (str): CRM a ser verificado
            exclude_id (int): ID a ser excluído da verificação (para edição)
            
        Returns:
            bool: True se único, False se duplicado
        """
        try:
            if exclude_id:
                result = db_manager.execute_query('''
                    SELECT COUNT(*) as total FROM medicos 
                    WHERE crm = ? AND id != ?
                ''', (crm.upper(), exclude_id))
            else:
                result = db_manager.execute_query('''
                    SELECT COUNT(*) as total FROM medicos 
                    WHERE crm = ?
                ''', (crm.upper(),))
            
            return result.iloc[0]['total'] == 0
            
        except Exception:
            return False
    
    @staticmethod
    def validate_patient_data(data, exclude_id=None):
        """
        Valida dados completos do paciente
        
        Args:
            data (dict): Dados do paciente
            exclude_id (int): ID para exclusão na verificação de duplicidade
            
        Returns:
            dict: {
                'valid': bool,
                'errors': list
            }
        """
        errors = []
        
        # Validar campos obrigatórios
        required_fields = ['nome', 'cpf', 'data_nascimento', 'genero', 'telefone']
        for field in required_fields:
            if not data.get(field, '').strip():
                field_names = {
                    'nome': 'Nome completo',
                    'cpf': 'CPF',
                    'data_nascimento': 'Data de nascimento',
                    'genero': 'Gênero',
                    'telefone': 'Telefone'
                }
                errors.append(f"{field_names[field]} é obrigatório.")
        
        # Validar CPF
        if data.get('cpf'):
            if not RelationalIntegrityChecker.validate_cpf(data['cpf']):
                errors.append("CPF inválido.")
            elif not RelationalIntegrityChecker.check_cpf_uniqueness(data['cpf'], exclude_id):
                errors.append("CPF já cadastrado no sistema.")
        
        # Validar email se fornecido
        if data.get('email'):
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors.append("Email inválido.")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_doctor_data(data, exclude_id=None):
        """
        Valida dados completos do médico
        
        Args:
            data (dict): Dados do médico
            exclude_id (int): ID para exclusão na verificação de duplicidade
            
        Returns:
            dict: {
                'valid': bool,
                'errors': list
            }
        """
        errors = []
        
        # Validar campos obrigatórios
        required_fields = ['nome', 'crm', 'especialidade', 'telefone']
        for field in required_fields:
            if not data.get(field, '').strip():
                field_names = {
                    'nome': 'Nome completo',
                    'crm': 'CRM',
                    'especialidade': 'Especialidade',
                    'telefone': 'Telefone'
                }
                errors.append(f"{field_names[field]} é obrigatório.")
        
        # Validar CRM
        if data.get('crm'):
            if not RelationalIntegrityChecker.validate_crm(data['crm']):
                errors.append("CRM inválido. Use o formato: CRM/UF 123456")
            elif not RelationalIntegrityChecker.check_crm_uniqueness(data['crm'], exclude_id):
                errors.append("CRM já cadastrado no sistema.")
        
        # Validar email se fornecido
        if data.get('email'):
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors.append("Email inválido.")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

# Instância global para uso direto
integrity_checker = RelationalIntegrityChecker()

# Funções utilitárias para uso direto
def can_delete_patient(patient_id):
    """Verifica se paciente pode ser excluído"""
    return integrity_checker.check_patient_dependencies(patient_id)

def can_delete_doctor(doctor_id):
    """Verifica se médico pode ser excluído"""
    return integrity_checker.check_doctor_dependencies(doctor_id)

def validate_patient(data, exclude_id=None):
    """Valida dados do paciente"""
    return integrity_checker.validate_patient_data(data, exclude_id)

def validate_doctor(data, exclude_id=None):
    """Valida dados do médico"""
    return integrity_checker.validate_doctor_data(data, exclude_id)

if __name__ == "__main__":
    # Testes do módulo
    print("🧪 Testando validações...")
    
    # Teste CPF
    cpfs_teste = ["12345678901", "000.000.000-00", "123.456.789-09"]
    for cpf in cpfs_teste:
        valido = integrity_checker.validate_cpf(cpf)
        print(f"CPF {cpf}: {'✅ Válido' if valido else '❌ Inválido'}")
    
    # Teste CRM
    crms_teste = ["CRM/SP 123456", "crm/rj 98765", "CRM123456"]
    for crm in crms_teste:
        valido = integrity_checker.validate_crm(crm)
        print(f"CRM {crm}: {'✅ Válido' if valido else '❌ Inválido'}")
    
    print("✅ Testes concluídos!")
