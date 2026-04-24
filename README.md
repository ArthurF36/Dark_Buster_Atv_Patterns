# Dark_Buster_Atv
Dark Patterns Analyzer

Projeto desenvolvido para analisar sites e identificar padrões
manipulativos (Dark Patterns) utilizando inteligência artificial, com
integração com modelos da OpenAI e Google Gemini.

OBJETIVO

-   Identificar práticas de design manipulativo em websites
-   Detectar possíveis riscos de segurança
-   Comparar resultados entre diferentes modelos de IA
-   Gerar relatórios estruturados em formato Excel

TECNOLOGIAS UTILIZADAS

-   Python 3.x
-   OpenAI API
-   Google Gemini API
-   Pandas
-   Requests
-   BeautifulSoup
-   OpenPyXL
-   Matplotlib / Seaborn

CONFIGURAÇÃO

1.  Instalar dependências no terminal: pip install -r requirements.txt

2.  Inicializar o código python com: 

- python Atividade_Dark_Patterns/Gemini_Atv.py
- python Atividade_Dark_Patterns/Openai_Atv.py

CONFIGURAÇÃO DAS APIs

- Google Gemini: export GOOGLE_API_KEY=“sua_chave_aqui”
- OpenAI: export OPENAI_API_KEY=“sua_chave_aqui”

ENTRADA DE DADOS

-   Data/sites.txt
-   Data/sites_educativos.txt

SAÍDA DE DADOS

-   Pasta Data_resultados/

Inclui: - URL analisada - Presença de dark patterns - Tipos detectados -
Riscos de segurança - Nível de confiança

ANÁLISE

Notebook: Notebook/graficos_Dark_Buster.ipynb

OBSERVAÇÕES

-   Alguns sites podem bloquear requisições automáticas
-   A qualidade depende do modelo de IA
-   Necessário internet

MELHORIAS FUTURAS

-   Interface web
-   Mais modelos de IA
-   Classificação mais detalhada
-   Automação de relatórios

AUTOR

Projeto acadêmico voltado para estudo de IA aplicada à detecção de
padrões manipulativos na web.
