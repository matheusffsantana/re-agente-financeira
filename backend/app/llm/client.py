import json
import os
from openai import OpenAI

_cliente_openrouter = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


def _gerar_resposta_openrouter(system_prompt: str, mensagens: list[dict]) -> str:
    resposta = _cliente_openrouter.chat.completions.create(
        model="openrouter/free",
        messages=[{"role": "system", "content": system_prompt}] + mensagens,  # type: ignore[arg-type]
    )
    conteudo = resposta.choices[0].message.content
    if conteudo is None:
        raise ValueError("O modelo não retornou texto na resposta.")
    return conteudo


PROVEDORES = {
    "openrouter": _gerar_resposta_openrouter,
}


def gerar_resposta(system_prompt: str, mensagens: list[dict]) -> str:
    nome_provedor = os.environ.get("LLM_PROVIDER", "openrouter")
    funcao_provedor = PROVEDORES.get(nome_provedor)
    if funcao_provedor is None:
        raise ValueError(f"Provedor de LLM não configurado ou desconhecido: {nome_provedor}")
    return funcao_provedor(system_prompt, mensagens)


def classificar_estruturado(prompt_classificacao: str) -> dict:
    resposta_texto = gerar_resposta("", [{"role": "user", "content": prompt_classificacao}])
    return json.loads(resposta_texto)