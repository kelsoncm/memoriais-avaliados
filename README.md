# 🏛️ RSC-TAE Dashboard | IFRN

[![Atualização Diária e Deploy](https://github.com/kelsoncm/memoriais-avaliados/actions/workflows/daily_update.yml/badge.svg)](https://github.com/kelsoncm/memoriais-avaliados/actions/workflows/daily_update.yml)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![LGPD Compliant](https://img.shields.io/badge/LGPD-100%25%20Anonimizado-success.svg)](#privacidade-e-lgpd)
[![Privacy by Design](https://img.shields.io/badge/Privacy%20by%20Design-Ativa-informational.svg)](#privacidade-e-lgpd)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Plataforma aberta e automatizada para monitoramento, análise estatística e acompanhamento transparente dos processos de **Reconhecimento de Saberes e Competências (RSC)** dos servidores Técnico-Administrativos em Educação (TAE) do **Instituto Federal do Rio Grande do Norte (IFRN)**.

---

## 📌 Visão Geral

O projeto **rsc-tae-dashboard** coleta diariamente os memoriais avaliados pela Comissão de Reconhecimento de Saberes e Competências (CRSC-PCCTAE) do IFRN via API pública do SUAP, realiza o expurgo rigoroso de dados pessoais sensíveis (PII) e publica visualizações agregadas no GitHub Pages com documentação metodológica integrada.

### Fundamentação Legal
- **Decreto Federal nº 13.048/2026:** Regulamenta o Reconhecimento de Saberes e Competências (RSC) para o PCCTAE.
- **Lei Federal nº 11.091/2005:** Plano de Carreira dos Cargos Técnico-Administrativos em Educação (PCCTAE).
- **Lei Federal nº 13.709/2018 (LGPD):** Conformidade com o tratamento de dados públicos e anonimização.
- **Lei Federal nº 12.527/2011 (LAI):** Transparência ativa na administração pública.

---

## 📁 Estrutura do Repositório

```text
memoriais-avaliados/
├── .github/
│   └── workflows/
│       └── daily_update.yml       # Workflow diário no GitHub Actions (02:00 UTC)
├── data/
│   └── raw/                      # JSONs brutos efêmeros coletados da API (ignorados no Git / .gitignore)
├── src/
│   ├── __init__.py
│   ├── build_site.py             # Compilador estático HTML / template renderer
│   ├── collect.py                # Coleta da API do SUAP com retries e paginação
│   ├── process.py                # Pipeline de anonimização, padronização e k-anonimato
│   └── validate.py               # Suíte de validação matemática e de privacidade
├── docs/                         # Portal estático e documentação (Jekyll + Chart.js)
│   ├── _config.yml               # Configuração do Jekyll para o GitHub Pages
│   ├── _layouts/default.html     # Layout responsivo e acessível
│   ├── _includes/                # Cabeçalho e rodapé institucionais
│   ├── assets/
│   │   ├── css/style.css         # Design system com cores institucionais do IFRN
│   │   └── js/dashboard.js       # Gráficos interativos (Chart.js) e filtros reativos
│   ├── data/                     # Datasets anonimizados e agregados (CSVs e JSON)
│   │   ├── fato_anonimo.csv      # Tabela fato com identificador SHA-256 e sem PII
│   │   ├── agg_campus_mes.csv    # Agregado por Campus, tipo e mês (n >= 5)
│   │   ├── agg_cargo_nivel.csv   # Agregado por Cargo, classe e nível (n >= 5)
│   │   ├── agg_institucional_mes.csv # Série histórica institucional
│   │   └── agg_summary.json      # Payload consolidado para visualizações rápidas
│   ├── index.html                # Página principal do Dashboard
│   ├── sobre.html / sobre.md     # Contexto, objetivos e Decreto nº 13.048/2026
│   ├── metodologia.html / .md    # Pipeline ETL, fórmulas e regras de agregação
│   ├── privacidade.html / .md    # Conformidade LGPD, campos expurgados e k-anonimato
│   └── dados.html / dados.md     # Dicionário de dados, schemas e links de download
├── dashboard/                    # Acesso direto e independente ao dashboard
│   └── index.html
├── requirements.txt              # Dependências Python (requests, pandas)
├── LICENSE                       # Licença MIT
└── README.md                     # Documentação principal
```

---

## 🔒 Privacidade e Conformidade LGPD

O pipeline de dados opera sob o princípio de **Privacy by Design**:

1. **Expurgo Total de Dados Identificadores:** Nomes (`identificacao.nome`), SIAPEs (`identificacao.siape`), e-mails e IDs originais são eliminados na extração.
2. **Eliminação de Textos Livres:** Introduções de memoriais, relatórios narrativos de requisitos, textos de conclusão e descrições individuais de documentos comprobatórios não são armazenados.
3. **Pseudonimização Criptográfica:** Cada processo recebe um hash unidirecional `SHA-256` com salt institucional exclusivo para contagem estatística não-reversível.
4. **Metadados Institucionais Públicos:** Apenas atributos administrativos públicos (Campus, Cargo no PCCTAE, Nível RSC e Situação da Avaliação) são publicados, garantindo total transparência e fidelidade institucional.

---

## 🚀 Como Executar Localmente

### 1. Pré-requisitos
- Python 3.10+ (recomendado 3.12)
- Git

### 2. Clonar o Repositório e Configurar o Ambiente

```bash
git clone https://github.com/kelsoncm/memoriais-avaliados.git
cd memoriais-avaliados

# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Executar o Pipeline ETL

```bash
# 1. Coleta da API do SUAP (ou use --sample-file caminho.json para teste offline)
python src/collect.py

# 2. Processamento, anonimização e geração de agregados
python src/process.py

# 3. Validação de integridade e privacidade
python src/validate.py
```

### 4. Visualizar o Dashboard Localmente

Você pode iniciar um servidor HTTP simples na pasta `docs/` ou na raiz:

```bash
# Opção A: Servir a documentação e dashboard via Python
python3 -m http.server 8000 --directory docs

# Acesse no navegador:
# http://localhost:8000
```

Se tiver Ruby e Jekyll instalados:
```bash
cd docs
bundle install
bundle exec jekyll serve
```

---

## ⚙️ Configuração no GitHub Pages

Para ativar a publicação automática do dashboard no repositório GitHub:

1. Acesse o repositório no GitHub: **Settings > Pages**.
2. Em **Build and deployment > Source**, selecione:
   - **GitHub Actions** (recomendado para usar o workflow `.github/workflows/daily_update.yml`).
3. O workflow diário executará automaticamente:
   - Coleta diária às 02:00 UTC.
   - Anonimização e validação.
   - Commit dos novos dados versionados em `/data`.
   - Deploy do site no GitHub Pages.

---

## 📊 Schemas dos Datasets Gerados

| Arquivo | Descrição | Principais Campos |
| :--- | :--- | :--- |
| `fato_anonimo.csv` | Microdados anonimizados | `id_anonimo`, `campus`, `tipo_campus`, `cargo`, `classe_cargo`, `nivel_pretendido`, `nivel_reconhecido`, `status`, `tempo_tramitacao_dias` |
| `agg_campus_mes.csv` | Agrupado por Campus e Mês | `campus`, `tipo_campus`, `ano`, `mes`, `total_processos`, `total_deferidos`, `taxa_deferimento`, `tempo_medio_tramitacao` |
| `agg_cargo_nivel.csv` | Agrupado por Cargo e Nível | `cargo`, `classe_cargo`, `nivel_pretendido`, `total_processos`, `total_deferidos`, `taxa_deferimento` |
| `agg_institucional_mes.csv` | Série Histórica Institucional | `ano`, `mes`, `total_submetidos`, `total_concluidos`, `total_deferidos`, `taxa_deferimento` |
| `agg_summary.json` | Consolidado para o Dashboard | Metadados, rankings de campi, distribuição de níveis, classes e séries |

---

## 🤝 Como Contribuir

Contribuições com novas análises, aprimoramentos nos gráficos e sugestões de governança de dados são muito bem-vindas!

1. Faça um Fork do projeto (`git checkout -b feature/novo-grafico`).
2. Faça o Commit das alterações (`git commit -m 'feat: adiciona gráfico de evolução temporal'`).
3. Faça o Push para a branch (`git push origin feature/novo-grafico`).
4. Abra um **Pull Request**.

---

## 📄 Licença

Este projeto é distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---
**Observatório RSC-TAE IFRN** • *Ciência de Dados em Defesa da Educação Pública e da Transparência.*
