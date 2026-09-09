import { useState } from "react";
import SelecaoCliente from "./SelecaoCliente";
import Conversa from "./Conversa";

export default function App() {
  const [clienteSelecionado, setClienteSelecionado] = useState(null);

  if (clienteSelecionado === null) {
    return <SelecaoCliente aoSelecionar={setClienteSelecionado} />;
  }
  return <Conversa clienteId={clienteSelecionado} aoVoltar={() => setClienteSelecionado(null)} />;
}