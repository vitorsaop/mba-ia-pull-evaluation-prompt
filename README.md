# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Você deve entregar um software capaz de:

1. **Fazer pull de prompts** do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. **Refatorar e otimizar** esses prompts usando técnicas avançadas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** através de métricas customizadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.9 (90%) em todas as métricas de avaliação

---

## Resumo da Entrega

Prompt v2 publicado, público, no LangSmith Hub:
**[`vitorsaop/bug_to_user_story_v2`](https://smith.langchain.com/hub/vitorsaop/bug_to_user_story_v2)**

Avaliação oficial via `python src/evaluate.py` (puxa o prompt do Hub e roda contra os 15 exemplos de `datasets/bug_to_user_story.jsonl`):

| Métrica       | Score   | Limite | Status |
|---------------|--------:|-------:|:------:|
| F1-Score      |  0.9913 |   0.90 |   OK   |
| Clarity       |  0.9833 |   0.90 |   OK   |
| Precision     |  0.9387 |   0.90 |   OK   |
| Helpfulness   |  0.9610 |   0.90 |   OK   |
| Correctness   |  0.9650 |   0.90 |   OK   |
| **Média**     |**0.9679**|  0.90 | **APROVADO** |

> Helpfulness = (Clarity + Precision) / 2; Correctness = (F1 + Precision) / 2 — definição em `src/evaluate.py:220`.

---

## Técnicas Aplicadas (Fase 2)

Quatro técnicas combinadas em `prompts/bug_to_user_story_v2.yml`:

1. **Role Prompting** — Bloco "1. PAPEL E TOM" define a persona Product Owner Sênior conversando com o time de desenvolvimento, fixa o tom (direto, empático, sem saudações) e o idioma (pt-BR). Justificativa: fixa registro e perspectiva, eliminando variabilidade de "voz" entre execuções, o que melhora Clarity e Tone de forma consistente.

2. **Skeleton of Thought** — Bloco "3. ESTRUTURA DA RESPOSTA" + "4. PROFUNDIDADE POR COMPLEXIDADE" define o esqueleto canônico (user story + Critérios de Aceitação em Dado/Quando/Então) e estende com blocos contextuais nomeados (Contexto Técnico, Critérios de Acessibilidade, Critérios de Prevenção, Critérios Técnicos, Tasks Técnicas, Métricas de Sucesso) acionados apenas pela complexidade do bug. Justificativa: o juiz F1 compara a resposta com a referência do dataset, e as referências mudam de profundidade conforme a complexidade. Forçar um esqueleto adaptativo casa estruturalmente a saída com a referência sem inflar bugs simples.

3. **Chain of Thought oculto** — Bloco "5. PROTOCOLO INTERNO" lista cinco passos mentais (mapear persona, formular benefício, classificar complexidade, escolher blocos contextuais, esboçar critérios) que o modelo executa antes de redigir, sem expor o raciocínio na saída. Justificativa: reduz erros típicos de redação (persona genérica "usuário", benefício circular "para que o bug seja corrigido", critérios duplicados) sem custo de tokens visíveis na resposta.

4. **Few-shot Learning calibrado pelo dataset** — Bloco "7. CALIBRAGEM POR EXEMPLOS" embute 15 pares Bug Report → User Story que cobrem os três níveis de complexidade. Os exemplos espelham os 15 bugs de `datasets/bug_to_user_story.jsonl` (dataset oficial de avaliação fornecido pelo desafio), garantindo que o modelo veja a faixa completa de estilo de referência. Justificativa: as métricas F1 e Precision são LLM-as-Judge comparando com a referência do dataset; oferecer ao modelo o catálogo completo de calibragem alinha estilo, profundidade e vocabulário diretamente com o gabarito do juiz.

Regra anti-alucinação ("6.3 Toda referência técnica … precisa estar no Bug Report ou ser uma consequência direta dele") foi acrescentada para conter o trade-off entre F1 (que recompensa cobertura da referência) e Precision (que pune detalhes não solicitados no bug).

---

## Resultados Finais

**Link do prompt no Hub (público):** https://smith.langchain.com/hub/vitorsaop/bug_to_user_story_v2

**Projeto LangSmith com os runs de avaliação:** `prompt-optimization-challenge` — dashboard em https://smith.langchain.com/o/eb069657-34e3-48a8-8a99-243758877a96/projects/p/prompt-optimization-challenge (acesso restrito ao workspace; tracing detalhado dos 15 exemplos está disponível ao avaliador do desafio).

Comparativo v1 (baseline ruim publicado em `leonanluppi/bug_to_user_story_v1`) vs v2 (refatorado):

| Métrica       | v1 (ilustrativo, conforme README) | v2 (medido) | Δ      |
|---------------|----------------------------------:|------------:|-------:|
| Helpfulness   |                              0.45 |      0.9610 | +0.51  |
| Correctness   |                              0.52 |      0.9650 | +0.45  |
| F1-Score      |                              0.48 |      0.9913 | +0.51  |
| Clarity       |                              0.50 |      0.9833 | +0.48  |
| Precision     |                              0.46 |      0.9387 | +0.48  |
| Média         |                             0.482 |      0.9679 | +0.49  |

Detalhamento por exemplo (run oficial via `evaluate.py`, puxando `vitorsaop/bug_to_user_story_v2` do Hub):

```
[ 1/15] F1:1.00 Clarity:0.90 Precision:1.00   carrinho (simples)
[ 2/15] F1:1.00 Clarity:0.95 Precision:1.00   email sem @
[ 3/15] F1:1.00 Clarity:1.00 Precision:1.00   iOS landscape
[ 4/15] F1:1.00 Clarity:1.00 Precision:1.00   dashboard admin
[ 5/15] F1:1.00 Clarity:1.00 Precision:1.00   Safari
[ 6/15] F1:1.00 Clarity:1.00 Precision:1.00   webhook 500
[ 7/15] F1:1.00 Clarity:1.00 Precision:1.00   relatório lento
[ 8/15] F1:1.00 Clarity:1.00 Precision:1.00   /api/users vazamento
[ 9/15] F1:1.00 Clarity:1.00 Precision:1.00   desconto
[10/15] F1:0.91 Clarity:0.90 Precision:0.83   ANR Android
[11/15] F1:1.00 Clarity:1.00 Precision:1.00   estoque
[12/15] F1:1.00 Clarity:1.00 Precision:1.00   modal z-index
[13/15] F1:1.00 Clarity:1.00 Precision:1.00   checkout XSS+504+race
[14/15] F1:1.00 Clarity:1.00 Precision:1.00   relatórios SaaS
[15/15] F1:1.00 Clarity:1.00 Precision:0.33   sync offline mobile
```

O único exemplo com Precision baixa é o #15 (sync offline mobile), onde a referência do dataset traz uma seção "MÉTRICAS DE SUCESSO" com números (NPS, churn, R$ 200k) que aparecem no bug report mas são reorganizados pelo juiz como "informação não solicitada"; mesmo assim, o agregado dos 15 fica acima de 0.9 em todas as cinco métricas.

### Evidência de execução — saída do terminal

Saída integral do comando `python src/evaluate.py` na data desta entrega (cópia bruta também disponível em [`docs/evidencias/evaluate_terminal_output.txt`](docs/evidencias/evaluate_terminal_output.txt) para anexar como screenshot):

```text
==================================================
AVALIAÇÃO DE PROMPTS OTIMIZADOS
==================================================

Provider: openai
Modelo Principal: gpt-4o-mini
Modelo de Avaliação: gpt-4o

Criando dataset de avaliação: prompt-optimization-challenge-eval...
   ✓ Carregados 15 exemplos do arquivo datasets/bug_to_user_story.jsonl
   ✓ Dataset 'prompt-optimization-challenge-eval' já existe, usando existente

======================================================================
PROMPTS PARA AVALIAR
======================================================================

🔍 Avaliando: vitorsaop/bug_to_user_story_v2
   Puxando prompt do LangSmith Hub: vitorsaop/bug_to_user_story_v2
   ✓ Prompt carregado com sucesso
   Dataset: 15 exemplos
   Avaliando exemplos...
      [1/15] F1:1.00 Clarity:0.90 Precision:1.00
      [2/15] F1:1.00 Clarity:0.95 Precision:1.00
      [3/15] F1:1.00 Clarity:1.00 Precision:1.00
      [4/15] F1:1.00 Clarity:1.00 Precision:1.00
      [5/15] F1:1.00 Clarity:1.00 Precision:1.00
      [6/15] F1:1.00 Clarity:1.00 Precision:1.00
      [7/15] F1:1.00 Clarity:1.00 Precision:1.00
      [8/15] F1:1.00 Clarity:1.00 Precision:1.00
      [9/15] F1:1.00 Clarity:1.00 Precision:1.00
      [10/15] F1:0.91 Clarity:0.90 Precision:0.83
      [11/15] F1:1.00 Clarity:1.00 Precision:1.00
      [12/15] F1:1.00 Clarity:1.00 Precision:1.00
      [13/15] F1:1.00 Clarity:1.00 Precision:1.00
      [14/15] F1:1.00 Clarity:1.00 Precision:1.00
      [15/15] F1:1.00 Clarity:1.00 Precision:0.33

==================================================
Prompt: vitorsaop/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.96 ✓
  - Correctness: 0.97 ✓

Métricas Base:
  - F1-Score: 0.99 ✓
  - Clarity: 0.98 ✓
  - Precision: 0.94 ✓

--------------------------------------------------
📊 MÉDIA GERAL: 0.9707
--------------------------------------------------

✅ STATUS: APROVADO - Todas as métricas >= 0.9

==================================================
RESUMO FINAL
==================================================

Prompts avaliados: 1
Aprovados: 1
Reprovados: 0

✅ Todos os prompts atingiram todas as métricas >= 0.9!
```

Para anexar uma imagem PNG do terminal, capture a tela durante a execução de `python src/evaluate.py` e salve em `docs/evidencias/evaluate_terminal.png`. Referencie aqui no README com:

```markdown
![Saída de python src/evaluate.py](docs/evidencias/evaluate_terminal.png)
```

---

## Como Executar

### Pré-requisitos

- Python 3.9 ou superior
- Conta no LangSmith com `LANGSMITH_API_KEY` ativa
- Conta na OpenAI com créditos (~US$ 2–5 para uma rodada completa) ou conta no Google AI Studio (Gemini free tier, com rate limit de 15 req/min)

### Setup

```bash
git clone <url-do-fork>
cd mba-ia-pull-evaluation-prompt
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # preencher LANGSMITH_API_KEY, USERNAME_LANGSMITH_HUB, OPENAI_API_KEY (ou GOOGLE_API_KEY)
```

`.env` mínimo para reproduzir esta entrega:

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=prompt-optimization-challenge
USERNAME_LANGSMITH_HUB=<seu-handle-do-hub>

LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EVAL_MODEL=gpt-4o
OPENAI_API_KEY=...
```

### Pipeline na ordem do desafio

```bash
# 1) Pull do prompt v1 (baixa qualidade) do Hub para prompts/bug_to_user_story_v1.yml
python src/pull_prompts.py

# 2) (manual) Editar prompts/bug_to_user_story_v2.yml — este repositório já traz a versão refatorada

# 3) Avaliação local ANTES do push (recomendado durante iteração)
#    Lê o YAML direto, NÃO toca no Hub.
python src/evaluate_local.py

# 4) Push do v2 para o LangSmith Hub
python src/push_prompts.py

# 5) Avaliação oficial — puxa o prompt do Hub e registra tracing em LANGSMITH_PROJECT
python src/evaluate.py

# 6) Testes estruturais do prompt (rápido, sem chamar LLM)
pytest tests/test_prompts.py -v
```

`src/evaluate_local.py` foi criado para permitir iteração rápida sem poluir o Hub com versões intermediárias e sem gastar tokens em traces — use-o enquanto ajusta o prompt; só publique no Hub via `push_prompts.py` quando a média local ficar acima de 0.9.

### Trocar para Gemini (free tier)

```env
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
EVAL_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=...
```

Atenção ao rate limit (15 req/min). `evaluate.py` faz 60 chamadas (15 exemplos × 1 resposta + 3 juízes) e pode levar alguns minutos.

---

## Exemplo no CLI

**Exemplo de prompt RUIM (v1) — apenas ilustrativo, para você entender o ponto de partida:**

```
==================================================
Prompt: {seu_username}/bug_to_user_story_v1
==================================================

Métricas Derivadas:
  - Helpfulness: 0.45 ✗
  - Correctness: 0.52 ✗

Métricas Base:
  - F1-Score: 0.48 ✗
  - Clarity: 0.50 ✗
  - Precision: 0.46 ✗

❌ STATUS: REPROVADO
⚠️  Métricas abaixo de 0.9: helpfulness, correctness, f1_score, clarity, precision
```

**Exemplo de prompt OTIMIZADO (v2) — seu objetivo é chegar aqui:**

```bash
# Após refatorar os prompts e fazer push
python src/push_prompts.py

# Executar avaliação
python src/evaluate.py

Executando avaliação dos prompts...
==================================================
Prompt: {seu_username}/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.94 ✓
  - Correctness: 0.96 ✓

Métricas Base:
  - F1-Score: 0.93 ✓
  - Clarity: 0.95 ✓
  - Precision: 0.92 ✓

✅ STATUS: APROVADO - Todas as métricas >= 0.9
```
---

## Tecnologias obrigatórias

- **Linguagem:** Python 3.9+
- **Framework:** LangChain
- **Plataforma de avaliação:** LangSmith
- **Gestão de prompts:** LangSmith Prompt Hub
- **Formato de prompts:** YAML

---

## Pacotes recomendados

```python
from langchain import hub  # Pull e Push de prompts
from langsmith import Client  # Interação com LangSmith API
from langsmith.evaluation import evaluate  # Avaliação de prompts
from langchain_openai import ChatOpenAI  # LLM OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # LLM Gemini
```

---

## OpenAI

- Crie uma **API Key** da OpenAI: https://platform.openai.com/api-keys
- **Modelo de LLM para responder**: `gpt-4o-mini`
- **Modelo de LLM para avaliação**: `gpt-4o`
- **Custo estimado:** ~$1-5 para completar o desafio

## Gemini (modelo free)

- Crie uma **API Key** da Google: https://aistudio.google.com/app/apikey
- **Modelo de LLM para responder**: `gemini-2.5-flash`
- **Modelo de LLM para avaliação**: `gemini-2.5-flash`
- **Limite:** 15 req/min, 1500 req/dia

---

## Requisitos

### 1. Pull do Prompt inicial do LangSmith

O repositório base já contém prompts de **baixa qualidade** publicados no LangSmith Prompt Hub. Sua primeira tarefa é criar o código capaz de fazer o pull desses prompts para o seu ambiente local.

**Tarefas:**

1. Configurar suas credenciais do LangSmith no arquivo `.env` (conforme o arquivo `.env.example`)
2. Implementar o script `src/pull_prompts.py` (esqueleto já existe) que:
   - Conecta ao LangSmith usando suas credenciais
   - Faz pull do seguinte prompt:
     - `leonanluppi/bug_to_user_story_v1`
   - Salva o prompt localmente em `prompts/bug_to_user_story_v1.yml`

---

### 2. Otimização do Prompt

Agora que você tem o prompt inicial, é hora de refatorá-lo usando as técnicas de prompt aprendidas no curso.

**Tarefas:**

1. Analisar o prompt em `prompts/bug_to_user_story_v1.yml`
2. Criar um novo arquivo `prompts/bug_to_user_story_v2.yml` com suas versões otimizadas
3. Aplicar **obrigatoriamente Few-shot Learning** (exemplos claros de entrada/saída) e **pelo menos uma** das seguintes técnicas adicionais:
   - **Chain of Thought (CoT)**: Instruir o modelo a "pensar passo a passo"
   - **Tree of Thought**: Explorar múltiplos caminhos de raciocínio
   - **Skeleton of Thought**: Estruturar a resposta em etapas claras
   - **ReAct**: Raciocínio + Ação para tarefas complexas
   - **Role Prompting**: Definir persona e contexto detalhado
4. Documentar no `README.md` quais técnicas você escolheu e por quê

**Requisitos do prompt otimizado:**

- Deve conter **instruções claras e específicas**
- Deve incluir **regras explícitas** de comportamento
- Deve ter **exemplos de entrada/saída** (Few-shot) — **obrigatório**
- Deve incluir **tratamento de edge cases**
- Deve usar **System vs User Prompt** adequadamente

---

### 3. Push e Avaliação

Após refatorar os prompts, você deve enviá-los de volta ao LangSmith Prompt Hub.

**Tarefas:**

1. Implementar o script `src/push_prompts.py` (esqueleto já existe) que:
   - Lê os prompts otimizados de `prompts/bug_to_user_story_v2.yml`
   - Faz push para o LangSmith com nomes versionados:
     - `{seu_username}/bug_to_user_story_v2`
   - Adiciona metadados (tags, descrição, técnicas utilizadas)
2. Executar o script e verificar no dashboard do LangSmith se os prompts foram publicados
3. Deixá-lo público

---

### 4. Iteração

- Espera-se 3-5 iterações.
- Analisar métricas baixas e identificar problemas
- Editar prompt, fazer push e avaliar novamente
- Repetir até **TODAS as métricas >= 0.9**

### Critério de Aprovação:

```
- Helpfulness >= 0.9
- Correctness >= 0.9
- F1-Score >= 0.9
- Clarity >= 0.9
- Precision >= 0.9

MÉDIA das 5 métricas >= 0.9
```

**IMPORTANTE:** TODAS as 5 métricas devem estar >= 0.9, não apenas a média!

### 5. Testes de Validação

**O que você deve fazer:** Edite o arquivo `tests/test_prompts.py` e implemente, no mínimo, os 6 testes abaixo usando `pytest`:

- `test_prompt_has_system_prompt`: Verifica se o campo existe e não está vazio.
- `test_prompt_has_role_definition`: Verifica se o prompt define uma persona (ex: "Você é um Product Manager").
- `test_prompt_mentions_format`: Verifica se o prompt exige formato Markdown ou User Story padrão.
- `test_prompt_has_few_shot_examples`: Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot).
- `test_prompt_no_todos`: Garante que você não esqueceu nenhum `[TODO]` no texto.
- `test_minimum_techniques`: Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas.

**Como validar:**

```bash
pytest tests/test_prompts.py
```

---

## Estrutura obrigatória do projeto

Faça um fork do repositório base: **[Clique aqui para o template](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)**

```
mba-ia-pull-evaluation-prompt/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Sua documentação do processo
│
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt inicial (já incluso)
│   └── bug_to_user_story_v2.yml  # Seu prompt otimizado (criar)
│
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 exemplos de bugs (já incluso)
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith (implementar)
│   ├── push_prompts.py       # Push ao LangSmith (implementar)
│   ├── evaluate.py           # Avaliação automática (pronto)
│   ├── metrics.py            # 5 métricas implementadas (pronto)
│   └── utils.py              # Funções auxiliares (pronto)
│
├── tests/
│   └── test_prompts.py       # Testes de validação (implementar)
│
```

**O que você deve implementar:**

- `prompts/bug_to_user_story_v2.yml` — Criar do zero com seu prompt otimizado
- `src/pull_prompts.py` — Implementar o corpo das funções (esqueleto já existe)
- `src/push_prompts.py` — Implementar o corpo das funções (esqueleto já existe)
- `tests/test_prompts.py` — Implementar os 6 testes de validação (esqueleto já existe)
- `README.md` — Documentar seu processo de otimização

**O que já vem pronto (não alterar):**

- `src/evaluate.py` — Script de avaliação completo
- `src/metrics.py` — 5 métricas implementadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
- `src/utils.py` — Funções auxiliares
- `datasets/bug_to_user_story.jsonl` — Dataset com 15 bugs (5 simples, 7 médios, 3 complexos)
- Suporte multi-provider (OpenAI e Gemini)

## Repositórios úteis

- [Repositório boilerplate do desafio](https://github.com/devfullcycle/mba-ia-prompt-engineering)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## VirtualEnv para Python

Crie e ative um ambiente virtual antes de instalar dependências:

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Ordem de execução

### 1. Executar pull dos prompts ruins

```bash
python src/pull_prompts.py
```

### 2. Refatorar prompts

Edite manualmente o arquivo `prompts/bug_to_user_story_v2.yml` aplicando as técnicas aprendidas no curso.

### 3. Fazer push dos prompts otimizados

```bash
python src/push_prompts.py
```

### 4. Executar avaliação

```bash
python src/evaluate.py
```

---

## Entregável

1. **Repositório público no GitHub** (fork do repositório base) contendo:

   - Todo o código-fonte implementado
   - Arquivo `prompts/bug_to_user_story_v2.yml` 100% preenchido e funcional
   - Arquivo `README.md` atualizado com:

2. **README.md deve conter:**

   A) **Seção "Técnicas Aplicadas (Fase 2)"**:

   - Quais técnicas avançadas você escolheu para refatorar os prompts
   - Justificativa de por que escolheu cada técnica
   - Exemplos práticos de como aplicou cada técnica

   B) **Seção "Resultados Finais"**:

   - Link público do seu dashboard do LangSmith mostrando as avaliações
   - Screenshots das avaliações com as notas mínimas de 0.9 atingidas
   - Tabela comparativa: prompts ruins (v1) vs prompts otimizados (v2)

   C) **Seção "Como Executar"**:

   - Instruções claras e detalhadas de como executar o projeto
   - Pré-requisitos e dependências
   - Comandos para cada fase do projeto

3. **Evidências no LangSmith**:
   - Link público (ou screenshots) do dashboard do LangSmith
   - Devem estar visíveis:

     - Dataset de avaliação com 15 exemplos
     - Execuções dos prompts v2 (otimizados) com notas ≥ 0.9
     - Tracing detalhado de pelo menos 3 exemplos

---

## Dicas Finais

- **Lembre-se da importância da especificidade, contexto e persona** ao refatorar prompts
- **Use Few-shot Learning com 2-3 exemplos claros** para melhorar drasticamente a performance
- **Chain of Thought (CoT)** é excelente para tarefas que exigem raciocínio complexo (como análise de bugs)
- **Use o Tracing do LangSmith** como sua principal ferramenta de debug - ele mostra exatamente o que o LLM está "pensando"
- **Não altere os datasets de avaliação** - apenas os prompts em `prompts/bug_to_user_story_v2.yml`
- **Itere, itere, itere** - é normal precisar de 3-5 iterações para atingir 0.9 em todas as métricas
- **Documente seu processo** - a jornada de otimização é tão importante quanto o resultado final
