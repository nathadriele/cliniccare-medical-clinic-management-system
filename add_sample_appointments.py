#!/usr/bin/env python3
"""
Script para adicionar consultas de exemplo para testar a visualização da agenda
"""

from utils.db_manager import db_manager
from datetime import datetime, timedelta
import random

def add_sample_appointments():
    """Adiciona consultas de exemplo para os próximos dias"""
    
    try:
        # Buscar pacientes e médicos existentes
        pacientes = db_manager.execute_query("SELECT id, nome FROM pacientes WHERE ativo = 1")
        medicos = db_manager.execute_query("SELECT id, nome FROM medicos WHERE ativo = 1")
        
        if pacientes.empty or medicos.empty:
            print("❌ Não há pacientes ou médicos ativos no sistema")
            return
        
        print(f"📋 Encontrados {len(pacientes)} pacientes e {len(medicos)} médicos")
        
        # Consultas de exemplo para os próximos 7 dias
        consultas_exemplo = []
        
        # Hoje
        hoje = datetime.now().date()
        consultas_exemplo.extend([
            {
                'data': hoje,
                'horario': '09:00',
                'status': 'confirmado',
                'valor': 150.00,
                'observacoes': 'Consulta de rotina'
            },
            {
                'data': hoje,
                'horario': '14:30',
                'status': 'agendado',
                'valor': 200.00,
                'observacoes': 'Primeira consulta'
            }
        ])
        
        # Amanhã
        amanha = hoje + timedelta(days=1)
        consultas_exemplo.extend([
            {
                'data': amanha,
                'horario': '08:00',
                'status': 'agendado',
                'valor': 180.00,
                'observacoes': 'Retorno'
            },
            {
                'data': amanha,
                'horario': '10:15',
                'status': 'confirmado',
                'valor': 220.00,
                'observacoes': 'Consulta especializada'
            },
            {
                'data': amanha,
                'horario': '16:00',
                'status': 'agendado',
                'valor': 150.00,
                'observacoes': 'Acompanhamento'
            }
        ])
        
        # Depois de amanhã
        depois_amanha = hoje + timedelta(days=2)
        consultas_exemplo.extend([
            {
                'data': depois_amanha,
                'horario': '09:30',
                'status': 'agendado',
                'valor': 170.00,
                'observacoes': 'Consulta preventiva'
            },
            {
                'data': depois_amanha,
                'horario': '15:45',
                'status': 'confirmado',
                'valor': 190.00,
                'observacoes': 'Exame de rotina'
            }
        ])
        
        # Próxima semana
        proxima_semana = hoje + timedelta(days=5)
        consultas_exemplo.extend([
            {
                'data': proxima_semana,
                'horario': '11:00',
                'status': 'agendado',
                'valor': 160.00,
                'observacoes': 'Consulta de acompanhamento'
            },
            {
                'data': proxima_semana,
                'horario': '14:00',
                'status': 'agendado',
                'valor': 200.00,
                'observacoes': 'Avaliação médica'
            }
        ])
        
        # Inserir consultas
        consultas_inseridas = 0
        
        for consulta in consultas_exemplo:
            # Selecionar paciente e médico aleatórios
            paciente = pacientes.sample(1).iloc[0]
            medico = medicos.sample(1).iloc[0]
            
            # Combinar data e horário
            data_consulta = f"{consulta['data']} {consulta['horario']}:00"
            
            # Verificar se já existe consulta neste horário
            existing = db_manager.execute_query('''
                SELECT COUNT(*) as total FROM consultas 
                WHERE medico_id = ? AND data_consulta = ?
            ''', (medico['id'], data_consulta))
            
            if existing.iloc[0]['total'] == 0:
                # Inserir consulta
                db_manager.execute_insert('''
                    INSERT INTO consultas 
                    (paciente_id, medico_id, data_consulta, valor, observacoes, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    paciente['id'],
                    medico['id'],
                    data_consulta,
                    consulta['valor'],
                    consulta['observacoes'],
                    consulta['status']
                ))
                
                consultas_inseridas += 1
                print(f"✅ Consulta inserida: {consulta['data']} {consulta['horario']} - {paciente['nome']} com Dr(a). {medico['nome']}")
            else:
                print(f"⚠️ Consulta já existe: {consulta['data']} {consulta['horario']} - Dr(a). {medico['nome']}")
        
        print(f"\n🎉 {consultas_inseridas} consultas de exemplo adicionadas com sucesso!")
        
        # Mostrar total de consultas
        total = db_manager.execute_query("SELECT COUNT(*) as total FROM consultas")
        print(f"📊 Total de consultas no sistema: {total.iloc[0]['total']}")
        
    except Exception as e:
        print(f"❌ Erro ao adicionar consultas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🏥 ClinicCare - Adicionando Consultas de Exemplo")
    print("=" * 60)
    add_sample_appointments()
