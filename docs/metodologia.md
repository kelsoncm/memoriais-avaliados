---
layout: default
title: Metodologia
description: Descrição detalhada das etapas de coleta, processamento, agregação e fórmulas estatísticas utilizadas.
---

<div class="content-container">
  <div class="doc-wrapper">
    <article class="doc-article">
      <h1>Metodologia e Engenharia de Dados</h1>
      
      <p>
        O <strong>RSC-TAE Dashboard</strong> opera através de uma arquitetura modular de pipeline de dados (ETL) automatizada, orientada a dados abertos e à estrita conformidade com normas de privacidade e governança estatística.
      </p>

      <h2>1. Fonte e Origem dos Dados</h2>
      <p>
        Os dados são consumidos a partir do endpoint público disponibilizado pelo Sistema Unificado de Administração Pública (SUAP) do IFRN:
      </p>
      <pre><code>GET https://suap.ifrn.edu.br/api/rsc_tae/memoriais-avaliados/</code></pre>
      <p>
        Este endpoint lista os memoriais que passaram pela comissão de avaliação institucional. A API é pública e não exige token de autenticação para leitura de processos avaliados.
      </p>

      <h2>2. Etapas do Pipeline ETL</h2>
      <div class="callout info">
        <strong>Fluxo Diário:</strong> Coleta (02:00 UTC) ➔ Anonimização & Expurgos ➔ Agregação & K-Anonimato ➔ Validação de Integridade ➔ Deploy no GitHub Pages.
      </div>

      <h3>A. Coleta (<code>src/collect.py</code>)</h3>
      <ul>
        <li>Realiza requisição HTTP com cabeçalhos padrão e mecanismo de retentativas automáticas (3 tentativas com backoff exponencial).</li>
        <li>Itera pela paginação (caso o campo <code>next</code> esteja presente) até obter o conjunto integral de registros.</li>
        <li>Registra o JSON com timestamp em <code>data/raw/raw_memoriais_YYYYMMDD_HHMMSS.json</code>.</li>
      </ul>

      <h3>B. Anonimização e Filtragem (<code>src/process.py</code>)</h3>
      <ul>
        <li><strong>Expurgo Total de PII:</strong> São imediatamente descartados nomes, números SIAPE, e-mails, descrições detalhadas de documentos comprobatórios e todo o texto livre (introdução do memorial, relatórios de requisitos e textos de conclusão).</li>
        <li><strong>Pseudonimização Unidirecional:</strong> O ID do processo original é convertido em um hash criptográfico <code>SHA-256</code> com salt institucional, impossibilitando a correlação externa, mas permitindo contagens estatísticas unívocas internas.</li>
        <li><strong>Padronização de Entidades:</strong>
          <ul>
            <li><strong>Campus e Tipo:</strong> A sigla do setor de lotação (ex: <code>COTIC/CA</code> ➔ <code>CA</code>) é convertida para o Campus padronizado (ex: <em>Caicó</em>) e classificada por territorialidade (<em>Capital</em>, <em>Interior</em> ou <em>Reitoria</em>).</li>
            <li><strong>Cargo e Classe:</strong> Os cargos são limpos e mapeados para a respectiva classe do PCCTAE (<em>Classe C</em>, <em>Classe D</em> ou <em>Classe E</em>).</li>
          </ul>
        </li>
      </ul>

      <h3>C. Agregação e Estruturação de Métricas</h3>
      <p>
        O pipeline consolida os registros anonimizados em três dimensões essenciais para acompanhamento social:
      </p>
      <ul>
        <li><strong>Por Campus e Mês:</strong> Contagem de processos, taxas e tempo de tramitação por unidade de lotação.</li>
        <li><strong>Por Cargo e Nível:</strong> Mapeamento da adesão e reconhecimento entre as diferentes carreiras do PCCTAE e níveis RSC.</li>
        <li><strong>Série Institucional:</strong> Acompanhamento temporal consolidado do IFRN.</li>
      </ul>

      <h3>D. Validação de Consistência (<code>src/validate.py</code>)</h3>
      <p>Antes de qualquer publicação, a suíte de testes automáticos checa:</p>
      <ol>
        <li>Ausência total de colunas ou dados pessoais identificáveis em todas as tabelas de saída.</li>
        <li>Coerência matemática ($\sum \text{processos por campus} = \sum \text{processos por cargo} = \sum \text{processos institucionais} = \text{total da tabela fato}$).</li>
        <li>Validade das taxas percentuais ($0 \le \text{taxa} \le 100$).</li>
        <li>Integridade de esquemas e formatos CSV/JSON.</li>
      </ol>

      <h2>3. Fórmulas e Métricas Utilizadas</h2>
      <ul>
        <li>
          <strong>Taxa de Deferimento (%):</strong>
          $$\text{Taxa} = \left( \frac{\text{Total Deferidos}}{\text{Total Concluídos}} \right) \times 100$$
        </li>
        <li>
          <strong>Tempo Médio de Tramitação (dias):</strong> Média aritmética simples calculada entre o início do requerimento e a data de publicação do memorial avaliado.
        </li>
        <li>
          <strong>Tempo Mediano de Tramitação (dias):</strong> Valor central da distribuição temporal de tramitação, imune a valores atípicos (outliers).
        </li>
      </ul>
    </article>
  </div>
</div>
