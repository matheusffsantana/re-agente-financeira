import { useWebSocket } from "./hooks/useWebSocket";
import Chat from "./components/Chat";
import Dashboard from "./components/Dashboard";
import PropostaBanco from "./components/PropostaBanco";

const CLIENTE_ID = "cli_002";

export default function App() {

    const { mensagens, faseAtual, proposta, enviarMensagem, enviarDecisao } = useWebSocket(CLIENTE_ID);

    return (
        <div className="app">
            <h1>Rê — sua parceira para sair do vermelho</h1>
            <Dashboard faseAtual={faseAtual} />
            <PropostaBanco proposta={proposta} aoDecidir={enviarDecisao} />
            <Chat mensagens={mensagens} aoEnviar={enviarMensagem} />
        </div>
    );
}