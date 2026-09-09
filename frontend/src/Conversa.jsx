import { useWebSocket } from "./hooks/useWebSocket";
import Chat from "./components/Chat";
import Dashboard from "./components/Dashboard";
import PropostaBanco from "./components/PropostaBanco";

export default function Conversa({ clienteId, aoVoltar }) {
  const { mensagens, faseAtual, proposta, enviarMensagem, enviarDecisao } = useWebSocket(clienteId);

  return (
    <div className="app">
      <button onClick={aoVoltar} className="botao-voltar">← Voltar para seleção</button>
      <h1>Rê — sua parceira para sair do vermelho</h1>
      <Dashboard faseAtual={faseAtual} />
      <PropostaBanco proposta={proposta} aoDecidir={enviarDecisao} />
      <Chat mensagens={mensagens} aoEnviar={enviarMensagem} />
    </div>
  );
}