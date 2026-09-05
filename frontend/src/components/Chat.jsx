import { useState } from "react";

export default function Chat({ mensagens, aoEnviar }) {
  const [texto, setTexto] = useState("");

  function handleEnviar() {
    if (texto.trim() === "") {
      return;
    }
    aoEnviar(texto);
    setTexto("");
  }

  return (
    <div className="chat">
      <div className="chat-mensagens">
        {mensagens.map((mensagem, indice) => (
          <div key={indice} className={`mensagem mensagem-${mensagem.autor}`}>
            {mensagem.texto}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleEnviar()}
          placeholder="Converse com a Rê..."
        />
        <button onClick={handleEnviar}>Enviar</button>
      </div>
    </div>
  );
}