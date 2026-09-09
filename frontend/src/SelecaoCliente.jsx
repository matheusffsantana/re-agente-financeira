const CLIENTES_TESTE = [
  {
    id: "cli_001",
    nome: "Bruna",
    fase: "Diagnóstico",
    descricao: "Acabou de chegar, ainda sem negociação iniciada. Bom para testar acolhimento inicial e coleta de dados.",
  },
  {
    id: "cli_002",
    nome: "Carlos",
    fase: "Aguardando o banco",
    descricao: "Já recusou 2 propostas e aceitou a 3ª, esperando confirmação. Bom para testar o limite de tentativas e geração de proposta real.",
  },
  {
    id: "cli_003",
    nome: "Fernanda",
    fase: "Organização",
    descricao: "Já negociou e está pagando as parcelas, perto de completar a reserva. Bom para testar comemoração de pagamento e tom encorajador.",
  },
];

export default function SelecaoCliente({ aoSelecionar }) {
  return (
    <div className="selecao-cliente">
      <h1>Rê — Ambiente de testes</h1>
      <p>Escolha um cliente para simular a conversa:</p>

      {CLIENTES_TESTE.map((cliente) => (
        <div key={cliente.id} className="cliente">
          <h2>{cliente.nome}</h2>
          <p><strong>Fase:</strong> {cliente.fase}</p>
          <p>{cliente.descricao}</p>
          <button onClick={() => aoSelecionar(cliente.id)}>Selecionar</button>
        </div>
      ))}

    </div>
  );
}