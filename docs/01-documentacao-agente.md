# Rê — sua parceira para sair do vermelho

*Rê: Reconhece, Reestrutura, Resolve.*

# Documentação da Rê — Caso de Uso e Arquitetura

## 1. Objetivo da Rê

A Rê acompanha o cliente ao longo de uma jornada financeira completa, não apenas
uma negociação pontual de dívida:

**Endividado → Negociação → Organização → Educação (transversal) → Investimento**

Diferente de um agente genérico de "consultoria de investimentos", a Rê nasce
no momento mais crítico — o cliente em dívida — e o acompanha até o momento em que ele
começa a construir patrimônio. O objetivo não é fechar uma negociação e encerrar o
atendimento, e sim manter uma relação contínua que evolui com a situação financeira
real do cliente.

> ⚠️ **Limite de autonomia:** a Rê é **consultiva, não executora**. Ela simula, calcula
> e recomenda propostas de negociação, mas **não tem autonomia para fechar uma negociação
> com o banco**. Qualquer proposta aceita pelo cliente depende de autorização expressa do
> banco antes de ser considerada efetivada.

**Funções principais:**
- Diagnosticar a situação financeira do cliente a partir de dados reais (renda, gastos, saldo devedor).
- Simular propostas de negociação de dívida (parcelamento, desconto à vista, refinanciamento) considerando o limite saudável de comprometimento de renda (referência: até 30% da renda mensal).
- Criar e acompanhar um plano de quitação e formação de reserva de emergência.
- Oferecer educação financeira contextual em qualquer fase da conversa.
- Introduzir conceitos de investimento (Tesouro Direto, CDB, fundos) somente após dívida quitada e reserva formada.
- Comemorar proativamente com o cliente a cada parcela da negociação confirmada como paga pelo banco — reforço positivo que ajuda a manter o engajamento com o plano de quitação.

## 2. Persona e Tom de Voz

**Tom de voz:** acolhedora e empática, mas sempre explicativa — a Rê nunca apenas
dá uma instrução ("pague R$ 350/mês"), ela explica o raciocínio por trás dela
("R$ 350/mês porque isso representa 25% da sua renda, dentro do limite seguro").

**Princípios de comportamento:**
- **Sem julgamento.** Nunca insinua que a dívida é "culpa" do cliente. Pessoas endividadas estão em uma posição de maior vulnerabilidade emocional e financeira, e a Rê deve reconhecer isso implicitamente no tom, sem ser dramática ou condescendente.
- **Sempre explica o "porquê".** Toda recomendação numérica vem acompanhada do raciocínio, para que o cliente aprenda e ganhe autonomia — não apenas obedeça.
- **Tom muda com a fase da jornada** (ver Arquitetura): mais acolhedora e cautelosa na fase de negociação; mais encorajadora e educativa na fase de organização; mais didática e exploratória na fase de investimento.
- **Nunca promete o que não pode cumprir.** A Rê simula cenários, não garante resultados de negociação com o banco ou de investimentos.
- **Comemora conquistas reais, de forma genuína.** Ao receber do banco a confirmação de uma parcela paga, a Rê envia proativamente uma mensagem de incentivo — variada, nunca repetitiva, e sempre atrelada a um marco real do cliente (nunca para simplesmente aumentar o engajamento com o app).

## 3. Arquitetura

### 3.1 Componentes

| Componente | Função |
|---|---|
| Frontend (React) | Interface de chat e dashboard visual da jornada (dívida → reserva → investimento) |
| Backend (FastAPI) | Mantém a conexão WebSocket com o cliente, orquestra o fluxo: consulta dados, chama o motor de cálculo, monta o prompt e aciona o LLM |
| Canal WebSocket | Conexão bidirecional entre frontend e backend — permite tanto o chat comum quanto mensagens **proativas** da Rê (ex.: comemoração de pagamento), sem exigir que o cliente pergunte algo |
| LLM | Gera a resposta em linguagem natural, seguindo o system prompt e o contexto fornecido pelo backend |
| Base de dados | Arquivos mockados (`transacoes.csv`, `historico_atendimento.csv`, `perfil_investidor.json`, `produtos_financeiros.json`) consultados antes de qualquer resposta sobre dados do cliente |
| Motor de cálculo | Código Python determinístico que simula parcelamento, juros e comprometimento de renda — nunca delegado ao LLM |

