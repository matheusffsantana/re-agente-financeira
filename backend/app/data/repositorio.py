from pathlib import Path
import json
import csv

BASE_DIR = Path(__file__).resolve().parents[3] / "data"

def carregar_perfil_cliente(cliente_id: str) -> dict:
    """
    Carrega o perfil do cliente a partir de um arquivo JSON.

    Args:
        cliente_id (str): O ID do cliente.

    Returns:
        dict: O perfil do cliente.
    """
    with open(BASE_DIR / "perfil_investidor.json", encoding="utf-8") as file:
        perfis = json.load(file)
    for perfil in perfis:
        if perfil.get("cliente_id") == cliente_id:
            return perfil
    raise ValueError(f"Cliente {cliente_id} não encontrado.")


def carregar_historico(cliente_id: str) -> list[dict]:
    with open(BASE_DIR / "historico_atendimento.csv", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    resultado = [linha for linha in linhas if linha["cliente_id"] == cliente_id]
    return resultado

def carregar_transacoes(cliente_id: str) -> list[dict]:
    with open(BASE_DIR / "transacoes.csv", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    resultado = [linha for linha in linhas if linha["cliente_id"] == cliente_id]
    return resultado

def carregar_produtos_financeiros() -> dict:
    with open(BASE_DIR / "produtos_financeiros.json", encoding="utf-8") as f:
        produtos_financeiros = json.load(f)
    return produtos_financeiros