# Base de Conhecimento — Estratégia de Dados

## 1. Visão geral

Os dados mockados foram adaptados para alimentar diretamente a máquina de estados e o
motor de cálculo do Rê (ver `docs/01-documentacao-agente.md`). Cada campo existe porque
uma regra de negócio específica depende dele — não há dado "decorativo".

Três clientes fictícios cobrem fases distintas da jornada, permitindo testar o agente em
pontos diferentes do fluxo sem precisar simular a jornada inteira manualmente a cada teste:

| Cliente | Fase | O que essa fase testa |
|---|---|---|
| Bruna Andrade (`cli_001`) | `diagnostico` | Coleta inicial de dados e cálculo de comprometimento de renda |
| Carlos Nogueira (`cli_002`) | `aguardando_banco` | Limite de tentativas de negociação (já recusou 2 propostas) e o portão de autorização do banco |
| Fernanda Lima (`cli_003`) | `organizacao` | Mensagens comemorativas (9 de 12 parcelas já pagas) e proximidade da transição para `investimento` |

## 2. Arquivos e seus papéis

### `perfil_investidor.json` — Perfil e estado do cliente
Fonte única de verdade para o estado do cliente na máquina de estados. Contém os campos
que `avaliar_transicao()` usa diretamente: `fase`, `saldo_devedor`, `tentativas_negociacao`,
`reserva_atual`, `meta_reserva`. O campo `perfil_investidor` (conservador/moderado/arrojado)
só é preenchido quando o cliente se aproxima da fase de investimento — reflete que esse
dado só existe no mundo real depois que o cliente responde ao questionário de perfil.

### `historico_atendimento.csv` — Log de eventos
Cada linha corresponde a um `evento` do mesmo vocabulário usado na máquina de estados
(`proposta_recusada`, `proposta_aceita_pelo_cliente`, `banco_confirmou`, `parcela_paga`
etc.). Isso não é coincidência: o histórico é o que teria disparado essas transições em um
sistema real, e reaproveitar os mesmos nomes evita uma camada de tradução desnecessária
entre "o que aconteceu" e "o que o código entende".

### `transacoes.csv` — Detalhamento de renda e gastos
Granularidade mensal por categoria, usada pelo motor de cálculo para simular o quanto do
orçamento do cliente já está comprometido — a informação com que o `perfil_investidor.json`
resume em `gastos_fixos`/`gastos_variaveis` vem, na prática, de somar estas linhas.

### `produtos_financeiros.json` — Catálogo de produtos
Dividido em dois blocos que correspondem a duas fases diferentes da jornada:
- **`negociacao`**: as opções que o motor de cálculo usa para simular propostas (parcelamento, desconto à vista, refinanciamento), com as taxas necessárias para o cálculo de comprometimento de renda.
- **`investimento`**: produtos filtrados por `perfil_recomendado`, cruzando com o `perfil_investidor` do cliente — é assim que o Rê evita recomendar um fundo de risco médio para alguém com perfil conservador.

## 3. Por que esses dados evitam alucinação

Como definido na Etapa 1, o LLM nunca recebe a tarefa de "lembrar" ou "estimar" esses
números — o backend sempre busca o valor exato nesses arquivos antes de montar qualquer
prompt. Isso significa que qualquer dúvida sobre "por que o Rê disse esse valor" tem uma
resposta rastreável: o dado veio de uma linha específica de um desses arquivos, nunca de
uma inferência do modelo.

## 4. Evolução futura

Hoje os arquivos são estáticos e lidos do disco. O desenho já antecipa a substituição por
uma API bancária real (mencionada na visão original do projeto): a estrutura de campos foi
pensada para que essa troca seja apenas na camada de acesso a dados, sem alterar a máquina
de estados nem o motor de cálculo.