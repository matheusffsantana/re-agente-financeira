const FASES = ["diagnostico", "negociacao", "aguardando_banco", "organizacao", "investimento"];

const ROTULOS = {
    diagnostico: "Diagnóstico",
    negociacao: "Negociação",
    aguardando_banco: "Aguardando o banco",
    organizacao: "Organização",
    investimento: "Investimento",
};

export default function Dashboard({ faseAtual }) {
    const indiceFaseAtual = FASES.indexOf(faseAtual);


    return (
        <div className="dashboard">
            {FASES.map((fase, i) => (
                <div key={fase} className={`dashboard-fase ${i <= indiceFaseAtual ? "dashboard-fase-atual" : ""}`}>
                    {ROTULOS[fase]}
                </div>
            ))}
        </div>
    );
}