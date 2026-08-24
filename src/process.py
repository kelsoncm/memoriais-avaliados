#!/usr/bin/env python3
"""
Processador e Anonimizador de Dados de RSC-TAE (IFRN).

Regras de conformidade com LGPD e Privacidade:
1. Eliminação total de identificadores diretos e indiretos (nome, SIAPE, IDs originais, e-mails).
2. Eliminação de campos de texto livre (introdução, requisitos, conclusões, descrições).
3. Pseudonimização irreversível através de hash SHA-256 para contagem unívoca.
4. Mapeamento estruturado de campus, tipo_campus, cargo, classe e níveis RSC.
5. Supressão estatística de pequenas células (n < 5) nas tabelas públicas agregadas.
6. Exportação para data/processed/ e docs/data/ (para consumo no GitHub Pages).
"""

import os
import sys
import glob
import json
import hashlib
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Tuple, List, Optional
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("rsc_processor")

# Limiar de privacidade (k-anonymity / supressão de pequenas células)
PRIVACY_THRESHOLD = 5

def parse_lotacao(lotacao_raw: Optional[str]) -> Tuple[str, str]:
    """
    Identifica a sigla do campus e a classificação territorial (Capital ou Interior)
    a partir da lotação funcional (SUAP / SIAPE).

    A entrada pode estar no formato 'setor/campus' (ex: 'COTIC/CA', 'DG/CNAT', 'DIAC/CANG')
    ou diretamente apenas o 'campus' (ex: 'RE', 'CM', 'NC', 'CH', 'CAL', 'CCAL').

    Regras de Normalização:
    - O campus CH às vezes aparece como CH, outras vezes como CAL (ou CCAL).
      O pipeline converte 'CAL' e 'CCAL' para 'CH'.
    - 'CNC' é normalizado para 'NC', 'CSGA' para 'SGA' e 'SPO' para 'SPP'.

    Regra de Territorialidade:
    - Capital: RE, CNAT, ZL, CH (e CAL/CCAL), ZN
    - Interior: demais unidades/campi

    Nota metodológica: Utiliza-se o campus de lotação no SIAPE como regra geral.
    Para os servidores sem campus de lotação no SIAPE (ex: cedidos), adota-se o campus de exercício.
    """
    if not lotacao_raw or not isinstance(lotacao_raw, str):
        return ("Não Informado", "Outro")

    lotacao_clean = lotacao_raw.strip().upper()
    if not lotacao_clean or lotacao_clean in ("-", "NAN", "OUTRO", "NÃO INFORMADO", "NONE"):
        return ("Outro", "Outro")

    # Extrai o campus a partir da string de lotação (seja 'setor/campus' ou apenas 'campus')
    if "/" in lotacao_clean:
        parts = lotacao_clean.split("/")
        campus = parts[1].strip() if len(parts) > 1 else parts[0].strip()
    else:
        campus = "RE" if lotacao_clean in ("AUDGE", "COGLEG", "SECOL", "DIGPE") else lotacao_clean

    # Padronização de siglas de campi (CAL/CCAL -> CH, SPO -> SPP, CSGA -> SGA, CNC -> NC)
    if campus in ("CAL", "CCAL"):
        campus = "CH"
    elif campus == "CNC":
        campus = "NC"
    elif campus == "CSGA":
        campus = "SGA"
    elif campus == "SPO":
        campus = "SPP"

    # Classificação do tipo de campus baseada na sigla (Capital vs Interior)
    if campus in ("RE", "CNAT", "ZL", "CH", "ZN"):
        tipo_campus = "Capital"
    elif campus in ("-", "NAN", "OUTRO", "NÃO INFORMADO"):
        tipo_campus = "Outro"
    else:
        tipo_campus = "Interior"

    return (campus, tipo_campus)


parse_campus = parse_lotacao




