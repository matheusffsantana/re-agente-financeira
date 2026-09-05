import { useEffect, useRef, useState } from "react";

export function useWebSocket(clienteId) {
  const [mensagens, setMensagens] = useState([]);
  const [faseAtual, setFaseAtual] = useState(null);
  const [proposta, setProposta] = useState(null);
  const socketRef = useRef(null);

  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/${clienteId}`);
    socketRef.current = socket;

    socket.onmessage = (evento) => {
      const dado = JSON.parse(evento.data);

      if (dado.tipo === "mensagem") {
        setMensagens((anteriores) => [...anteriores, { autor: dado.autor, texto: dado.texto }]);
      } else if (dado.tipo === "estado") {
        setFaseAtual(dado.fase);
      } else if (dado.tipo === "proposta") {
        setProposta(dado.proposta);
      }
    };

    return () => socket.close();
  }, [clienteId]);

  function enviarMensagem(texto) {
    setMensagens((anteriores) => [...anteriores, { autor: "cliente", texto }]);
    socketRef.current?.send(JSON.stringify({ tipo: "mensagem", texto }));
  }

  function enviarDecisao(evento) {
    socketRef.current?.send(JSON.stringify({ tipo: "decisao", evento }));
    setProposta(null);
  }

  return { mensagens, faseAtual, proposta, enviarMensagem, enviarDecisao };
}