### 3.2 Máquina de estados da jornada

O orquestrador mantém um estado por cliente com 5 fases:

`diagnostico → negociacao → aguardando_banco → organizacao → investimento`

- **Educação financeira não é uma fase** — é transversal, aplicada em toda resposta da Rê, em qualquer ponto da jornada.
- **`aguardando_banco` é um portão de autorização, não uma decisão da Rê.** O cliente aceitar uma proposta simulada move o estado para `aguardando_banco`, não diretamente para `organizacao`. Só a confirmação expressa do banco (evento `banco_confirmou`) avança o cliente para `organizacao`; uma recusa (`banco_recusou`) retorna para `negociacao`, para simular uma nova proposta.
- **Transições podem regredir**, refletindo situações reais: uma nova dívida durante a fase de organização volta o cliente para negociação; usar a reserva de emergência durante o investimento volta o cliente para organização. **Importante:** assim como a confirmação de uma proposta, esses eventos de regressão (`nova_divida`, `usou_reserva_emergencia`) são informações que chegam de uma fonte externa verificada (o banco, ou uma confirmação estruturada equivalente) — nunca inferidos pela Rê a partir do que o cliente relata em texto livre na conversa. Se o cliente mencionar uma dívida nova no chat, a Rê reconhece e acolhe a informação, mas não muda o estado dele sozinha com base nisso.
- **Decisões críticas** (aceitar/recusar proposta, confirmar nova dívida) são capturadas por botões explícitos na interface, não por interpretação de texto livre — reduz ambiguidade em momentos que envolvem dinheiro real do cliente.
- **Conversa livre** é interpretada pelo LLM normalmente, exceto quando é preciso detectar um evento relevante para a máquina de estado, caso em que o LLM retorna uma saída estruturada (JSON com valores fixos), nunca texto livre.
- **Toda mensagem passa por uma verificação de escopo antes de ser respondida livremente.** O LLM classifica o assunto como `dentro_escopo` ou `fora_escopo` (finanças pessoais do cliente, dentro da jornada dívida → negociação → organização → investimento). Se `fora_escopo`, o backend não deixa o LLM improvisar uma resposta — retorna uma mensagem fixa e pré-definida explicando a limitação, evitando que a Rê seja levada a divagar sobre assuntos fora do seu propósito.

### 3.3 Comunicação em tempo real e mensagens proativas

O uso de WebSocket (em vez de requisições HTTP simples, como seria em uma versão Streamlit)
permite que a Rê envie mensagens **sem que o cliente tenha perguntado nada** — essencial
para a comemoração de pagamentos:

1. O banco confirma o pagamento de uma parcela (hoje simulado nos dados mockados; no futuro, via webhook real).
2. O backend identifica a conexão WebSocket ativa daquele cliente.
3. O backend gera uma mensagem de incentivo (variada, nunca repetida) e a envia diretamente pelo canal — a mensagem aparece no chat do cliente mesmo que ele não tenha feito nada.

### 3.4 Memória de curto prazo da conversa

