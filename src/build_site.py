#!/usr/bin/env python3
"""
Gerador / Compilador Estático do Site e Dashboard (IFRN RSC-TAE).

Renderiza os templates Liquid / Markdown em páginas HTML completas, autônomas e
prontas para serem servidas diretamente por qualquer servidor HTTP (Python,
Jekyll, Nginx ou GitHub Pages) sem depender de Ruby/Jekyll instalado localmente.
"""

import os
import re
import html
from typing import Dict

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
DASHBOARD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard"))

HEADER_HTML = """<header class="site-header">
  <div class="header-container">
    <div class="brand-container">
      <a href="INDEX_LINK" class="brand-logo-link">
        <div class="brand-emblem">
          <span class="emblem-square green"></span>
          <span class="emblem-square red"></span>
        </div>
        <div class="brand-text">
          <span class="brand-title">RSC-TAE Dashboard</span>
          <span class="brand-subtitle">IFRN • Observatório de Saberes & Competências</span>
        </div>
      </a>
    </div>

    <button class="mobile-nav-toggle" id="mobileNavToggle" aria-label="Abrir Menu de Navegação">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>

    <nav class="site-nav" id="siteNav">
      <ul class="nav-list">
        <li class="nav-item">
          <a href="INDEX_LINK" class="nav-link ACTIVE_HOME">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
            Dashboard
          </a>
        </li>
        <li class="nav-item">
          <a href="SOBRE_LINK" class="nav-link ACTIVE_SOBRE">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            Sobre
          </a>
        </li>
        <li class="nav-item">
          <a href="METODOLOGIA_LINK" class="nav-link ACTIVE_METODOLOGIA">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            Metodologia
          </a>
        </li>
        <li class="nav-item">
          <a href="PRIVACIDADE_LINK" class="nav-link ACTIVE_PRIVACIDADE">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            Privacidade
          </a>
        </li>
        <li class="nav-item">
          <a href="DADOS_LINK" class="nav-link ACTIVE_DADOS">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
            Downloads
          </a>
        </li>
        <li class="nav-item">
          <a href="AUTOR_LINK" class="nav-link ACTIVE_AUTOR">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            Autor
          </a>
        </li>
      </ul>
    </nav>
  </div>
</header>"""

FOOTER_HTML = """<footer class="site-footer">
  <div class="footer-container">
    <div class="footer-grid">
      <div class="footer-col brand-col">
        <div class="footer-brand">
          <span class="brand-title">RSC-TAE Dashboard</span>
          <span class="brand-sub">Instituto Federal de Educação, Ciência e Tecnologia do Rio Grande do Norte (IFRN)</span>
        </div>
        <p class="footer-desc">
          Plataforma de transparência e monitoramento analítico agregado dos processos de Reconhecimento de Saberes e Competências (RSC) da carreira TAE, fundamentada no Decreto nº 13.048/2026 e na Lei nº 11.091/2005.
        </p>
      </div>

      <div class="footer-col">
        <h4 class="footer-heading">Transparência & Conformidade</h4>
        <ul class="footer-links">
          <li><a href="PRIVACIDADE_LINK">Compromisso LGPD & Transparência</a></li>
          <li><a href="METODOLOGIA_LINK">Metodologia & Pipeline ETL</a></li>
          <li><a href="DADOS_LINK">Dicionário de Dados & Downloads</a></li>
          <li><a href="https://suap.ifrn.edu.br/api/rsc_tae/memoriais-avaliados/" target="_blank" rel="noopener noreferrer">Endpoint Público SUAP/IFRN ↗</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4 class="footer-heading">Projeto Aberto</h4>
        <ul class="footer-links">
          <li><a href="https://github.com/kelsoncm/memoriais-avaliados" target="_blank" rel="noopener noreferrer">Código no GitHub ↗</a></li>
          <li><a href="https://github.com/kelsoncm/memoriais-avaliados/actions" target="_blank" rel="noopener noreferrer">Atualização Diária (GitHub Actions) ↗</a></li>
          <li><a href="AUTOR_LINK">Sobre o Autor (Kelson Medeiros)</a></li>
          <li><span class="license-badge">Licença MIT • Acesso Aberto</span></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <p>© 2026 Observatório RSC-TAE IFRN • Dados anonimizados e agregados para fins de pesquisa, gestão e controle social.</p>
      <div class="footer-badges">
        <span class="badge-status online">API SUAP Sincronizada</span>
        <span class="badge-status privacy">100% Livre de PII</span>
      </div>
    </div>
  </div>
</footer>"""

BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{TITLE}} | RSC-TAE Dashboard | IFRN</title>
  <meta name="description" content="{{DESCRIPTION}}">
  
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏛️</text></svg>">
  
  <!-- Google Fonts: Inter & Plus Jakarta Sans -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
  
  <!-- Chart.js CDN -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>

  <!-- Main Stylesheet -->
  <link rel="stylesheet" href="{{CSS_PATH}}">
</head>
<body class="site-body">
  {{HEADER}}

  <main class="main-content">
    {{CONTENT}}
  </main>

  {{FOOTER}}

  <script>
    // Toggle Mobile Navigation Menu
    document.addEventListener('DOMContentLoaded', () => {
      const toggle = document.getElementById('mobileNavToggle');
      const nav = document.getElementById('siteNav');
      if (toggle && nav) {
        toggle.addEventListener('click', () => {
          nav.classList.toggle('nav-open');
          toggle.classList.toggle('toggle-active');
        });
      }
    });
  </script>
  {{CUSTOM_JS}}
</body>
</html>"""


def markdown_to_html(md_text: str) -> str:
    """Converte markdown simples para HTML estruturado."""
    # Remove frontmatter
    text = re.sub(r"^---\n.*?\n---\n", "", md_text, flags=re.DOTALL)

    # Processa callouts HTML já existentes ou Markdown
    def replace_code_block(match):
        lang = match.group(1) or ""
        code = html.escape(match.group(2).strip())
        return f'<pre><code class="{lang}">{code}</code></pre>'

    text = re.sub(r"```(\w*)\n(.*?)```", replace_code_block, text, flags=re.DOTALL)

    # Headers
    text = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)

    # Negrito e itálico
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)

    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Links
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)

    # Remove liquid tags
    text = re.sub(r"\{\{.*?\}\}", "", text)
    text = re.sub(r"\{%.*?%\}", "", text)

    # Seções de texto envoltas em parágrafos se não forem tags de bloco
    lines = text.split("\n\n")
    processed_blocks = []
    for block in lines:
        b = block.strip()
        if not b:
            continue
        if b.startswith("<") or b.startswith("|"):
            processed_blocks.append(b)
        else:
            # Lista
            if b.startswith("- ") or b.startswith("* "):
                items = [f"<li>{item.lstrip('-* ')}</li>" for item in b.split("\n") if item.strip()]
                processed_blocks.append(f"<ul>{''.join(items)}</ul>")
            elif re.match(r"^\d+\.", b):
                items = [f"<li>{re.sub(r'^\d+\.\s*', '', item)}</li>" for item in b.split("\n") if item.strip()]
                processed_blocks.append(f"<ol>{''.join(items)}</ol>")
            else:
                processed_blocks.append(f"<p>{b}</p>")

    return "\n\n".join(processed_blocks)


def render_page(
    title: str,
    description: str,
    content_html: str,
    active_nav: str,
    rel_prefix: str = "",
    custom_js: str = ""
) -> str:
    """Renderiza a página HTML completa."""
    css_path = f"{rel_prefix}assets/css/style.css"
    
    header = HEADER_HTML
    header = header.replace("INDEX_LINK", f"{rel_prefix}index.html")
    header = header.replace("SOBRE_LINK", f"{rel_prefix}sobre.html")
    header = header.replace("METODOLOGIA_LINK", f"{rel_prefix}metodologia.html")
    header = header.replace("PRIVACIDADE_LINK", f"{rel_prefix}privacidade.html")
    header = header.replace("DADOS_LINK", f"{rel_prefix}dados.html")
    header = header.replace("AUTOR_LINK", f"{rel_prefix}autor.html")

    header = header.replace("ACTIVE_HOME", "active" if active_nav == "home" else "")
    header = header.replace("ACTIVE_SOBRE", "active" if active_nav == "sobre" else "")
    header = header.replace("ACTIVE_METODOLOGIA", "active" if active_nav == "metodologia" else "")
    header = header.replace("ACTIVE_PRIVACIDADE", "active" if active_nav == "privacidade" else "")
    header = header.replace("ACTIVE_DADOS", "active" if active_nav == "dados" else "")
    header = header.replace("ACTIVE_AUTOR", "active" if active_nav == "autor" else "")

    footer = FOOTER_HTML
    footer = footer.replace("SOBRE_LINK", f"{rel_prefix}sobre.html")
    footer = footer.replace("METODOLOGIA_LINK", f"{rel_prefix}metodologia.html")
    footer = footer.replace("PRIVACIDADE_LINK", f"{rel_prefix}privacidade.html")
    footer = footer.replace("DADOS_LINK", f"{rel_prefix}dados.html")
    footer = footer.replace("AUTOR_LINK", f"{rel_prefix}autor.html")

    html_out = BASE_TEMPLATE
    html_out = html_out.replace("{{TITLE}}", title)
    html_out = html_out.replace("{{DESCRIPTION}}", description)
    html_out = html_out.replace("{{CSS_PATH}}", css_path)
    html_out = html_out.replace("{{HEADER}}", header)
    html_out = html_out.replace("{{CONTENT}}", content_html)
    html_out = html_out.replace("{{FOOTER}}", footer)
    html_out = html_out.replace("{{CUSTOM_JS}}", custom_js)

    return html_out


def build_all():
    print("Compilando site estático em docs/ e dashboard/...")

    # 1. Página Principal (Dashboard)
    index_body_file = os.path.join(DOCS_DIR, "index_body.html")
    if not os.path.isfile(index_body_file):
        # Lê de index.html removendo frontmatter
        with open(os.path.join(DOCS_DIR, "index.html"), "r", encoding="utf-8") as f:
            raw = f.read()
            raw_clean = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.DOTALL)
            raw_clean = raw_clean.replace("{{ '/data/agg_campus_mes.csv' | relative_url }}", "data/agg_campus_mes.csv")
            raw_clean = raw_clean.replace("{{ '/data/agg_cargo_nivel.csv' | relative_url }}", "data/agg_cargo_nivel.csv")
            with open(index_body_file, "w", encoding="utf-8") as bf:
                bf.write(raw_clean)

    with open(index_body_file, "r", encoding="utf-8") as f:
        dashboard_content = f.read()

    js_tag = '<script src="assets/js/dashboard.js"></script>'
    full_index = render_page(
        title="Dashboard Analítico RSC-TAE",
        description="Painel estatístico e anônimo dos processos de RSC dos servidores TAE do IFRN.",
        content_html=dashboard_content,
        active_nav="home",
        rel_prefix="",
        custom_js=js_tag
    )

    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(full_index)
    print("✓ docs/index.html gerado com sucesso.")

    # 2. Standalone Dashboard em dashboard/index.html
    js_tag_dash = '<script src="../docs/assets/js/dashboard.js"></script>'
    dashboard_standalone = render_page(
        title="Dashboard Analítico RSC-TAE",
        description="Painel estatístico e anônimo dos processos de RSC dos servidores TAE do IFRN.",
        content_html=dashboard_content.replace('data/', '../docs/data/'),
        active_nav="home",
        rel_prefix="../docs/",
        custom_js=js_tag_dash
    )
    with open(os.path.join(DASHBOARD_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(dashboard_standalone)
    print("✓ dashboard/index.html gerado com sucesso.")

    # 3. Páginas Informativas (Sobre, Metodologia, Privacidade, Dados, Autor)
    pages = [
        ("sobre.md", "sobre.html", "Sobre o Projeto", "Contexto, objetivos e Decreto nº 13.048/2026", "sobre"),
        ("metodologia.md", "metodologia.html", "Metodologia", "Pipeline ETL, fórmulas estatísticas e agregação", "metodologia"),
        ("privacidade.md", "privacidade.html", "Privacidade e LGPD", "Regras de anonimização, descarte de PII e transparência", "privacidade"),
        ("dados.md", "dados.html", "Dados & Downloads", "Dicionário de dados, schemas e links para download", "dados"),
        ("autor.md", "autor.html", "Sobre o Autor", "Perfil profissional de Kelson da Costa Medeiros, desenvolvedor do RSC-TAE Dashboard", "autor")
    ]

    for md_file, html_file, title, desc, nav_key in pages:
        md_path = os.path.join(DOCS_DIR, md_file)
        if os.path.isfile(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # Extrai o miolo
            body_clean = re.sub(r"^---\n.*?\n---\n", "", md_content, flags=re.DOTALL)
            body_clean = body_clean.replace("{{ '/data/fato_anonimo.csv' | relative_url }}", "data/fato_anonimo.csv")
            body_clean = body_clean.replace("{{ '/data/agg_campus_mes.csv' | relative_url }}", "data/agg_campus_mes.csv")
            body_clean = body_clean.replace("{{ '/data/agg_cargo_nivel.csv' | relative_url }}", "data/agg_cargo_nivel.csv")
            body_clean = body_clean.replace("{{ '/data/agg_summary.json' | relative_url }}", "data/agg_summary.json")

            rendered_html = render_page(
                title=title,
                description=desc,
                content_html=body_clean,
                active_nav=nav_key,
                rel_prefix=""
            )

            out_path = os.path.join(DOCS_DIR, html_file)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(rendered_html)
            print(f"✓ docs/{html_file} gerado com sucesso.")

    print("Compilação concluída com 100% de sucesso!")


if __name__ == "__main__":
    build_all()
