# Rê — sua parceira para sair do vermelho

Agente financeiro que acompanha o cliente numa jornada completa — do diagnóstico da
dívida até o primeiro investimento — combinando conversação por IA generativa com
regras de negócio determinísticas e guardrails de segurança em cada etapa.

Projeto final do bootcamp **GenAI, Dados e Cybersecurity**, em parceria com o Bradesco
(DIO), desenvolvido a partir de uma base de lab fornecida pela DIO.

---

## O nome

**Rê** vem de **Re**conhece, **Re**estrutura, **Re**solve — as três etapas emocionais
pelas quais o cliente passa antes de sair do vermelho de verdade.

## A jornada

```
Diagnóstico → Negociação → Aguardando o banco → Organização → Investimento
```

A Rê é **consultiva, não executora**: ela simula, calcula e recomenda, mas nunca fecha
uma negociação sozinha — isso sempre depende de autorização expressa do banco. Detalhes
completos da arquitetura e dos guardrails estão em [`docs/01-documentacao-agente.md`](docs/01-documentacao-agente.md).

## Stack técnica

| Camada | Tecnologia |
|---|---|
| Backend | Python + FastAPI + WebSocket |
| Frontend | React + Vite |
| LLM | OpenRouter (modelo `openrouter/free` para testes) via SDK compatível com OpenAI |
| Dados | Arquivos mockados (`data/`) — sem persistência real ainda (ver limitações conhecidas) |

## Estrutura do projeto

```
re-agente-financeiro/
├── backend/
│   ├── app/
│   │   ├── core/        # Máquina de estados, motor de cálculo, mensagens (Python puro)
│   │   ├── llm/         # Prompts e integração com o LLM
│   │   ├── data/        # Leitura dos dados mockados
│   │   ├── websocket/   # Gerenciamento de conexões em tempo real
│   │   └── main.py      # Ponto de entrada da API
│   └── tests/           # Testes automatizados (pytest)
├── frontend/
│   └── src/
│       ├── components/  # Chat, Dashboard, PropostaBanco
│       ├── hooks/        # useWebSocket
│       ├── SelecaoCliente.jsx  # Tela de testes (escolha de cliente mockado)
│       └── Conversa.jsx        # Tela principal do chat
├── data/                 # Clientes, transações e produtos financeiros mockados
├── docs/                 # Documentação completa do projeto (01 a 05)
└── assets/               # Diagramas e imagens
```

## Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/01-documentacao-agente.md`](docs/01-documentacao-agente.md) | Caso de uso, persona, arquitetura, guardrails e limitações conhecidas |
| [`docs/02-base-conhecimento.md`](docs/02-base-conhecimento.md) | Estratégia de dados mockados |
| [`docs/03-prompts.md`](docs/03-prompts.md) | Engenharia de prompts (system prompt, few-shot, classificação estruturada) |
| [`docs/04-metricas.md`](docs/04-metricas.md) | Métricas de avaliação técnica, de qualidade e de negócio |
| [`docs/05-pitch.md`](docs/05-pitch.md) | Roteiro do pitch de apresentação |

## Como rodar localmente

### Backend
```bash
cd backend
pip install -r requirements.txt
```
Crie um arquivo `.env` dentro de `backend/` com:
```
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sua_chave_aqui
```
Depois:
```bash
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Abra o endereço mostrado no terminal (normalmente `http://localhost:5173`). A tela
inicial permite escolher entre 3 clientes mockados, cada um em uma fase diferente da
jornada — ambiente pensado para testes e demonstração.

## Limitações conhecidas

O projeto usa um modelo de LLM gratuito para desenvolvimento e não tem persistência
real de dados entre reinícios do backend. Ambas as limitações, e o raciocínio por trás
delas, estão detalhadas em [`docs/01-documentacao-agente.md`](docs/01-documentacao-agente.md#5-limitações-conhecidas-do-ambiente-de-testes).