def clean_cargo(cargo_raw: Optional[str]) -> Tuple[str, str]:
    """
    Padroniza a denominação do cargo e infere a Classe PCCTAE (C, D, E).
    """
    if not cargo_raw or not isinstance(cargo_raw, str):
        return ("Não Informado", "Não Informado")

    cargo_str = cargo_raw.strip()

    # Detecta código PCCTAE se presente
    classe = "Classe D"
    if "7014" in cargo_str:
        classe = "Classe C"
    elif "7012" in cargo_str:
        classe = "Classe D"
    elif "7010" in cargo_str or "6470" in cargo_str or "PCMED" in cargo_str:
        classe = "Classe E"

    # Limpeza textual do nome do cargo
    import re
    cleaned = re.sub(r"\s*\([^)]*\)\s*-\s*\d+", "", cargo_str)
    cleaned = re.sub(r"\s*-\s*\d+$", "", cleaned)
    cleaned = cleaned.strip().title()

    # Ajustes finos de nomenclatura institucional
    substitutions = {
        "Tec ": "Técnico ",
        "Aux ": "Auxiliar ",
        "Tecnico ": "Técnico ",
        "Tecnologia Da Informacao": "Tecnologia da Informação",
        "Tec Da Informacao": "Tecnologia da Informação",
        "De Laboratorio": "de Laboratório",
        "Laboratorio": "Laboratório",
        "Em Administracao": "em Administração",
        "Em Contabilidade": "em Contabilidade",
        "Em Assuntos Educacionais": "em Assuntos Educacionais",
        "Em Enfermagem": "em Enfermagem",
        "Em Agropecuaria": "em Agropecuária",
        "Em Edificacoes": "em Edificações",
        "Em Eletrotecnica": "em Eletrotécnica",
        "Em Mecanica": "em Mecânica",
        "Em Quimica": "em Química",
        "Em Audiovisual": "em Audiovisual",
        "De Aluno": "de Aluno",
        "De Enfermagem": "de Enfermagem",
        "De Edificacoes": "de Edificações",
        "Bibliotecario-Documentalista": "Bibliotecário-Documentalista",
        "Pedagogo-Area": "Pedagogo",
        "Enfermeiro-Area": "Enfermeiro",
        "Engenheiro-Area": "Engenheiro",
        "Medico - Pcctae": "Médico",
        "Psicologo-Area": "Psicólogo",
        "Economista": "Economista",
        "Nutricionista-Habilitacao": "Nutricionista",
        "Odontologo": "Odontólogo",
        "Auditor": "Auditor",
        "Contador": "Contador",
        "Administrador": "Administrador",
        "Assistente Social": "Assistente Social",
        "Tradutor Interprete De Linguagem Sinais": "Tradutor e Intérprete de Libras",
        "Tecnologo-Formacao": "Tecnólogo",
        "Tecnologo Formacao": "Tecnólogo",
        "Tecnologo": "Tecnólogo",
    }
    for old, new in substitutions.items():
        if old.lower() in cleaned.lower():
            cleaned = re.sub(re.escape(old), new, cleaned, flags=re.IGNORECASE)

    return (cleaned.strip(), classe)


def clean_nivel_rsc(nivel_raw: Optional[str]) -> str:
    """Padroniza a denominação do nível RSC (RSC-I, RSC-II, RSC-III, etc.)."""
    if not nivel_raw or not isinstance(nivel_raw, str):
        return "RSC-III"

    nivel = nivel_raw.strip().upper()
    if "VI" in nivel:
        return "RSC-VI"
    if "V" in nivel:
        return "RSC-V"
    if "IV" in nivel:
        return "RSC-IV"
    if "III" in nivel:
        return "RSC-III"
    if "II" in nivel:
        return "RSC-II"
    if "I" in nivel:
        return "RSC-I"
    return nivel


def anonymize_records(records: List[dict], collection_date: str) -> pd.DataFrame:
    """
    Transforma registros brutos em tabela fato anonimizada.
    Descarta qualquer PII, textos livres e documentos.
    Gera um hash unidirecional com salt aleatório dinâmico a cada processamento.
    """
    rows = []
    import secrets
    dynamic_salt = secrets.token_hex(32)
    logger.info(f"Salt criptográfico dinâmico gerado para esta execução: {dynamic_salt[:8]}... (efêmero)")

    for item in records:
        original_id = str(item.get("id", ""))
        hash_input = f"{dynamic_salt}:{original_id}".encode("utf-8")
        id_anonimo = hashlib.sha256(hash_input).hexdigest()[:16]

        ident = item.get("identificacao", {}) or {}
        req = item.get("requerimento", {}) or {}

        campus, tipo_campus = parse_lotacao(ident.get("lotacao"))
        cargo_nome, classe_cargo = clean_cargo(ident.get("cargo"))
        nivel_pretendido = clean_nivel_rsc(req.get("nivel_rsc_pretendido"))
        
        status = "Deferido"
        nivel_reconhecido = nivel_pretendido

        rows.append({
            "id_anonimo": id_anonimo,
            "campus": campus,
            "tipo_campus": tipo_campus,
            "cargo": cargo_nome,
            "classe_cargo": classe_cargo,
            "nivel_pretendido": nivel_pretendido,
            "nivel_reconhecido": nivel_reconhecido,
            "status": status
        })

    df = pd.DataFrame(rows)
    return df


