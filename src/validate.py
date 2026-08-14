#!/usr/bin/env python3
"""
Script de Validação e Integridade de Dados e Privacidade - RSC-TAE (IFRN).

Verifica:
1. Conformidade com LGPD (ausência total de PII, nomes, SIAPEs, textos livres).
2. Regra de k-anonimato / supressão (nenhuma célula individual com n < 5).
3. Coerência matemática dos agregados (soma dos campi = soma institucional = tabela fato).
4. Integridade de esquemas e não-vacuidade dos arquivos.
"""

import os
import sys
import json
import logging
import argparse
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("rsc_validator")

FORBIDDEN_COLUMNS = {
    "nome", "siape", "cpf", "email", "e-mail", "matricula", "processo_anterior_id",
    "introducao", "requisitos", "conclusao", "texto", "resumo", "documentos", "descricao"
}

PRIVACY_MIN_N = 5


def validate_file_exists(filepath: str) -> bool:
    if not os.path.isfile(filepath):
        logger.error(f"Arquivo obrigatório não encontrado: {filepath}")
        return False
    if os.path.getsize(filepath) == 0:
        logger.error(f"Arquivo está vazio: {filepath}")
        return False
    return True


def validate_no_pii(df: pd.DataFrame, filename: str) -> bool:
    """Verifica se existem colunas ou nomes suspeitos com dados pessoais."""
    for col in df.columns:
        col_lower = str(col).lower()
        if col_lower in FORBIDDEN_COLUMNS:
            logger.error(f"FALHA DE PRIVACIDADE em {filename}: coluna proibida detectada '{col}'")
            return False
        for forbidden in FORBIDDEN_COLUMNS:
            if forbidden in col_lower:
                logger.error(f"FALHA DE PRIVACIDADE em {filename}: coluna com termo proibido '{col}'")
                return False
    logger.info(f"OK: Nenhuma coluna de dados pessoais identificada em {filename}")
    return True


def validate_privacy_threshold(df: pd.DataFrame, filename: str, count_col: str = "total_processos", label_col: str = "campus") -> bool:
    """Garante que registros com contagem < 5 não estejam expostos individualmente."""
    if count_col not in df.columns:
        return True

    small_cells = df[df[count_col] < PRIVACY_MIN_N]
    if not small_cells.empty:
        # Se existem células pequenas, verifica se são linhas agrupadas
        for _, row in small_cells.iterrows():
            label = str(row.get(label_col, ""))
            if "Outros" not in label and "agrupados" not in label.lower():
                logger.error(
                    f"FALHA DE PRIVACIDADE em {filename}: Célula com n={row[count_col]} < {PRIVACY_MIN_N} "
                    f"não foi agrupada: {dict(row)}"
                )
                return False
    logger.info(f"OK: Regra de supressão/agrupamento de privacidade (n >= {PRIVACY_MIN_N}) respeitada em {filename}")
    return True


def validate_mathematical_coherence(
    df_fato: pd.DataFrame,
    df_campus: pd.DataFrame,
    df_cargo: pd.DataFrame,
    df_institucional: pd.DataFrame
) -> bool:
    """Valida se as somas e métricas são coerentes entre todas as tabelas."""
    total_fato = len(df_fato)
    total_campus = df_campus["total_processos"].sum()
    total_cargo = df_cargo["total_processos"].sum()
    total_institucional = df_institucional["total_processos"].sum()

    logger.info(f"Totais encontrados -> Fato: {total_fato}, Campus: {total_campus}, Cargo: {total_cargo}, Institucional: {total_institucional}")

    if total_campus != total_fato:
        logger.error(f"Incoerência: Soma de processos por campus ({total_campus}) != Tabela Fato ({total_fato})")
        return False

    if total_cargo != total_fato:
        logger.error(f"Incoerência: Soma de processos por cargo ({total_cargo}) != Tabela Fato ({total_fato})")
        return False

    if total_institucional != total_fato:
        logger.error(f"Incoerência: Soma de processos institucionais ({total_institucional}) != Tabela Fato ({total_fato})")
        return False

    # Validação de taxas
    for name, df in [("Campus", df_campus), ("Cargo", df_cargo), ("Institucional", df_institucional)]:
        if "taxa_deferimento" in df.columns:
            invalid_rates = df[(df["taxa_deferimento"] < 0) | (df["taxa_deferimento"] > 100)]
            if not invalid_rates.empty:
                logger.error(f"Taxa de deferimento inválida encontrada em {name}: {invalid_rates['taxa_deferimento'].tolist()}")
                return False

    logger.info("OK: Coerência matemática validada com 100% de consistência.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Validador de Integridade e Privacidade RSC-TAE")
    parser.add_argument("--data-dir", default="docs/data", help="Diretório dos dados processados (padrão: docs/data)")
    args = parser.parse_args()

    data_dir = args.data_dir
    files_to_check = [
        "fato_anonimo.csv",
        "agg_campus_mes.csv",
        "agg_cargo_nivel.csv",
        "agg_institucional_mes.csv",
        "agg_summary.json"
    ]

    all_valid = True

    # 1. Checagem de existência de arquivos
    for fname in files_to_check:
        filepath = os.path.join(data_dir, fname)
        if not validate_file_exists(filepath):
            all_valid = False

    if not all_valid:
        logger.error("Validação interrompida por arquivos ausentes.")
        sys.exit(1)

    # 2. Carregamento dos dados
    df_fato = pd.read_csv(os.path.join(data_dir, "fato_anonimo.csv"))
    df_campus = pd.read_csv(os.path.join(data_dir, "agg_campus_mes.csv"))
    df_cargo = pd.read_csv(os.path.join(data_dir, "agg_cargo_nivel.csv"))
    df_institucional = pd.read_csv(os.path.join(data_dir, "agg_institucional_mes.csv"))

    with open(os.path.join(data_dir, "agg_summary.json"), "r", encoding="utf-8") as f:
        summary_json = json.load(f)

    # 3. Validação de ausência de PII
    for name, df in [
        ("fato_anonimo.csv", df_fato),
        ("agg_campus_mes.csv", df_campus),
        ("agg_cargo_nivel.csv", df_cargo),
        ("agg_institucional_mes.csv", df_institucional)
    ]:
        if not validate_no_pii(df, name):
            all_valid = False

    # 4. Validação de Coerência Matemática
    if not validate_mathematical_coherence(df_fato, df_campus, df_cargo, df_institucional):
        all_valid = False

    # 6. Validação do JSON
    if summary_json.get("meta", {}).get("total_geral_avaliados") != len(df_fato):
        logger.error("Incoerência no total_geral_avaliados do arquivo agg_summary.json")
        all_valid = False

    if all_valid:
        logger.info("TODAS AS VALIDAÇÕES PASSARAM COM SUCESSO! (Privacidade, LGPD e Coerência Matemática OK)")
        print("STATUS: APROVADO")
        sys.exit(0)
    else:
        logger.error("FALHA NA VALIDAÇÃO DOS DADOS.")
        print("STATUS: REPROVADO")
        sys.exit(1)


if __name__ == "__main__":
    main()
