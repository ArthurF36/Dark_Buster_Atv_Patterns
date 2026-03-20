import os
import requests
import json
import pandas as pd

# ============================================
# CONFIGURAÇÃO DA API GEMINI
# ============================================
key = "GOOGLE_API_KEY"
api_key = os.getenv(key)

if not api_key:
    print(f"ERRO: {key} não encontrada!")
    exit(1)

modelo = "gemini-2.5-flash"
endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"

def obter_html(url):
    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        return resposta.text
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

def analisar_site(url):
    html = obter_html(url)
    
    # Template de retorno conforme seu padrão
    resultado_padrao = {
        "url": url,
        "manipulative_design": False,
        "patterns_detected": [],
        "security_risks": [],
        "confidence_level": "baixa"
    }

    if not html:
        resultado_padrao["security_risks"] = ["Falha na conexão ou site inacessível."]
        return resultado_padrao

    prompt = f"""
Analise o HTML e responda APENAS com um JSON válido seguindo este padrão estrito:
{{
    "url": "{url}",
    "manipulative_design": boolean,
    "patterns_detected": [{{ "name": "string", "description": "string" }}],
    "security_risks": ["string"],
    "confidence_level": "alta/média/baixa"
}}
HTML: {html[:15000]} 
"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(endpoint, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            texto_json = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Limpeza simples caso a IA retorne blocos de código ```json
            if texto_json.startswith("```"):
                texto_json = texto_json.strip("```json").strip("```")
            
            return json.loads(texto_json)
        else:
            resultado_padrao["security_risks"] = [f"Erro API: {response.status_code}"]
            return resultado_padrao
    except Exception as e:
        resultado_padrao["security_risks"] = [f"Erro no processamento: {str(e)}"]
        return resultado_padrao

# ============================================
# LOOP DE EXECUÇÃO E DATAFRAME
# ============================================
if __name__ == "__main__":
    # Criamos uma lista para armazenar os dicionários antes de converter para DF
    lista_resultados = []

    print("--- Analisador de Sites iniciado ---")

    while True:
        url_input = input("\nDigite a URL (ou 'sair' ou '0' para encerrar): ").strip()

        if url_input.lower() in ['sair', 'exit', 's', 'n', '0']:
            break

        if not url_input.startswith("http"):
            print("Insira uma URL válida (ex: https://google.com)")
            continue

        print(f"🔍 Analisando: {url_input}...")
        dados_analise = analisar_site(url_input)
        
        # Adiciona o resultado à nossa lista
        lista_resultados.append(dados_analise)
        print("✅ Dados processados com sucesso!")

    # Fora do loop, consolidamos tudo em um DataFrame
    if lista_resultados:
        df_final = pd.DataFrame(lista_resultados)

        pasta_resultados = "Data_resultados"

        if not os.path.exists(pasta_resultados):
            os.makedirs(pasta_resultados)
            print(f"📁 Pasta '{pasta_resultados}' criada com sucesso!")

        caminho_arquivo = os.path.join(pasta_resultados, 
                                       "gemini_manipulative_design.xlsx")
        df_final.to_excel(caminho_arquivo, index=False, engine='openpyxl')
        
        print("\n" + "="*50)
        print("RESULTADO CONSOLIDADO (DATAFRAME):")
        print(df_final)
        print("="*50)
    else:
        print("\nNenhuma análise foi realizada.")