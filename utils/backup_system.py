#!/usr/bin/env python3
"""
Sistema de Backup Automático
Módulo para backup e restauração de dados do ClinicCare
"""

import os
import shutil
import sqlite3
import zipfile
import json
from datetime import datetime, timedelta
import schedule
import time
import threading
import logging

class BackupSystem:
    """Sistema de backup automático para o ClinicCare"""
    
    def __init__(self, db_path="data/clinic.db", backup_dir="backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.config_file = "backup_config.json"
        
        os.makedirs(backup_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/backup.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.config = self.load_config()
        
        self.scheduler_thread = None
        self.running = False
    
    def load_config(self):
        """Carrega configurações de backup"""
        default_config = {
            "auto_backup_enabled": True,
            "backup_frequency": "daily",
            "backup_time": "02:00",
            "max_backups": 30,
            "compress_backups": True,
            "include_logs": False,
            "email_notifications": False,
            "email_recipients": []
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            return default_config
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            return default_config
    
    def save_config(self):
        """Salva configurações de backup"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
    
    def create_backup(self, backup_type="manual"):
        """
        Cria um backup completo do sistema
        
        Args:
            backup_type (str): Tipo do backup (manual, scheduled)
            
        Returns:
            str: Caminho do arquivo de backup criado
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"cliniccare_backup_{backup_type}_{timestamp}"
            
            if self.config["compress_backups"]:
                backup_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
                return self._create_compressed_backup(backup_path, backup_name)
            else:
                backup_path = os.path.join(self.backup_dir, backup_name)
                return self._create_folder_backup(backup_path)
                
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            raise
    
    def _create_compressed_backup(self, backup_path, backup_name):
        """Cria backup comprimido em ZIP"""
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            if os.path.exists(self.db_path):
                zipf.write(self.db_path, f"{backup_name}/database/clinic.db")
                self.logger.info("Banco de dados incluído no backup")
            
            config_files = [
                "config.py",
                "backup_config.json",
                "requirements.txt"
            ]
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    zipf.write(config_file, f"{backup_name}/config/{config_file}")
            
            if os.path.exists("prescricoes"):
                for root, dirs, files in os.walk("prescricoes"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = file_path.replace("prescricoes", f"{backup_name}/prescricoes")
                        zipf.write(file_path, arc_path)
                self.logger.info("Prescrições incluídas no backup")
            
            if self.config["include_logs"] and os.path.exists("logs"):
                for root, dirs, files in os.walk("logs"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = file_path.replace("logs", f"{backup_name}/logs")
                        zipf.write(file_path, arc_path)
                self.logger.info("Logs incluídos no backup")
            
            metadata = {
                "backup_date": datetime.now().isoformat(),
                "backup_type": "compressed",
                "cliniccare_version": "1.0.0",
                "database_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
                "total_files": len(zipf.namelist())
            }
            
            zipf.writestr(f"{backup_name}/metadata.json", json.dumps(metadata, indent=2))
        
        if self._verify_backup(backup_path):
            self.logger.info(f"Backup criado com sucesso: {backup_path}")

            self._cleanup_old_backups()

            return backup_path
        else:
            raise Exception("Falha na verificação de integridade do backup")
    
    def _create_folder_backup(self, backup_path):
        """Cria backup em pasta"""
        
        os.makedirs(backup_path, exist_ok=True)
        
        if os.path.exists(self.db_path):
            db_backup_dir = os.path.join(backup_path, "database")
            os.makedirs(db_backup_dir, exist_ok=True)
            shutil.copy2(self.db_path, os.path.join(db_backup_dir, "clinic.db"))
            self.logger.info("✅ Banco de dados copiado")
        
        config_backup_dir = os.path.join(backup_path, "config")
        os.makedirs(config_backup_dir, exist_ok=True)
        
        config_files = ["config.py", "backup_config.json", "requirements.txt"]
        for config_file in config_files:
            if os.path.exists(config_file):
                shutil.copy2(config_file, config_backup_dir)
        
        if os.path.exists("prescricoes"):
            shutil.copytree("prescricoes", os.path.join(backup_path, "prescricoes"))
            self.logger.info("✅ Prescrições copiadas")
        
        if self.config["include_logs"] and os.path.exists("logs"):
            shutil.copytree("logs", os.path.join(backup_path, "logs"))
            self.logger.info("✅ Logs copiados")
        
        metadata = {
            "backup_date": datetime.now().isoformat(),
            "backup_type": "folder",
            "cliniccare_version": "1.0.0",
            "database_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        }
        
        with open(os.path.join(backup_path, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"✅ Backup criado com sucesso: {backup_path}")
        self._cleanup_old_backups()
        
        return backup_path
    
    def _verify_backup(self, backup_path):
        """Verifica integridade do backup"""
        try:
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    bad_files = zipf.testzip()
                    if bad_files:
                        self.logger.error(f"Arquivos corrompidos no backup: {bad_files}")
                        return False
                    
                    files = zipf.namelist()
                    has_metadata = any("metadata.json" in f for f in files)

                    return has_metadata
            else:
                has_metadata = os.path.exists(os.path.join(backup_path, "metadata.json"))

                return has_metadata
                
        except Exception as e:
            self.logger.error(f"Erro na verificação do backup: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Remove backups antigos baseado na configuração"""
        try:
            if not os.path.exists(self.backup_dir):
                return
            
            backups = []
            for file in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, file)
                if os.path.isfile(file_path) or os.path.isdir(file_path):
                    backups.append((file_path, os.path.getctime(file_path)))
            
            backups.sort(key=lambda x: x[1])
            
            max_backups = self.config.get("max_backups", 30)
            if len(backups) > max_backups:
                backups_to_remove = backups[:-max_backups]
                
                for backup_path, _ in backups_to_remove:
                    try:
                        if os.path.isfile(backup_path):
                            os.remove(backup_path)
                        else:
                            shutil.rmtree(backup_path)
                        
                        self.logger.info(f"🗑️ Backup antigo removido: {backup_path}")
                    except Exception as e:
                        self.logger.error(f"Erro ao remover backup antigo {backup_path}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Erro na limpeza de backups antigos: {e}")
    
    def restore_backup(self, backup_path):
        """
        Restaura um backup
        
        Args:
            backup_path (str): Caminho do backup a ser restaurado
            
        Returns:
            bool: True se restaurado com sucesso
        """
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup não encontrado: {backup_path}")
            
            safety_backup = self.create_backup("pre_restore")
            self.logger.info(f"Backup de segurança criado: {safety_backup}")
            
            if backup_path.endswith('.zip'):
                return self._restore_compressed_backup(backup_path)
            else:
                return self._restore_folder_backup(backup_path)
                
        except Exception as e:
            self.logger.error(f"Erro na restauração: {e}")
            return False
    
    def _restore_compressed_backup(self, backup_path):
        """Restaura backup comprimido"""
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            temp_dir = "temp_restore"
            zipf.extractall(temp_dir)
            
            backup_contents = os.listdir(temp_dir)
            backup_dir = os.path.join(temp_dir, backup_contents[0])
            
            db_backup = os.path.join(backup_dir, "database", "clinic.db")
            if os.path.exists(db_backup):
                if os.path.exists(self.db_path):
                    shutil.copy2(self.db_path, f"{self.db_path}.backup")
                
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                shutil.copy2(db_backup, self.db_path)
                self.logger.info("✅ Banco de dados restaurado")
            
            prescricoes_backup = os.path.join(backup_dir, "prescricoes")
            if os.path.exists(prescricoes_backup):
                if os.path.exists("prescricoes"):
                    shutil.rmtree("prescricoes")
                shutil.copytree(prescricoes_backup, "prescricoes")
                self.logger.info("✅ Prescrições restauradas")
            
            shutil.rmtree(temp_dir)
        
        self.logger.info("✅ Restauração concluída com sucesso")
        return True
    
    def _restore_folder_backup(self, backup_path):
        """Restaura backup em pasta"""
        
        db_backup = os.path.join(backup_path, "database", "clinic.db")
        if os.path.exists(db_backup):
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, f"{self.db_path}.backup")
            
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            shutil.copy2(db_backup, self.db_path)
            self.logger.info("✅ Banco de dados restaurado")
        
        prescricoes_backup = os.path.join(backup_path, "prescricoes")
        if os.path.exists(prescricoes_backup):
            if os.path.exists("prescricoes"):
                shutil.rmtree("prescricoes")
            shutil.copytree(prescricoes_backup, "prescricoes")
            self.logger.info("✅ Prescrições restauradas")
        
        self.logger.info("✅ Restauração concluída com sucesso")
        return True
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for item in os.listdir(self.backup_dir):
            item_path = os.path.join(self.backup_dir, item)
            
            try:
                metadata = None
                if item.endswith('.zip'):
                    with zipfile.ZipFile(item_path, 'r') as zipf:
                        metadata_files = [f for f in zipf.namelist() if f.endswith('metadata.json')]
                        if metadata_files:
                            metadata_content = zipf.read(metadata_files[0])
                            metadata = json.loads(metadata_content.decode())
                else:
                    metadata_path = os.path.join(item_path, 'metadata.json')
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                
                backup_info = {
                    'name': item,
                    'path': item_path,
                    'size': self._get_size(item_path),
                    'created': datetime.fromtimestamp(os.path.getctime(item_path)),
                    'metadata': metadata
                }
                
                backups.append(backup_info)
                
            except Exception as e:
                self.logger.error(f"Erro ao processar backup {item}: {e}")
        
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return backups
    
    def _get_size(self, path):
        """Calcula tamanho de arquivo ou diretório"""
        if os.path.isfile(path):
            return os.path.getsize(path)
        else:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            return total_size
    
    def start_scheduler(self):
        """Inicia o agendador de backups automáticos"""
        if not self.config["auto_backup_enabled"]:
            self.logger.info("Backup automático desabilitado")
            return
        
        self.running = True
        
        frequency = self.config["backup_frequency"]
        backup_time = self.config["backup_time"]
        
        if frequency == "daily":
            schedule.every().day.at(backup_time).do(self._scheduled_backup)
        elif frequency == "weekly":
            schedule.every().week.at(backup_time).do(self._scheduled_backup)
        elif frequency == "monthly":
            schedule.every().month.at(backup_time).do(self._scheduled_backup)
        
        self.logger.info(f"Agendador iniciado: backup {frequency} às {backup_time}")
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Para o agendador de backups"""
        self.running = False
        schedule.clear()
        self.logger.info("Agendador de backup parado")
    
    def _scheduled_backup(self):
        """Executa backup agendado"""
        try:
            self.logger.info("Iniciando backup automático agendado...")
            backup_path = self.create_backup("scheduled")
            self.logger.info(f"Backup automático concluído: {backup_path}")
            
            if self.config["email_notifications"]:
                self._send_email_notification(backup_path, "success")
                
        except Exception as e:
            self.logger.error(f"Erro no backup automático: {e}")
            
            if self.config["email_notifications"]:
                self._send_email_notification(None, "error", str(e))
    
    def _send_email_notification(self, backup_path, status, error_msg=None):
        """Envia notificação por email sobre o backup"""
        pass

backup_system = BackupSystem()

def create_manual_backup():
    """Cria um backup manual"""
    return backup_system.create_backup("manual")

def start_auto_backup():
    """Inicia backup automático"""
    backup_system.start_scheduler()

if __name__ == "__main__":
    print("🔄 Testando sistema de backup...")
    
    backup_path = create_manual_backup()
    print(f"✅ Backup criado: {backup_path}")
    
    backups = backup_system.list_backups()
    print(f"📋 Total de backups: {len(backups)}")
    
    for backup in backups[:3]:  # Mostrar apenas os 3 mais recentes
        print(f"  • {backup['name']} - {backup['created'].strftime('%d/%m/%Y %H:%M')}")
    
    print("✅ Teste concluído!")
