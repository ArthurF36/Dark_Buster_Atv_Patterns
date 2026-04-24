import os
import requests
import json
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup  # Recomendado para limpar o HTML

# ============================================
# CONFIGURAÇÃO DA API GEMINI
# ============================================
API_KEY_NAME = "GOOGLE_API_KEY"
api_key = os.getenv(API_KEY_NAME)

if not api_key:
    raise ValueError(f"ERRO: variável de ambiente '{API_KEY_NAME}' não encontrada!")

# Atualizado para a versão estável mais recente
MODEL = "gemini-1.5-flash" 
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key}"

# ============================================
# FUNÇÃO: OBTER E LIMPAR HTML
# ============================================
def obter_html(url):
    try:
        # Headers mais robustos para evitar bloqueios (User-Agent de navegador real)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.google.com/"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Limpeza do HTML para focar no conteúdo e reduzir gasto de tokens
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts e estilos que não ajudam na análise de design
        for script_or_style in soup(["script", "style", "meta", "noscript", "link"]):
            script_or_style.decompose()
            
        # Retorna apenas o corpo da página limpo
        return str(soup.body)[:20000] # Limite de caracteres para segurança
        
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao acessar {url}: {e}")
        return None

# ============================================
# FUNÇÃO: LIMPAR RESPOSTA DA IA
# ============================================
def limpar_json_resposta(texto):
    # Remove markdown de blocos de código se houver
    if "```json" in texto:
        texto = texto.split("```json")[1].split("```")[0].strip()
    elif "```" in texto:
        texto = texto.split("```")[1].split("```")[0].strip()
    return texto.strip()

# ============================================
# FUNÇÃO: PROMPT
# ============================================
def construir_prompt(url, html):
    return f"""
Analise o HTML do site abaixo em busca de Deceptive Patterns (Dark Patterns) ou Design Persuasivo.
URL: {url}

Responda APENAS com um JSON válido:
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
            "evidence": "trecho do HTML ou elemento"
        }}
    ],
    "risk_level": "alto | medio | baixo",
    "security_risks": ["string"],
    "confidence_level": "alta | media | baixa"
}}

HTML:
{html}
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
        resultado_padrao["security_risks"] = ["Falha ao acessar o site ou bloqueio de bot"]
        return resultado_padrao

    prompt = construir_prompt(url, html)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1, # Menor temperatura para respostas mais técnicas
            "response_mime_type": "application/json" # Força a saída em JSON se o modelo suportar
        }
    }

    try:
        response = requests.post(ENDPOINT, json=payload, timeout=30)

        if response.status_code != 200:
            resultado_padrao["security_risks"] = [f"Erro API: {response.status_code} - {response.text}"]
            return resultado_padrao

        data = response.json()
        texto = data["candidates"][0]["content"]["parts"][0]["text"]
        
        texto_limpo = limpar_json_resposta(texto)
        return json.loads(texto_limpo)

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
    caminho = os.path.join(pasta, f"analise_sites_{timestamp}.xlsx")
    df.to_excel(caminho, index=False, engine="openpyxl")
    print(f"\n📁 Resultados salvos em: {caminho}")

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================
def main():
    resultados = []
    print("\n=== ANALISADOR DE SITES (IA) ===")
    print("Dica: Use URLs completas como https://www.ludoeducativo.com.br")

    while True:
        url = input("\nDigite uma URL (ou 'sair'): ").strip()

        if url.lower() in ["sair", "exit", "s"]:
            break

        if not url.startswith("http"):
            url = "https://" + url

        print(f"🔍 Analisando: {url}...")
        resultado = analisar_site(url)
        resultados.append(resultado)
        print("✅ Análise concluída!")

    if resultados:
        df = pd.json_normalize(resultados) # Melhor para converter JSON aninhado em tabela
        print("\n=== RESUMO ===")
        print(df[["url", "design_classification", "risk_level"]].to_string())
        salvar_resultados(df)
    else:
        print("Nenhuma análise realizada.")

if __name__ == "__main__":
    main()