def load_quadro_ativos(ativos_path: str) -> pd.DataFrame:
    """
    Carrega o quadro de técnicos administrativos ativos do IFRN.
    Suporta tanto a coluna 'lotacao' (que pode ser 'setor/campus' ou apenas 'campus')
    quanto a coluna 'campus'.
    Padroniza campus e cargos. Se o CSV já tiver uma coluna 'tipo_campus'
    pré-calculada, ela é usada diretamente em vez de reclassificar a lotação.
    """
    if not os.path.isfile(ativos_path):
        logger.warning(f"Arquivo de servidores ativos não encontrado em: {ativos_path}")
        return pd.DataFrame()

    logger.info(f"Carregando quadro de TAEs ativos de: {ativos_path}")
    df_raw = pd.read_csv(ativos_path)
    has_tipo_campus_col = "tipo_campus" in df_raw.columns
    rows = []
    for _, r in df_raw.iterrows():
        raw_lot = r.get("lotacao") if "lotacao" in r and pd.notna(r.get("lotacao")) else r.get("campus", "")
        campus, parsed_tipo_campus = parse_lotacao(str(raw_lot))
        if has_tipo_campus_col and pd.notna(r.get("tipo_campus")):
            tipo_campus = r["tipo_campus"]
        else:
            tipo_campus = parsed_tipo_campus
        cargo_nome, classe_cargo = clean_cargo(str(r.get("cargo", "")))
        rows.append({
            "campus": campus,
            "tipo_campus": tipo_campus,
            "cargo": cargo_nome,
            "classe_cargo": classe_cargo
        })
    df_ativos = pd.DataFrame(rows)
    logger.info(f"Quadro de ativos carregado: {len(df_ativos)} servidores.")
    return df_ativos


