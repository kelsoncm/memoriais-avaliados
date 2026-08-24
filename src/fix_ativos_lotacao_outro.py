#!/usr/bin/env python3
"""
Correção pontual do quadro de TAEs ativos (data/quadro_tae_ativos.csv e
docs/data/quadro_tae_ativos.csv).

Causa raiz (ver src/debug_outro_ativos.py): 25 servidores ativos estão em
situação funcional especial (cedidos, exercício provisório, colaboração
técnica etc.) e por isso não têm campus_lotacao no SIAPE — o campo vem
vazio ("-"). O export do SUAP, porém, sempre tem setor_exercicio/
campus_exercicio preenchidos para esses casos. process.py já documenta a
regra (linha 54): usar o campus de exercício como fallback quando não há
lotação. Este script aplica esse fallback nos 25 registros afetados,
mantendo intactos os outros 1166 registros e a ordem/id_anonimo do
arquivo já publicado.

Não gera nem depende de nenhum arquivo com PII: cruza export_suap.csv
(fonte local, gitignorada) apenas para obter o campus de exercício, e
grava de volta somente cargo/lotacao (sem nome/matrícula) nos CSVs já
públicos.
"""

import sys
import pandas as pd

EXPORT_SUAP_PATH = "data/export_suap.csv"
TARGETS = ["data/quadro_tae_ativos.csv", "docs/data/quadro_tae_ativos.csv"]

APOSENTADO = "APOSENTADO - 02"


def is_missing(v) -> bool:
    return pd.isna(v) or str(v).strip() in ("-", "", "nan", "NaN")


def fallback_exercicio(row) -> str:
    # Usa direto o campus_exercicio (sigla "crua", ex: "CNAT", "RE"), e não
    # setor_exercicio: em parte dos registros esse campo vem sem o sufixo
    # "/campus" (ex: "PROJU", "DIAES", "COBIB"), o que faria parse_lotacao
    # tratar o próprio setor como se fosse a sigla do campus.
    if not is_missing(row["campus_exercicio"]):
        return row["campus_exercicio"]
    raise ValueError(f"Sem campus_exercicio disponível para: {row['nome']}")


def main():
    sup = pd.read_csv(EXPORT_SUAP_PATH, dtype=str)
    ativos = sup[sup["situacao"].astype(str).str.strip() != APOSENTADO].copy()

    sem_lotacao = ativos[ativos["campus_lotacao"].apply(is_missing)].copy()
    sem_lotacao["fallback"] = sem_lotacao.apply(fallback_exercicio, axis=1)
    print(f"Registros com campus_lotacao ausente em export_suap.csv: {len(sem_lotacao)}")

    # Agrupa os valores de fallback por cargo. id_anonimo não carrega
    # identidade real, então quando há mais de uma pessoa com o mesmo
    # cargo afetado, a ordem de atribuição dentro do grupo é irrelevante
    # para a correção estatística agregada — o que importa é que o
    # conjunto certo de campi entre no lugar certo de cargo.
    fallback_by_cargo = {}
    for cargo, group in sem_lotacao.groupby("cargo"):
        fallback_by_cargo[cargo] = group["fallback"].tolist()

    for path in TARGETS:
        qta = pd.read_csv(path, dtype=str)
        mask = qta["lotacao"] == "-"
        idx = qta.index[mask].tolist()

        if len(idx) != len(sem_lotacao):
            print(
                f"ABORTADO em {path}: esperava {len(sem_lotacao)} linhas com "
                f"lotacao == '-', encontrou {len(idx)}. Verifique manualmente antes de reexecutar."
            )
            sys.exit(1)

        pending = {cargo: list(vals) for cargo, vals in fallback_by_cargo.items()}
        for row_idx in idx:
            cargo = qta.at[row_idx, "cargo"]
            if cargo not in pending or not pending[cargo]:
                print(
                    f"ABORTADO em {path}, linha {row_idx} (id_anonimo="
                    f"{qta.at[row_idx, 'id_anonimo']}): nenhum fallback disponível "
                    f"para o cargo '{cargo}'. Verifique manualmente."
                )
                sys.exit(1)
            qta.at[row_idx, "lotacao"] = pending[cargo].pop()

        qta.to_csv(path, index=False, encoding="utf-8")
        print(f"Corrigido: {path} ({len(idx)} registros atualizados)")


if __name__ == "__main__":
    main()
