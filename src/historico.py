#!/usr/bin/env python3
"""
Reconstrói a evolução histórica do RSC-TAE a partir do histórico git.

Percorre os commits que alteraram ``docs/data/agg_summary.json``, mantém o
último snapshot de cada dia e grava ``docs/data/historico.csv``. Os dados são
apenas agregados (sem PII), os mesmos já publicados em ``agg_summary.json``.

Uso: python src/historico.py
"""

import csv
import json
import os
import subprocess
from typing import Dict, List, Optional

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SUMMARY_PATH = "docs/data/agg_summary.json"
OUTPUT_PATH = os.path.join(ROOT, "docs", "data", "historico.csv")

COLUNAS = [
    "data",
    "commit",
    "total_avaliados",
    "total_tae_ativos",
    "taxa_cobertura_pct",
    "total_campi",
    "total_cargos",
    "rsc_iii",
    "rsc_v",
    "rsc_vi",
    "capital",
    "interior",
    "observacao",
]


def git(*args: str) -> str:
    """Executa um comando git na raiz do repositório e devolve o stdout."""
    try:
        return subprocess.run(
            ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Falha ao executar git {' '.join(args)}: {exc.stderr.strip()}")


def ultimo_commit_por_dia() -> Dict[str, str]:
    """Mapeia data (AAAA-MM-DD) -> hash do último commit do dia que tocou o resumo."""
    saida = git("log", "--reverse", "--format=%H %as", "--", SUMMARY_PATH)
    por_dia: Dict[str, str] = {}
    for linha in saida.splitlines():
        h, dia = linha.split()
        por_dia[dia] = h  # --reverse: o último a ser lido é o mais recente do dia
    return por_dia


def ler_snapshot(commit: str) -> Optional[dict]:
    try:
        return json.loads(git("show", f"{commit}:{SUMMARY_PATH}"))
    except (json.JSONDecodeError, SystemExit):
        return None


def montar_linha(dia: str, commit: str, resumo: dict) -> Optional[Dict[str, object]]:
    meta = resumo.get("meta", {})
    total = meta.get("total_geral_avaliados")
    if total is None:
        return None
    niveis = resumo.get("distribuicao_niveis", {})
    tipos = resumo.get("distribuicao_tipo_campus", {})
    ativos = meta.get("total_tae_ativos")  # ausente no primeiro schema
    cobertura = meta.get("taxa_cobertura_global_pct")
    return {
        "data": dia,
        "commit": commit[:7],
        "total_avaliados": total,
        "total_tae_ativos": ativos if ativos is not None else "",
        "taxa_cobertura_pct": cobertura if cobertura is not None else "",
        "total_campi": meta.get("total_campi_atendidos", ""),
        "total_cargos": meta.get("total_cargos_atendidos", ""),
        "rsc_iii": niveis.get("RSC-III", 0),
        "rsc_v": niveis.get("RSC-V", 0),
        "rsc_vi": niveis.get("RSC-VI", 0),
        "capital": tipos.get("Capital", 0),
        "interior": tipos.get("Interior", 0),
        "observacao": "",
    }


def anotar_descontinuidades(linhas: List[Dict[str, object]]) -> None:
    """Marca quedas no total e mudanças no denominador entre snapshots consecutivos."""
    for ant, atual in zip(linhas, linhas[1:]):
        notas = []
        if atual["total_avaliados"] < ant["total_avaliados"]:
            notas.append("queda no total (possível falha de coleta ou revisão da fonte)")
        if ant["total_tae_ativos"] != "" and atual["total_tae_ativos"] != ant["total_tae_ativos"]:
            notas.append("mudança no total de TAE ativos")
        if ant["total_tae_ativos"] == "" and atual["total_tae_ativos"] != "":
            notas.append("novo schema")
        atual["observacao"] = "; ".join(notas)


def main() -> None:
    linhas: List[Dict[str, object]] = []
    for dia, commit in sorted(ultimo_commit_por_dia().items()):
        resumo = ler_snapshot(commit)
        linha = montar_linha(dia, commit, resumo) if resumo else None
        if linha:
            linhas.append(linha)

    anotar_descontinuidades(linhas)

    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)

    print(f"✓ {len(linhas)} snapshots diários gravados em {os.path.relpath(OUTPUT_PATH, ROOT)}")


if __name__ == "__main__":
    main()
