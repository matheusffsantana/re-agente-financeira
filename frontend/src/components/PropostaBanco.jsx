export default function PropostaBanco({ proposta, aoDecidir }) {
    if (proposta == null) {
        return null;
    }
    return (
        <div className="proposta-banco">
            <p>
                O banco propôs: {proposta.numero_parcelas}x de R$ {proposta.valor_parcela.toFixed(2)}
            </p>
            <div className="proposta-botoes">
                <button onClick={() => aoDecidir("proposta_aceita_pelo_cliente")}>✅ Aceitar</button>
                <button onClick={() => aoDecidir("proposta_recusada")}>❌ Recusar</button>
            </div>
        </div>
    );
}