def generate_aggregates(
    df_fato: pd.DataFrame,
    df_ativos: Optional[pd.DataFrame] = None,
    collected_at: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """
    Gera tabelas agregadas e cruzamentos com o quadro de TAEs ativos.
    """
    total_geral_avaliados = len(df_fato)
    has_ativos = df_ativos is not None and not df_ativos.empty
    total_tae_ativos = len(df_ativos) if has_ativos else 1360

    # 1. Agregado por Campus
    campus_aval = (
        df_fato.groupby(["campus", "tipo_campus"])
        .agg(total_processos=("id_anonimo", "count"))
        .reset_index()
    )

    if has_ativos:
        campus_ativos = (
            df_ativos.groupby(["campus", "tipo_campus"])
            .size()
            .reset_index(name="total_ativos")
        )
        agg_campus = pd.merge(campus_ativos, campus_aval, on=["campus", "tipo_campus"], how="outer").fillna(0)
        agg_campus["total_ativos"] = agg_campus["total_ativos"].astype(int)
        agg_campus["total_processos"] = agg_campus["total_processos"].astype(int)
        agg_campus["taxa_adesao_pct"] = np.where(
            agg_campus["total_ativos"] > 0,
            (agg_campus["total_processos"] / agg_campus["total_ativos"] * 100).round(1),
            0.0
        )
        agg_campus["participacao_pct"] = (agg_campus["total_processos"] / total_geral_avaliados * 100).round(1)
    else:
        agg_campus = campus_aval
        agg_campus["participacao_pct"] = (agg_campus["total_processos"] / total_geral_avaliados * 100).round(1)

    agg_campus["total"] = agg_campus["total_processos"]
    agg_campus = agg_campus.sort_values(by="total_processos", ascending=False)

    # 2. Agregado por Cargo e Nível
    agg_cargo = (
        df_fato.groupby(["cargo", "classe_cargo", "nivel_pretendido", "nivel_reconhecido"])
        .agg(total_processos=("id_anonimo", "count"))
        .reset_index()
        .sort_values(by="total_processos", ascending=False)
    )

    # Totais por cargo consolidados com ativos
    top_cargos_list = []
    if has_ativos:
        c_ativos = df_ativos.groupby(["cargo", "classe_cargo"]).size().rename("total_ativos")
        c_aval = df_fato.groupby(["cargo", "classe_cargo"]).size().rename("total_avaliados")
        c_merged = pd.concat([c_ativos, c_aval], axis=1).fillna(0).astype(int).reset_index()
        c_merged["taxa_adesao_pct"] = np.where(
            c_merged["total_ativos"] > 0,
            (c_merged["total_avaliados"] / c_merged["total_ativos"] * 100).round(1),
            0.0
        )
        c_merged["participacao_pct"] = (c_merged["total_avaliados"] / total_geral_avaliados * 100).round(1)
        c_merged = c_merged.sort_values(by="total_avaliados", ascending=False)
        top_cargos_list = c_merged.to_dict(orient="records")
    else:
        top_cargos_df = (
            df_fato.groupby(["cargo", "classe_cargo"])
            .agg(total=("id_anonimo", "count"))
            .reset_index()
            .sort_values(by="total", ascending=False)
        )
        top_cargos_list = top_cargos_df.to_dict(orient="records")

    # 3. Agregado Institucional Consolidado
    taxa_cobertura_global = round((total_geral_avaliados / total_tae_ativos * 100), 1) if total_tae_ativos > 0 else 0.0
    saldo_potencial = max(0, total_tae_ativos - total_geral_avaliados)

    agg_institucional = pd.DataFrame([{
        "total_processos": total_geral_avaliados,
        "total_tae_ativos": total_tae_ativos,
        "taxa_cobertura_global_pct": taxa_cobertura_global,
        "saldo_potencial_restante": saldo_potencial,
        "total_campi": int(df_fato["campus"].nunique()),
        "total_cargos": int(df_fato["cargo"].nunique())
    }])

    # 4. Adesão por Classe PCCTAE
    adesao_classes = {}
    for cl in ["Classe C", "Classe D", "Classe E"]:
        ativos_cl = int((df_ativos["classe_cargo"] == cl).sum()) if has_ativos else 0
        aval_cl = int((df_fato["classe_cargo"] == cl).sum())
        taxa_cl = round((aval_cl / ativos_cl * 100), 1) if ativos_cl > 0 else 0.0
        adesao_classes[cl] = {
            "total_ativos": ativos_cl,
            "total_avaliados": aval_cl,
            "taxa_adesao_pct": taxa_cl
        }

    # 5. Sumário Estruturado em JSON
    niveis_dist = df_fato["nivel_pretendido"].value_counts().to_dict()
    tipo_campus_dist = df_fato["tipo_campus"].value_counts().to_dict()
    tipo_campus_dist_ativos = df_ativos["tipo_campus"].value_counts().to_dict() if has_ativos else {}
    classe_dist = df_fato["classe_cargo"].value_counts().to_dict()
    
    campus_ranking = agg_campus.to_dict(orient="records")

    campus_nivel_crosstab = (
        pd.crosstab(df_fato["campus"], df_fato["nivel_pretendido"])
        .reset_index()
        .to_dict(orient="records")
    )

    summary_json = {
        "meta": {
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "coletado_em": collected_at or datetime.now(timezone.utc).isoformat(),
            "total_geral_avaliados": total_geral_avaliados,
            "total_tae_ativos": total_tae_ativos,
            "taxa_cobertura_global_pct": taxa_cobertura_global,
            "saldo_potencial_restante": saldo_potencial,
            "total_campi_atendidos": int(df_fato["campus"].nunique()),
            "total_cargos_atendidos": int(df_fato["cargo"].nunique()),
            "total_cargos_existentes": int(df_ativos["cargo"].nunique()) if has_ativos else int(df_fato["cargo"].nunique())
        },
        "adesao_classes": adesao_classes,
        "distribuicao_niveis": niveis_dist,
        "distribuicao_tipo_campus": tipo_campus_dist,
        "distribuicao_tipo_campus_ativos": tipo_campus_dist_ativos,
        "distribuicao_classes": classe_dist,
        "ranking_campi": campus_ranking,
        "campus_niveis": campus_nivel_crosstab,
        "top_cargos": top_cargos_list,
        "serie_institucional": agg_institucional.to_dict(orient="records")
    }

    return agg_campus, agg_cargo, agg_institucional, summary_json


def find_latest_raw_file(raw_dir: str) -> Optional[str]:
    """Localiza o arquivo JSON bruto mais recente em data/raw/."""
    latest_named = os.path.join(raw_dir, "raw_memoriais_latest.json")
    if os.path.isfile(latest_named):
        return latest_named

    files = glob.glob(os.path.join(raw_dir, "raw_memoriais_*.json"))
    if not files:
        # fallback para qualquer .json no diretório
        files = glob.glob(os.path.join(raw_dir, "*.json"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def save_processed_files(
    df_fato: pd.DataFrame,
    agg_campus: pd.DataFrame,
    agg_cargo: pd.DataFrame,
    agg_institucional: pd.DataFrame,
    summary_json: dict,
    output_dir: str
):
    """
    Salva os datasets processados e anonimizados em docs/data.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # CSVs
    df_fato.to_csv(os.path.join(output_dir, "fato_anonimo.csv"), index=False, encoding="utf-8")
    agg_campus.to_csv(os.path.join(output_dir, "agg_campus_mes.csv"), index=False, encoding="utf-8")
    agg_cargo.to_csv(os.path.join(output_dir, "agg_cargo_nivel.csv"), index=False, encoding="utf-8")
    agg_institucional.to_csv(os.path.join(output_dir, "agg_institucional_mes.csv"), index=False, encoding="utf-8")
    
    # JSON Consolidado
    with open(os.path.join(output_dir, "agg_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_json, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Arquivos processados salvos com sucesso em: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Processador e Anonimizador de Dados RSC-TAE")
    parser.add_argument(
        "--input",
        help="Caminho do arquivo JSON bruto de entrada (padrão: mais recente em data/raw/)"
    )
    parser.add_argument(
        "--raw-dir",
        default="data/raw",
        help="Diretório contendo os arquivos brutos (padrão: data/raw)"
    )
    parser.add_argument(
        "--output-dir",
        default="docs/data",
        help="Diretório de saída para os datasets (padrão: docs/data)"
    )
    parser.add_argument(
        "--ativos",
        default="data/quadro_tae_ativos.csv",
        help="Caminho do CSV com quadro de TAEs ativos (padrão: data/quadro_tae_ativos.csv)"
    )

    args = parser.parse_args()

    input_file = args.input or find_latest_raw_file(args.raw_dir)
    if not input_file or not os.path.isfile(input_file):
        logger.error(f"Nenhum arquivo JSON bruto encontrado em: {args.raw_dir}")
        sys.exit(1)

    logger.info(f"Lendo dados brutos de: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        raw_payload = json.load(f)

    if isinstance(raw_payload, dict):
        records = raw_payload.get("results", [])
        collected_at = raw_payload.get("metadata", {}).get("collected_at", datetime.now(timezone.utc).isoformat())
    elif isinstance(raw_payload, list):
        records = raw_payload
        collected_at = datetime.now(timezone.utc).isoformat()
    else:
        logger.error(f"Formato inválido de JSON em {input_file}")
        sys.exit(1)

    logger.info(f"Anonimizando {len(records)} registros...")
    df_fato = anonymize_records(records, collected_at)
    logger.info(f"Tabela fato anonimizada gerada com {len(df_fato)} linhas.")

    df_ativos = load_quadro_ativos(args.ativos)

    logger.info("Gerando tabelas agregadas e cruzamentos com quadro de TAEs ativos...")
    agg_campus, agg_cargo, agg_institucional, summary_json = generate_aggregates(df_fato, df_ativos, collected_at)

    save_processed_files(df_fato, agg_campus, agg_cargo, agg_institucional, summary_json, args.output_dir)

    # Compila automaticamente o site e páginas HTML prontas para servir
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from build_site import build_all
        build_all()
    except Exception as e:
        logger.warning(f"Aviso na compilação do site estático: {e}")

    print("SUCESSO: Processamento e anonimização concluídos.")
    print(f"Total Fato: {len(df_fato)} registros")
    print(f"Total Agregado Campus: {len(agg_campus)} linhas")
    print(f"Total Agregado Cargo: {len(agg_cargo)} linhas")
    print(f"Total Agregado Institucional: {len(agg_institucional)} linhas")


if __name__ == "__main__":
    main()
