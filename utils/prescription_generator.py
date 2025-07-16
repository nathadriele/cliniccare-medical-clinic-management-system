#!/usr/bin/env python3
"""
Sistema de Geração de Prescrições Médicas em PDF
Módulo para criar receitas médicas profissionais com formatação padrão
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import io

class PrescriptionGenerator:
    """Gerador de prescrições médicas em PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configura estilos personalizados para a prescrição"""
        
        # Estilo para cabeçalho da clínica
        self.styles.add(ParagraphStyle(
            name='ClinicHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            alignment=TA_CENTER,
            spaceAfter=6
        ))
        
        # Estilo para informações da clínica
        self.styles.add(ParagraphStyle(
            name='ClinicInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=20
        ))
        
        # Estilo para título da prescrição
        self.styles.add(ParagraphStyle(
            name='PrescriptionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            alignment=TA_CENTER,
            spaceAfter=15,
            spaceBefore=10
        ))
        
        # Estilo para dados do paciente
        self.styles.add(ParagraphStyle(
            name='PatientInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            spaceAfter=4
        ))
        
        # Estilo para medicamentos
        self.styles.add(ParagraphStyle(
            name='Medication',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=8,
            leftIndent=20
        ))
        
        # Estilo para observações
        self.styles.add(ParagraphStyle(
            name='Observations',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=6
        ))
        
        # Estilo para assinatura
        self.styles.add(ParagraphStyle(
            name='Signature',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#1f2937'),
            spaceBefore=30
        ))
    
    def generate_prescription(self, prescription_data, output_path=None):
        """
        Gera uma prescrição médica em PDF
        
        Args:
            prescription_data (dict): Dados da prescrição
            output_path (str): Caminho para salvar o PDF
            
        Returns:
            str: Caminho do arquivo gerado ou bytes do PDF
        """
        
        # Se não especificado, criar nome do arquivo
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            patient_name = prescription_data.get('patient_name', 'paciente').replace(' ', '_')
            output_path = f"prescricoes/receita_{patient_name}_{timestamp}.pdf"
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Construir conteúdo
        story = []
        
        # Cabeçalho da clínica
        story.extend(self._build_clinic_header(prescription_data))
        
        # Título da prescrição
        story.append(Paragraph("PRESCRIÇÃO MÉDICA", self.styles['PrescriptionTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        # Dados do paciente
        story.extend(self._build_patient_info(prescription_data))
        
        # Medicamentos prescritos
        story.extend(self._build_medications(prescription_data))
        
        # Observações
        story.extend(self._build_observations(prescription_data))
        
        # Assinatura do médico
        story.extend(self._build_signature(prescription_data))
        
        # Rodapé
        story.extend(self._build_footer(prescription_data))
        
        # Gerar PDF
        doc.build(story)
        
        return output_path
    
    def _build_clinic_header(self, data):
        """Constrói o cabeçalho da clínica"""
        elements = []
        
        clinic_info = data.get('clinic', {})
        
        # Nome da clínica
        clinic_name = clinic_info.get('name', 'ClinicCare - Sistema de Gestão Médica')
        elements.append(Paragraph(clinic_name, self.styles['ClinicHeader']))
        
        # Informações da clínica
        address = clinic_info.get('address', 'Rua das Flores, 123 - Centro - São Paulo/SP')
        phone = clinic_info.get('phone', '(11) 3456-7890')
        email = clinic_info.get('email', 'contato@cliniccare.com.br')
        
        clinic_details = f"{address}<br/>Tel: {phone} | Email: {email}"
        elements.append(Paragraph(clinic_details, self.styles['ClinicInfo']))
        
        # Linha separadora
        line_table = Table([['_' * 80]], colWidths=[18*cm])
        line_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#e5e7eb')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.3*cm))
        
        return elements
    
    def _build_patient_info(self, data):
        """Constrói as informações do paciente"""
        elements = []
        
        patient = data.get('patient', {})
        
        # Dados do paciente em tabela
        patient_data = [
            ['Paciente:', patient.get('name', 'Nome do Paciente')],
            ['CPF:', patient.get('cpf', '000.000.000-00')],
            ['Data de Nascimento:', patient.get('birth_date', '01/01/1990')],
            ['Endereço:', patient.get('address', 'Endereço do paciente')]
        ]
        
        patient_table = Table(patient_data, colWidths=[3*cm, 15*cm])
        patient_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        elements.append(patient_table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _build_medications(self, data):
        """Constrói a lista de medicamentos"""
        elements = []
        
        medications = data.get('medications', [])
        
        if medications:
            # Título da seção
            elements.append(Paragraph("MEDICAMENTOS PRESCRITOS:", self.styles['PatientInfo']))
            elements.append(Spacer(1, 0.2*cm))
            
            # Lista de medicamentos
            for i, med in enumerate(medications, 1):
                med_text = f"{i}. <b>{med.get('name', 'Nome do medicamento')}</b>"
                
                if med.get('dosage'):
                    med_text += f" - {med['dosage']}"
                
                if med.get('frequency'):
                    med_text += f"<br/>   <i>Posologia:</i> {med['frequency']}"
                
                if med.get('duration'):
                    med_text += f"<br/>   <i>Duração:</i> {med['duration']}"
                
                if med.get('instructions'):
                    med_text += f"<br/>   <i>Instruções:</i> {med['instructions']}"
                
                elements.append(Paragraph(med_text, self.styles['Medication']))
        
        else:
            # Caso não haja medicamentos
            elements.append(Paragraph("Nenhum medicamento prescrito.", self.styles['Medication']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _build_observations(self, data):
        """Constrói as observações médicas"""
        elements = []
        
        observations = data.get('observations', '')
        
        if observations:
            elements.append(Paragraph("OBSERVAÇÕES:", self.styles['PatientInfo']))
            elements.append(Paragraph(observations, self.styles['Observations']))
            elements.append(Spacer(1, 0.3*cm))
        
        return elements
    
    def _build_signature(self, data):
        """Constrói a área de assinatura"""
        elements = []
        
        doctor = data.get('doctor', {})
        
        # Data da prescrição
        prescription_date = data.get('date', datetime.now().strftime('%d/%m/%Y'))
        elements.append(Paragraph(f"São Paulo, {prescription_date}", self.styles['Signature']))
        
        elements.append(Spacer(1, 1*cm))
        
        # Linha para assinatura
        signature_table = Table([['_' * 40]], colWidths=[8*cm])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        
        # Centralizar tabela à direita
        signature_wrapper = Table([[signature_table]], colWidths=[18*cm])
        signature_wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ]))
        
        elements.append(signature_wrapper)
        elements.append(Spacer(1, 0.2*cm))
        
        # Nome e CRM do médico
        doctor_name = doctor.get('name', 'Dr. Nome do Médico')
        doctor_crm = doctor.get('crm', 'CRM/SP 123456')
        doctor_specialty = doctor.get('specialty', 'Especialidade Médica')
        
        doctor_info = f"{doctor_name}<br/>{doctor_crm}<br/>{doctor_specialty}"
        doctor_paragraph = Paragraph(doctor_info, self.styles['Signature'])
        
        elements.append(doctor_paragraph)
        
        return elements
    
    def _build_footer(self, data):
        """Constrói o rodapé da prescrição"""
        elements = []
        
        elements.append(Spacer(1, 1*cm))
        
        # Aviso legal
        legal_notice = (
            "<i>Esta prescrição é válida em todo território nacional e tem validade de 30 dias "
            "a partir da data de emissão. Medicamentos controlados seguem legislação específica.</i>"
        )
        
        footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER,
            spaceBefore=20
        )
        
        elements.append(Paragraph(legal_notice, footer_style))
        
        return elements

# Função utilitária para uso direto
def create_prescription_pdf(prescription_data, output_path=None):
    """
    Função utilitária para criar uma prescrição PDF
    
    Args:
        prescription_data (dict): Dados da prescrição
        output_path (str): Caminho para salvar o PDF
        
    Returns:
        str: Caminho do arquivo gerado
    """
    generator = PrescriptionGenerator()
    return generator.generate_prescription(prescription_data, output_path)

# Exemplo de uso
if __name__ == "__main__":
    # Dados de exemplo
    sample_data = {
        'clinic': {
            'name': 'ClinicCare - Centro Médico',
            'address': 'Av. Paulista, 1000 - Bela Vista - São Paulo/SP - CEP: 01310-100',
            'phone': '(11) 3456-7890',
            'email': 'contato@cliniccare.com.br'
        },
        'patient': {
            'name': 'João Silva Santos',
            'cpf': '123.456.789-00',
            'birth_date': '15/03/1985',
            'address': 'Rua das Flores, 456 - Vila Madalena - São Paulo/SP'
        },
        'doctor': {
            'name': 'Dra. Maria Oliveira',
            'crm': 'CRM/SP 123456',
            'specialty': 'Clínica Geral'
        },
        'medications': [
            {
                'name': 'Paracetamol 500mg',
                'dosage': '1 comprimido',
                'frequency': 'A cada 6 horas',
                'duration': '7 dias',
                'instructions': 'Tomar com água, preferencialmente após as refeições'
            },
            {
                'name': 'Ibuprofeno 400mg',
                'dosage': '1 comprimido',
                'frequency': 'A cada 8 horas',
                'duration': '5 dias',
                'instructions': 'Tomar com alimento para evitar irritação gástrica'
            }
        ],
        'observations': 'Retornar em 7 dias para reavaliação. Em caso de piora dos sintomas, procurar atendimento médico imediatamente.',
        'date': '14/07/2025'
    }
    
    # Gerar prescrição de exemplo
    pdf_path = create_prescription_pdf(sample_data)
    print(f"Prescrição gerada: {pdf_path}")