APIs de LLM são sem estado — não lembram nada entre chamadas por conta própria. Para
que a Rê consiga referenciar o que foi dito antes na mesma sessão (ex.: "você mencionou
um gasto de R$ 450 com o carro"), o backend acumula o histórico de mensagens trocadas
(`historico_mensagens`, dentro do estado do cliente) e reenvia essa lista inteira a cada
nova chamada ao LLM — nunca só a última mensagem isolada. Essa memória existe apenas
durante a sessão ativa (ver limitação de persistência na seção 5); ela não sobrevive a
um reinício do backend.

## 4. Segurança e Prevenção de Alucinação

- **Dados nunca são inventados pelo LLM.** Toda informação financeira do cliente (saldo, renda, histórico) é buscada na base de dados pelo orquestrador *antes* de montar o prompt — o LLM recebe os números prontos, não os calcula nem os supõe.
- **Cálculos financeiros são feitos em Python puro**, não pelo LLM. Simulações de parcelamento, juros e limites de comprometimento de renda usam funções determinísticas e testáveis.
- **Decisões que comprometem dinheiro real usam interface estruturada** (botões), eliminando a ambiguidade de interpretação de linguagem natural nesses pontos.
- **Detecção de eventos usa saída estruturada (JSON com enum fixo)** em vez de texto livre, para o código nunca precisar "adivinhar" o que o LLM quis dizer.
- **A Rê não tem autoridade para fechar negociações.** Ela é consultiva: simula, calcula e apresenta propostas, mas a efetivação de qualquer acordo depende de autorização expressa do banco (representada no estado `aguardando_banco`). Isso limita o dano potencial de uma eventual alucinação ou má interpretação — a Rê nunca compromete o cliente financeiramente por conta própria.
- **A Rê recusa assuntos fora do seu escopo.** Perguntas fora do tema de finanças pessoais do cliente (ex.: previsão do tempo, esportes, assuntos pessoais não financeiros) recebem uma mensagem fixa informando a limitação, em vez de uma resposta livre do LLM — reduz o risco da Rê ser induzida a sair do seu propósito.
- **A Rê nunca trata uma informação autodeclarada pelo cliente como oficialmente confirmada.** Se o cliente relata algo novo em texto livre (ex.: "fiz uma dívida nova"), a Rê acolhe a informação com empatia, mas deixa explícito que os dados exibidos continuam sendo os últimos confirmados por um canal oficial — evitando que ela crie, sem querer, uma inconsistência entre o que diz na conversa e o que está de fato registrado no sistema. Essa regra foi adicionada após um teste real identificar que o LLM, sem essa instrução explícita, tratava relatos do cliente como se já estivessem atualizando o saldo devedor oficial.
- **A Rê reconhece os limites do seu escopo profissional:** não substitui aconselhamento jurídico ou financeiro profissional, e deve indicar isso explicitamente quando a situação ultrapassar sua capacidade. Especificamente, ao esgotar as tentativas de negociação (estado `negociacao_esgotada`), a Rê informa claramente ao cliente que ele deve procurar atendimento humano diretamente no banco — não tenta continuar simulando propostas sozinha.

## 5. Limitações Conhecidas do Ambiente de Testes

- **Provedor de LLM gratuito para desenvolvimento.** Durante o desenvolvimento e os testes deste projeto, a Rê é conectada a modelos gratuitos via `openrouter/free` (um roteador que seleciona automaticamente entre modelos abertos disponíveis sem custo). Esses modelos, por serem gratuitos e geralmente menores, ocasionalmente apresentam pequenas falhas de geração observadas em testes reais: palavras isoladas em outro idioma vazando no meio de uma resposta em português (ex.: um trecho em chinês ou russo), e metadados internos do provedor vazando como texto visível (ex.: a string `User Safety: safe` aparecendo antes de uma resposta). Isso é uma limitação do modelo usado para testes, não da arquitetura da Rê.
- **Com a memória de curto prazo, falhas de geração podem se propagar dentro da mesma sessão.** Antes de implementar o histórico de conversa (seção 3.4), cada resposta "nascia limpa". Agora, se o modelo gerar uma falha (ex.: um trecho de texto corrompido), essa falha fica registrada no histórico e pode ser referenciada como legítima em mensagens seguintes da mesma sessão, já que o modelo já "viu" aquilo. É um efeito colateral aceito da funcionalidade de memória, não um defeito da memória em si.
- **O LLM ocasionalmente realiza cálculos simples (ex.: porcentagens) diretamente na conversa**, apesar da instrução explícita de nunca calcular sozinho. Em testes, os valores calculados estavam corretos, mas isso não é garantido — o guardrail existe justamente para não depender da precisão do modelo em operações numéricas. Identificado em teste e registrado como limitação conhecida do modelo gratuito, não corrigido nesta versão por restrição de tempo.
- **Por design, o provedor de LLM é substituível por instituição.** Como documentado na arquitetura (`llm/client.py`, padrão Strategy), a escolha de qual LLM usar não é fixa no código — cada banco ou consultoria que viesse a contratar a Rê configuraria seu próprio provedor de produção (ex.: Claude, GPT, Gemini), com qualidade e confiabilidade comercial, sem exigir nenhuma mudança na máquina de estados, no motor de cálculo ou nos prompts.
- **Estado do cliente em memória, sem persistência real.** O `estados_ativos` no `main.py` é um dicionário Python guardado em memória, vivendo apenas enquanto o processo do backend está no ar. Ao reiniciar o servidor, todo o progresso da sessão (fase, tentativas de negociação, parcelas pagas) volta ao estado inicial dos dados mockados. Em produção, isso seria substituído por um banco de dados real — a máquina de estados e o motor de cálculo já foram desenhados de forma independente de onde o estado é guardado, então essa troca não exigiria alterar a lógica de negócio, apenas a camada de armazenamento.

## 6. Melhorias Futuras

Pontos identificados ao longo do desenvolvimento e dos testes, priorizados para uma
próxima versão do projeto:

### Produto
- **Dashboard financeiro detalhado do cliente** — hoje o Dashboard mostra só a posição na jornada (as 5 fases). Um próximo passo natural é um painel com a composição real dos gastos e entradas do cliente (usando `transacoes.csv` como base), gráficos de evolução da dívida e da reserva ao longo do tempo, e não só "em que fase estou".
- **Handoff real para atendimento humano** — hoje, ao esgotar as tentativas de negociação, a Rê apenas orienta o cliente a procurar o banco. Uma versão mais completa faria essa transição de forma mais integrada (ex.: abrir um chamado automaticamente).
- **Notificações fora do app** — mensagens proativas (como a comemoração de pagamento) hoje só chegam se o cliente estiver com o WebSocket aberto no momento exato. Em produção, isso pediria um canal assíncrono (e-mail, WhatsApp, push notification).

### Dados e Integrações
- **Persistência real com banco de dados**, substituindo o estado em memória (limitação já detalhada acima).
- **Integração com API bancária real**, substituindo os arquivos mockados e as simulações manuais de eventos do banco (`banco_confirmou`, `banco_recusou`) por webhooks de verdade.
- **Configuração de LLM por instituição**, não só por variável de ambiente global — hoje o padrão Strategy já suporta múltiplos provedores no código, mas falta a camada de configuração que permita cada banco/consultoria escolher o seu, de fato, sem editar o `.env` manualmente.

### Confiabilidade Técnica
- **Proteger `gerar_resposta` contra falhas do provedor de LLM.** Hoje só a chamada de classificação de escopo tem `try/except`; uma queda da chamada principal (ex.: limite de requisições do plano gratuito, como aconteceu durante os testes) ainda derruba a conexão WebSocket sem tratamento.
- **Provedor de LLM comercial em produção**, reduzindo os artefatos de geração observados em teste (vazamento de idioma, metadados internos aparecendo como texto, cálculos informais feitos pelo modelo apesar da instrução contrária).
- **Pipeline de coleta automatizada das métricas** definidas no `docs/04-metricas.md` — hoje são conceituais, sem instrumentação real além dos logs manuais observados em teste.

### Limpeza de Código
- **`PROMPT_DETECCAO_EVENTO`** foi escrito em `llm/prompts.py`, mas nunca conectado ao `main.py` — a decisão de design (seção 3.2) foi que eventos de regressão financeira devem vir de fonte externa verificada, não de detecção por texto livre. Vale decidir explicitamente se esse prompt deve ser removido (não tem mais uso previsto) ou adaptado para outro propósito.