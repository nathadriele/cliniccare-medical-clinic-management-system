#!/usr/bin/env python3
"""
Teste específico para verificar se o problema dos KPIs foi resolvido
"""

import sys
import traceback

def test_kpis():
    """Testa a função get_kpis_dashboard"""
    
    print("Testando função get_kpis_dashboard...")
    
    try:
        # Importar o gerenciador de banco
        from utils.db_manager import db_manager
        print("✅ Importação do db_manager: OK")
        
        # Testar a função get_kpis_dashboard
        kpis = db_manager.get_kpis_dashboard()
        print("✅ Execução da função: OK")
        
        # Verificar se os KPIs foram retornados corretamente
        print(f"KPIs retornados: {kpis}")
        
        # Verificar tipos dos valores
        for key, value in kpis.items():
            print(f"   {key}: {value} (tipo: {type(value)})")
        
        # Verificar se não há valores None
        none_values = [k for k, v in kpis.items() if v is None]
        if none_values:
            print(f"❌ Valores None encontrados: {none_values}")
            return False
        
        print("✅ Todos os KPIs estão corretos!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar KPIs: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        print("Traceback completo:")
        traceback.print_exc()
        return False

def test_home_callback():
    """Testa o callback da página home"""
    
    print("\n Testando callback da página home...")
    
    try:
        from pages.home import update_kpi_cards
        print("✅ Importação do callback: OK")
        
        # Simular chamada do callback
        result = update_kpi_cards(0)
        print("✅ Execução do callback: OK")
        print(f"Resultado do callback: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar callback: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        print("Traceback completo:")
        traceback.print_exc()
        return False

def main():
    """Função principal de teste"""
    
    print("ClinicCare - Teste de Correção dos KPIs")
    print("=" * 50)
    
    # Teste 1: Função get_kpis_dashboard
    test1_ok = test_kpis()
    
    # Teste 2: Callback da página home
    test2_ok = test_home_callback()
    
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES:")
    print(f"   Função get_kpis_dashboard: {'✅ OK' if test1_ok else '❌ FALHOU'}")
    print(f"   Callback da página home: {'✅ OK' if test2_ok else '❌ FALHOU'}")
    
    if test1_ok and test2_ok:
        print("\n TODOS OS TESTES PASSARAM!")
        print("✅ O problema dos KPIs foi RESOLVIDO!")
        return 0
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        print("É necessário mais correções.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
