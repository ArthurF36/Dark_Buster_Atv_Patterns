import os
import requests
import json
import pandas as pd
from datetime import datetime

# ============================================
# CONFIGURAÇÃO DA API GEMINI
# ============================================
API_KEY_NAME = "GOOGLE_API_KEY"
api_key = os.getenv(API_KEY_NAME)

if not api_key:
    raise ValueError(f"ERRO: variável de ambiente '{API_KEY_NAME}' não encontrada!")

MODEL = "gemini-2.5-flash"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key}"

# ============================================
# FUNÇÃO: OBTER HTML
# ============================================
def obter_html(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; IA-Analyzer/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao acessar {url}: {e}")
        return None

# ============================================
# FUNÇÃO: LIMPAR RESPOSTA DA IA
# ============================================
def limpar_json_resposta(texto):
    if texto.startswith("```"):
        texto = texto.replace("```json", "").replace("```", "").strip()
    return texto

# ============================================
# FUNÇÃO: PROMPT
# ============================================
def construir_prompt(url, html):
    return f"""
Analise o HTML e responda APENAS com um JSON válido seguindo este padrão estrito:

{{
    "url": "{url}",
    "manipulative_design": boolean,
    "design_classification": "deceptive_pattern | persuasive_design | neutral | unclear",
    "has_deceptive_patterns": boolean,
    "patterns_detected": [
        {{
            "name": "string",
            "category": "string",
            "description": "string",
            "evidence": "trecho do HTML ou comportamento observado"
        }}
    ],
    "risk_level": "alto | medio | baixo",
    "security_risks": ["string"],
    "confidence_level": "alta | media | baixa"
}}

REGRAS IMPORTANTES:
- NÃO inventar padrões sem evidência
- Se não houver padrões, retornar []
- Basear-se apenas no HTML fornecido

Exemplos de deceptive patterns:
Roach Motel, Hidden Costs, Confirmshaming, Forced Continuity, Bait and Switch, Sneak into Basket

HTML:
{html[:15000]}
"""

# ============================================
# FUNÇÃO: ANALISAR SITE
# ============================================
def analisar_site(url):
    html = obter_html(url)

    resultado_padrao = {
        "url": url,
        "manipulative_design": False,
        "design_classification": "unclear",
        "has_deceptive_patterns": False,
        "patterns_detected": [],
        "risk_level": "baixo",
        "security_risks": [],
        "confidence_level": "baixa"
    }

    if not html:
        resultado_padrao["security_risks"] = ["Falha ao acessar o site"]
        return resultado_padrao

    prompt = construir_prompt(url, html)

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(ENDPOINT, json=payload, timeout=30)

        if response.status_code != 200:
            resultado_padrao["security_risks"] = [f"Erro API: {response.status_code}"]
            return resultado_padrao

        data = response.json()
        texto = data["candidates"][0]["content"]["parts"][0]["text"]

        texto = limpar_json_resposta(texto)

        resultado = json.loads(texto)

        return resultado

    except Exception as e:
        resultado_padrao["security_risks"] = [f"Erro processamento: {str(e)}"]
        return resultado_padrao

# ============================================
# FUNÇÃO: SALVAR RESULTADOS
# ============================================
def salvar_resultados(df):
    pasta = "Data_resultados"
    os.makedirs(pasta, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = os.path.join(pasta, f"analise_sites_gemini{timestamp}.xlsx")

    df.to_excel(caminho, index=False, engine="openpyxl")

    print(f"\n📁 Resultados salvos em: {caminho}")

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================
def main():
    resultados = []

    print("\n=== ANALISADOR DE SITES (IA) ===")

    while True:
        url = input("\nDigite uma URL (ou 'sair'): ").strip()

        if url.lower() in ["sair", "exit", "0", "s", "S"]:
            break

        if not url.startswith("http"):
            print("⚠️ URL inválida!")
            continue

        print(f"🔍 Analisando: {url}")

        resultado = analisar_site(url)

        resultados.append(resultado)

        print("✅ Análise concluída!")

    if resultados:
        df = pd.DataFrame(resultados)

        print("\n=== RESUMO ===")
        print(df[["url", "design_classification", "risk_level", "confidence_level"]])

        salvar_resultados(df)
    else:
        print("Nenhuma análise realizada.")

# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    main()