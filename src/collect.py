#!/usr/bin/env python3
"""
Coletor de dados da API pública do SUAP - RSC-TAE (IFRN).
Endpoint: https://suap.ifrn.edu.br/api/rsc_tae/memoriais-avaliados/

Coleta os memoriais avaliados, trata paginação e salva o JSON bruto
com timestamp em data/raw/.
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime, timezone
import urllib.request
import urllib.error

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("rsc_collector")

API_DEFAULT_URL = "https://suap.ifrn.edu.br/api/rsc_tae/memoriais-avaliados/"
USER_AGENT = "rsc-tae-dashboard-collector/1.0 (+https://github.com/kelsoncm/memoriais-avaliados)"


def fetch_page(url: str, timeout: int = 30, max_retries: int = 3) -> dict:
    """
    Realiza requisição HTTP GET para uma página da API do SUAP com retentativas.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Requisitando URL: {url} (tentativa {attempt}/{max_retries})")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status != 200:
                    raise urllib.error.HTTPError(
                        url, response.status, f"HTTP Status {response.status}", response.headers, None
                    )
                raw_data = response.read().decode("utf-8")
                return json.loads(raw_data)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            logger.warning(f"Falha na tentativa {attempt}: {exc}")
            if attempt == max_retries:
                logger.error(f"Número máximo de tentativas atingido para URL: {url}")
                raise
            time.sleep(2 * attempt)
    raise RuntimeError("Falha inesperada ao executar requisição HTTP.")


def collect_all_data(start_url: str = API_DEFAULT_URL) -> dict:
    """
    Coleta todos os registros navegando pela paginação da API.
    Retorna o payload consolidado contendo todos os 'results'.
    """
    all_results = []
    current_url = start_url
    total_count = None
    page_num = 1

    while current_url:
        logger.info(f"Processando página {page_num}...")
        data = fetch_page(current_url)

        if isinstance(data, dict):
            if total_count is None and "count" in data:
                total_count = data["count"]
                logger.info(f"Total de registros informado pela API: {total_count}")

            results = data.get("results", [])
            all_results.extend(results)
            logger.info(f"Página {page_num}: {len(results)} registros obtidos (acumulado: {len(all_results)})")

            current_url = data.get("next")
            page_num += 1
        elif isinstance(data, list):
            # API retornou lista direta
            all_results.extend(data)
            break
        else:
            raise ValueError(f"Formato inesperado de resposta da API: {type(data)}")

    logger.info(f"Coleta concluída com sucesso. Total coletado: {len(all_results)} registros.")

    return {
        "metadata": {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "source_endpoint": start_url,
            "total_count": len(all_results),
            "pages_fetched": page_num - 1
        },
        "count": len(all_results),
        "results": all_results
    }


def save_raw_data(data: dict, output_dir: str) -> str:
    """
    Salva o payload bruto em JSON com timestamp no nome do arquivo
    e atualiza a cópia 'raw_memoriais_latest.json'.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"raw_memoriais_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    latest_path = os.path.join(output_dir, "raw_memoriais_latest.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Arquivo bruto salvo em: {filepath}")

    # Atualiza versão 'latest'
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Arquivo de referência atualizado: {latest_path}")

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Coletor de Memoriais RSC-TAE SUAP/IFRN")
    parser.add_argument(
        "--url",
        default=API_DEFAULT_URL,
        help=f"URL inicial da API (padrão: {API_DEFAULT_URL})"
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Diretório para salvar os arquivos brutos (padrão: data/raw)"
    )
    parser.add_argument(
        "--sample-file",
        help="Caminho para arquivo JSON de amostra local (modo offline/fallback)"
    )

    args = parser.parse_args()

    try:
        if args.sample_file and os.path.isfile(args.sample_file):
            logger.info(f"Usando arquivo de amostra local: {args.sample_file}")
            with open(args.sample_file, "r", encoding="utf-8") as f:
                sample_data = json.load(f)
            
            if isinstance(sample_data, dict) and "results" in sample_data:
                results = sample_data["results"]
            elif isinstance(sample_data, list):
                results = sample_data
            else:
                results = []
            
            data = {
                "metadata": {
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                    "source_endpoint": f"local_file:{args.sample_file}",
                    "total_count": len(results),
                    "pages_fetched": 1
                },
                "count": len(results),
                "results": results
            }
        else:
            data = collect_all_data(start_url=args.url)

        saved_file = save_raw_data(data, args.output_dir)
        print(f"SUCESSO: Coleta finalizada. Arquivo gerado: {saved_file}")
    except Exception as exc:
        logger.exception(f"ERRO CRÍTICO na coleta: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
