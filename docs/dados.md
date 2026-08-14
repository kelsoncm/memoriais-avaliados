---
layout: default
title: Dados & Downloads
description: Dicionário de dados, schemas das tabelas fato e agregadas, links para download em CSV e JSON e limitações.
---

<div class="content-container">
  <div class="doc-wrapper">
    <article class="doc-article">
      <h1>Catálogo de Dados e Dicionário de Schemas</h1>

      <p>
        Todos os datasets gerados pelo pipeline são disponibilizados publicamente em formatos abertos (CSV e JSON), estruturados para consumo direto por ferramentas analíticas (Python, R, PowerBI, Excel) e pesquisadores.
      </p>

      <h2>1. Arquivos Disponíveis para Download</h2>

      <div class="kpi-grid" style="margin-top: 1.5rem;">
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Tabela Fato Anonimizada</span>
            <span class="badge slate">CSV</span>
          </div>
          <p style="font-size: 0.85rem; color: var(--slate-600); margin-bottom: 1rem;">
            Tabela de nível microdado individual, completamente desprovida de dados pessoais identificadores.
          </p>
          <a href="{{ '/data/fato_anonimo.csv' | relative_url }}" class="btn-download" download>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            Download fato_anonimo.csv
          </a>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Agregado Campus / Mês</span>
            <span class="badge green">CSV</span>
          </div>
          <p style="font-size: 0.85rem; color: var(--slate-600); margin-bottom: 1rem;">
            Contagens de processos, deferimentos e taxas agrupados por Campus, territorialidade e período.
          </p>
          <a href="{{ '/data/agg_campus_mes.csv' | relative_url }}" class="btn-download" download>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            Download agg_campus_mes.csv
          </a>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Agregado Cargo / Nível</span>
            <span class="badge blue">CSV</span>
          </div>
          <p style="font-size: 0.85rem; color: var(--slate-600); margin-bottom: 1rem;">
            Distribuição por cargo da carreira PCCTAE, classe funcional e nível de RSC pretendido e deferido.
          </p>
          <a href="{{ '/data/agg_cargo_nivel.csv' | relative_url }}" class="btn-download" download>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            Download agg_cargo_nivel.csv
          </a>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-label">Consolidado Institucional</span>
            <span class="badge amber">JSON</span>
          </div>
          <p style="font-size: 0.85rem; color: var(--slate-600); margin-bottom: 1rem;">
            Payload consolidado em JSON contendo metadados, rankings e distribuições estatísticas.
          </p>
          <a href="{{ '/data/agg_summary.json' | relative_url }}" class="btn-download" download>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            Download agg_summary.json
          </a>
        </div>
      </div>

      <h2>2. Schemas Detalhados dos Datasets</h2>

      <h3>A. <code>fato_anonimo.csv</code></h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>Coluna</th>
            <th>Tipo</th>
            <th>Descrição</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>id_anonimo</code></td>
            <td>String (Hex 16)</td>
            <td>Identificador pseudonimizado derivado de hash SHA-256 irreversível com salt.</td>
          </tr>
          <tr>
            <td><code>campus</code></td>
            <td>String</td>
            <td>Nome padronizado do Campus ou Reitoria do IFRN.</td>
          </tr>
          <tr>
            <td><code>tipo_campus</code></td>
            <td>String</td>
            <td>Categoria territorial (<em>Capital</em>, <em>Interior</em>, <em>Reitoria</em>).</td>
          </tr>
          <tr>
            <td><code>cargo</code></td>
            <td>String</td>
            <td>Denominação normalizada do cargo do servidor no PCCTAE.</td>
          </tr>
          <tr>
            <td><code>classe_cargo</code></td>
            <td>String</td>
            <td>Nível de classificação funcional (<em>Classe C</em>, <em>Classe D</em>, <em>Classe E</em>).</td>
          </tr>
          <tr>
            <td><code>nivel_pretendido</code></td>
            <td>String</td>
            <td>Nível de RSC pleiteado (<em>RSC-I</em> a <em>RSC-VI</em>).</td>
          </tr>
          <tr>
            <td><code>nivel_reconhecido</code></td>
            <td>String</td>
            <td>Nível de RSC reconhecido e concedido.</td>
          </tr>
          <tr>
            <td><code>status</code></td>
            <td>String</td>
            <td>Situação da avaliação (Deferido).</td>
          </tr>
        </tbody>
      </table>

      <h3>B. <code>agg_campus_mes.csv</code></h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>Coluna</th>
            <th>Tipo</th>
            <th>Descrição</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>campus</code></td>
            <td>String</td>
            <td>Nome oficial do Campus ou Reitoria.</td>
          </tr>
          <tr>
            <td><code>tipo_campus</code></td>
            <td>String</td>
            <td>Classificação territorial da unidade (Capital, Interior, Reitoria).</td>
          </tr>
          <tr>
            <td><code>total_ativos</code></td>
            <td>Integer</td>
            <td>Total de servidores técnico-administrativos ativos lotados na unidade.</td>
          </tr>
          <tr>
            <td><code>total_processos</code></td>
            <td>Integer</td>
            <td>Número total de processos de memoriais avaliados no campus.</td>
          </tr>
          <tr>
            <td><code>taxa_adesao_pct</code></td>
            <td>Float</td>
            <td>Percentual de adesão: (total_processos / total_ativos) * 100.</td>
          </tr>
          <tr>
            <td><code>participacao_pct</code></td>
            <td>Float</td>
            <td>Participação percentual do campus no total institucional de memoriais.</td>
          </tr>
        </tbody>
      </table>

      <h3>C. <code>agg_cargo_nivel.csv</code></h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>Coluna</th>
            <th>Tipo</th>
            <th>Descrição</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>cargo</code></td>
            <td>String</td>
            <td>Denominação do cargo na carreira PCCTAE.</td>
          </tr>
          <tr>
            <td><code>classe_cargo</code></td>
            <td>String</td>
            <td>Classe funcional no plano de carreira (Classe C, D ou E).</td>
          </tr>
          <tr>
            <td><code>nivel_pretendido</code></td>
            <td>String</td>
            <td>Nível de RSC pleiteado no requerimento.</td>
          </tr>
          <tr>
            <td><code>nivel_reconhecido</code></td>
            <td>String</td>
            <td>Nível de RSC outorgado e publicado.</td>
          </tr>
          <tr>
            <td><code>total_processos</code></td>
            <td>Integer</td>
            <td>Total de memoriais avaliados para o cargo/nível.</td>
          </tr>
        </tbody>
      </table>

      <h3>D. <code>quadro_tae_ativos.csv</code> (Referência Baseline)</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>Coluna</th>
            <th>Tipo</th>
            <th>Descrição</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>id_anonimo</code></td>
            <td>Integer</td>
            <td>Identificador anônimo sequencial do servidor ativo.</td>
          </tr>
          <tr>
            <td><code>cargo</code></td>
            <td>String</td>
            <td>Denominação e código do cargo extraído do SUAP.</td>
          </tr>
          <tr>
            <td><code>campus</code></td>
            <td>String</td>
            <td>Sigla da unidade/campus de lotação.</td>
          </tr>
        </tbody>
      </table>

      <h2>3. Limitações e Ressalvas Técnicas</h2>
      <ul>
        <li>
          <strong>Dependência do Endpoint SUAP:</strong> O pipeline consome o endpoint oficial <code>/api/rsc_tae/memoriais-avaliados/</code>. Caso o SUAP passe por instabilidades temporárias ou alterações de schema, o workflow retém o último estado consistente de dados válidos.
        </li>
        <li>
          <strong>Cadência de Atualização:</strong> As coletas ocorrem diariamente às 02:00 UTC via GitHub Actions. Novos memoriais publicados no SUAP são incorporados na execução subsequente.
        </li>
        <li>
          <strong>Transparência Ativa:</strong> Os datasets refletem a totalidade dos memoriais publicados oficialmente pela instituição, sem omissões ou supressões artificiais.
        </li>
      </ul>
    </article>
  </div>
</div>
