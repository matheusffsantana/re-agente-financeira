# Avaliação e Métricas

## 1. Objetivo da Avaliação

Medir se a Rê está cumprindo três promessas feitas na documentação (`docs/01`): **não alucina** dados financeiros, **respeita os limites de autonomia** definidos, e **avança o cliente na jornada** (dívida → negociação → organização → investimento) de forma real, não só conversacional. As métricas abaixo estão organizadas em três grupos, do mais técnico ao mais voltado a impacto de negócio.

## 2. Métricas Técnicas e Operacionais

| Métrica | O que mede | Como coletar hoje | Meta |
|---|---|---|---|
| Latência de resposta | Tempo entre o envio da mensagem e a resposta da Rê | Log de timestamp no `main.py`, antes e depois de `gerar_resposta` | < 5s para 90% das mensagens |
| Taxa de erro do LLM | % de chamadas ao LLM que falham ou retornam vazio (ex.: o `JSONDecodeError` que já enfrentamos na classificação de escopo) | Contar exceções capturadas pelo `try/except` no `main.py` | < 2% das chamadas |
| Disponibilidade do WebSocket | % de conexões que permanecem estáveis sem queda inesperada (código 1006) | Logs do `ConnectionManager` (eventos de conectar/desconectar) | > 99% das sessões sem queda |

## 3. Métricas de Qualidade e Segurança

Essas métricas validam diretamente os guardrails documentados na Etapa 1 — não são genéricas, cada uma corresponde a uma regra específica que definimos.

| Métrica | O que mede | Por que importa |
|---|---|---|
| Precisão da classificação de escopo | % de mensagens classificadas corretamente como `dentro_escopo`/`fora_escopo`, comparado a uma amostra revisada manualmente | Já identificamos um caso real de falha (saudações simples como "Olá" sendo classificadas como fora de escopo) — essa métrica é o que transformaria esse tipo de erro em algo mensurável e rastreável ao longo do tempo, em vez de descoberto por acaso durante um teste manual |
| Taxa de alucinação de dados | % de respostas em que a Rê menciona um valor financeiro que não vem do contexto fornecido pelo backend | Deveria ser **0% por construção** (dado que os dados sempre vêm de `repositorio.py` antes do prompt ser montado) — essa métrica serve para confirmar que a arquitetura está sendo respeitada na prática, não só no design |
| Decisões críticas via botão vs. texto livre | % de transições de fase que se originaram de um evento `"decisao"` (botão) contra qualquer tentativa de interpretar isso por texto livre | Deveria ser **100% via botão** para eventos como aceitar/recusar proposta — um valor abaixo disso indicaria uma falha no guardrail de autonomia limitada |
| Taxa de negociações fechadas sem autorização do banco | % de vezes que o estado avançou de `negociacao` para `organizacao` sem passar por `aguardando_banco` | Deveria ser **sempre 0%** — a máquina de estados foi desenhada para tornar isso estruturalmente impossível, então essa métrica é mais uma auditoria de integridade do que uma expectativa de falha |

## 4. Métricas de Jornada e Impacto

Essas métricas dependem de dados acumulados ao longo do tempo (hoje simulados via `historico_atendimento.csv`; em produção, viriam de um banco de dados real — ver limitação documentada no `docs/01`).

| Métrica | O que mede |
|---|---|
| Funil da jornada | Quantos clientes estão em cada fase (`diagnostico`, `negociacao`, `aguardando_banco`, `organizacao`, `investimento`) em um dado momento — mostra onde o funil "afunila" mais |
| Taxa de conclusão de negociação | % de clientes que saem de `negociacao`/`aguardando_banco` e chegam a `organizacao`, contra os que caem em `negociacao_esgotada` |
| Tempo médio até a negociação concluída | Da entrada em `diagnostico` até a confirmação do banco (`banco_confirmou`) |
| Taxa de regressão | % de clientes que regridem de fase (ex.: `organizacao` → `negociacao` por nova dívida) — um valor alto indicaria que o acompanhamento pós-negociação não está sendo eficaz em manter a saúde financeira do cliente |
| Engajamento com mensagens comemorativas | Correlação entre receber uma mensagem comemorativa (`parcela_paga`) e a probabilidade do cliente continuar pagando as parcelas seguintes — evidência de que o reforço positivo está de fato ajudando, não só "parecendo bonito" |

## 5. Limitação Atual da Coleta

Hoje, a única fonte de dados históricos é o `historico_atendimento.csv` mockado — as métricas acima são conceituais e não têm um pipeline de coleta automatizada implementado. Isso está alinhado com a limitação de persistência em memória já documentada no `docs/01`: sem um banco de dados real, não há como acumular histórico entre reinícios do backend para calcular essas métricas de verdade.