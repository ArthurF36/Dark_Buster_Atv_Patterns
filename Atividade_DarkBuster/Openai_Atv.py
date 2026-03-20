import os
import requests
import json
import pandas as pd

# ============================================
# CONFIGURAÇÃO DA API OPENAI
# ============================================
key = "OPENAI_API_KEY"
api_key = os.getenv(key)

if not api_key:
    print(f"ERRO: {key} não encontrada!")
    exit(1)

# Modelo atualizado (ex: gpt-4o ou gpt-4o-mini)
modelo = "gpt-4o-mini" 
endpoint = "https://api.openai.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

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

    # ESTRUTURA OPENAI (Diferente do Gemini)
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": "Você é um analista de segurança e design ético. Responda apenas em JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": { "type": "json_object" } # Garante que venha JSON
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Acessando o conteúdo na estrutura OpenAI
            texto_json = data["choices"][0]["message"]["content"].strip()
            return json.loads(texto_json)
        else:
            resultado_padrao["security_risks"] = [f"Erro API OpenAI: {response.status_code}"]
            return resultado_padrao
    except Exception as e:
        resultado_padrao["security_risks"] = [f"Erro no processamento: {str(e)}"]
        return resultado_padrao

# ============================================
# LOOP DE EXECUÇÃO E DATAFRAME
# ============================================
if __name__ == "__main__":
    lista_resultados = []

    print("--- Analisador de Sites (OpenAI) iniciado ---")

    while True:
        url_input = input("\nDigite a URL (ou '0' para encerrar): ").strip()

        if url_input in ['0', 'sair', 'exit']:
            break

        if not url_input.startswith("http"):
            print("Insira uma URL válida (ex: https://google.com)")
            continue

        print(f"🔍 Analisando com {modelo}: {url_input}...")
        dados_analise = analisar_site(url_input)
        
        lista_resultados.append(dados_analise)
        print("✅ Dados processados!")

    if lista_resultados:
        df_final = pd.DataFrame(lista_resultados)

        pasta_resultados = "Data_resultados"
        if not os.path.exists(pasta_resultados):
            os.makedirs(pasta_resultados)

        caminho_arquivo = os.path.join(pasta_resultados, 
                                       "openai_manipulative_design.xlsx")
        df_final.to_excel(caminho_arquivo, index=False, engine='openpyxl')
        
        print("\n" + "="*50)
        print("RESULTADO NO DATAFRAME:")
        print(df_final)
        print(f"\n📁 Salvo em: {caminho_arquivo}")
        print("="*50)
    else:
        print("\nNenhuma análise foi realizada.")