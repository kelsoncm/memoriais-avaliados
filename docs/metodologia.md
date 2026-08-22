---
layout: default
title: Metodologia
description: Descrição detalhada das etapas de coleta, processamento, critérios populacionais, agregação e fórmulas estatísticas em HTML puro.
---

<div class="content-container">
  <div class="doc-wrapper">
    <article class="doc-article">
      <h1>Metodologia e Engenharia de Dados</h1>
      
      <p>
        O <strong>RSC-TAE Dashboard</strong> opera através de uma arquitetura modular de pipeline de dados (ETL) automatizada, orientada a dados abertos e à estrita conformidade com normas de governança estatística, transparência ativa e proteção à privacidade.
      </p>

      <h2>1. Fonte dos Dados e Definição da População de Referência</h2>
      <p>
        Os dados primários dos processos de Reconhecimento de Saberes e Competências (RSC) são consumidos diretamente a partir do endpoint público oficial disponibilizado pelo Sistema Unificado de Administração Pública (SUAP) do IFRN:
      </p>
      <pre><code>GET https://suap.ifrn.edu.br/api/rsc_tae/memoriais-avaliados/</code></pre>
      <p>
        Este serviço lista os memoriais descritivos submetidos por servidores e avaliados pelas comissões institucionais designadas. O endpoint é de livre acesso e não exige autenticação para leitura dos registros de interesse público.
      </p>

      <h3>Critérios de Definição do Quadro de Referência (Baseline)</h3>
      <p>
        Para o cálculo das taxas institucionais de adesão e cobertura, foi estabelecido o seguinte protocolo metodológico de identificação e validação da população de servidores técnico-administrativos:
      </p>
      <ul>
        <li>
          <strong>Quantitativo Inicial do SUAP:</strong> O sistema lista originalmente <strong>1.358 servidores técnico-administrativos ativos</strong> cadastrados.
        </li>
        <li>
          <strong>Exclusão de Aposentados:</strong> Deste total, <strong>167 servidores estão aposentados</strong>, restando <strong>1.191 servidores ativos não aposentados</strong> aptos a pleitear o RSC.
        </li>
        <li>
          <strong>Diferenciação dos 3 Tipos de Campus Registrados:</strong> Na base funcional existem 3 campos possíveis para caracterizar a unidade de atuação do servidor:
          <ol>
            <li><em>Campus de lotação no SIAPE</em>;</li>
            <li><em>Campus de exercício no SIAPE</em>;</li>
            <li><em>Campus no SUAP</em>.</li>
          </ol>
        </li>
        <li>
          <strong>Adoção do Campus de Lotação SIAPE:</strong> Como regra geral, o estudo utiliza o <strong>campus de lotação no SIAPE</strong> dos servidores ativos não aposentados.
        </li>
        <li>
          <strong>Tratamento para Servidores sem Campus de Lotação:</strong> Existem <strong>25 servidores ativos não aposentados sem registro de campus de lotação no SIAPE</strong> (em razão de cessões a outros órgãos, convênios ou situações funcionais correlatas). Para estes servidores sem campus de lotação, <strong>consideramos o campus de exercício</strong>, garantindo o enquadramento integral dos <strong>1.191 servidores ativos não aposentados</strong>.
        </li>
        <li>
          <strong>Tratamento e Normalização de Siglas (<code>CAL</code> ➔ <code>CH</code>):</strong> No atributo <code>lotacao</code> retornado no web service do SUAP, o campus Cidade Alta / Centro Histórico aparece por vezes como <code>CH</code> e por vezes como <code>CAL</code> (ex: <code>COETEP/CAL</code>). O pipeline trata essa divergência convertendo sistematicamente o campus <code>CAL</code> (e <code>CCAL</code>) para <code>CH</code>.
        </li>
        <li>
          <strong>Não Utilização de Setor:</strong> O pipeline e as agregações <strong>não utilizam a informação de setor/departamento interno</strong>, mas sim a unidade correspondente ao <strong>campus institucional</strong>.
        </li>
      </ul>

      <h2>2. Territorialidade (Capital vs. Interior)</h2>
      <p>
        Para fins de análise comparativa regional, os campi e unidades do IFRN são categorizados segundo a territorialidade:
      </p>
      <div class="callout info">
        <p><strong>Classificação Territorial Oficial:</strong></p>
        <ul style="margin-bottom: 0;">
          <li>
            <strong>Capital:</strong> Unidades situadas no município de Natal/RN: <code>RE</code> (Reitoria), <code>CNAT</code> (Campus Natal-Central), <code>ZL</code> (Campus Natal-Zona Leste / EaD), <code>CH</code> (Campus Natal-Cidade Alta / Centro Histórico, abrangendo registros <code>CAL</code> e <code>CCAL</code>) e <code>ZN</code> (Campus Natal-Zona Norte).
          </li>
          <li>
            <strong>Interior:</strong> Todas as demais unidades e campi do IFRN no estado do Rio Grande do Norte (<code>AP</code>, <code>CA</code>, <code>CANG</code>, <code>CM</code>, <code>CN</code>, <code>IP</code>, <code>JC</code>, <code>JUC</code>, <code>LAJ</code>, <code>MC</code>, <code>MO</code>, <code>NC</code>, <code>PAAS</code>, <code>PAR</code>, <code>PF</code>, <code>SC</code>, <code>SGA</code>, <code>SPP</code>, etc.).
          </li>
        </ul>
      </div>

      <h2>3. Etapas do Pipeline ETL</h2>
      <div class="callout success">
        <strong>Fluxo Diário Automatizado:</strong> Coleta (02:00 UTC) ➔ Anonimização & Expurgos ➔ Agregação Territorial & Funcional ➔ Validação de Integridade ➔ Publicação no GitHub Pages.
      </div>

      <h3>A. Coleta Automatizada (<code>src/collect.py</code>)</h3>
      <ul>
        <li>Executa requisição HTTP segura ao web service do SUAP com política de 3 retentativas automáticas e backoff exponencial.</li>
        <li>Navega pela paginação da API comparando rigorosamente o total acumulado ao campo <code>count</code> reportado, abortando a execução em caso de inconsistência para preservar o histórico estável.</li>
        <li>Registra o JSON com timestamp em <code>data/raw/raw_memoriais_YYYYMMDD_HHMMSS.json</code>.</li>
      </ul>

      <h3>B. Anonimização e Padronização (<code>src/process.py</code>)</h3>
      <ul>
        <li><strong>Expurgo Total de PII:</strong> Eliminação definitiva de nomes, números SIAPE, e-mails, descrições de portarias/documentos comprobatórios e todo o texto livre (introdução do memorial, requisitos detalhados e conclusões).</li>
        <li><strong>Pseudonimização Criptográfica:</strong> Conversão do identificador de processo em hash <code>SHA-256</code> com salt efêmero institucional, impossibilitando reidentificação externa.</li>
        <li><strong>Padronização de Dimensões:</strong>
          <ul>
            <li><strong>Campus e Territorialidade:</strong> Extração da sigla da unidade a partir do campo <code>lotacao</code>, conversão de <code>CAL</code> para <code>CH</code> e classificação em <em>Capital</em> ou <em>Interior</em>.</li>
            <li><strong>Cargo e Classe:</strong> Normalização textual das denominações de cargo e enquadramento nas respectivas classes do PCCTAE (<em>Classe C</em>, <em>Classe D</em> e <em>Classe E</em>).</li>
          </ul>
        </li>
      </ul>

      <h3>C. Agregação e Cruzamento Estruturado</h3>
      <p>
        Os microdados anonimizados são agregados nas seguintes dimensões públicas:
      </p>
      <ul>
        <li><strong>Por Campus:</strong> Contagem de memoriais avaliados, quantitativo de servidores ativos na unidade (lotação ou exercício para sem lotação), taxa de adesão percentual e participação relativa.</li>
        <li><strong>Por Cargo e Nível:</strong> Volume de processos por carreira do PCCTAE, cruzamento com o total de ativos do cargo e distribuição por nível pretendido e reconhecido (RSC-I a RSC-VI).</li>
        <li><strong>Consolidado Institucional:</strong> Totais globais, taxa de cobertura frente ao quadro de 1.191 ativos não aposentados e saldo potencial de requerimentos restantes.</li>
      </ul>

      <h3>D. Validação e Integridade Matemática (<code>src/validate.py</code>)</h3>
      <p>Antes de qualquer publicação do painel, a suíte de testes automáticos executa checagens mandatórias:</p>
      <ol>
        <li>Ausência absoluta de dados pessoais ou colunas sensíveis em todos os arquivos de saída.</li>
        <li>Coerência matemática dos totais agregados:
          <div style="margin: 0.5rem 0;">
            <span class="formula-inline">&sum; Processos por Campus = &sum; Processos por Cargo = &sum; Processos Institucionais = Total da Tabela Fato</span>
          </div>
        </li>
        <li>Integridade de esquemas, tipos numéricos, limites percentuais (0% a 100%) e consistência dos payloads JSON e tabelas CSV.</li>
      </ol>

      <h2>4. Fórmulas e Métricas Utilizadas</h2>
      <p>
        Abaixo estão descritas as fórmulas matemáticas empregadas em todas as análises do observatório, renderizadas em HTML puro e acessível:
      </p>

      <div class="formula-block">
        <div class="formula-name">1. Taxa de Cobertura Global (%)</div>
        <div class="formula-expr">
          <span class="formula-var">Cobertura Global</span>
          <span class="formula-equal">=</span>
          <span class="formula-op">(</span>
          <div class="formula-fraction">
            <span class="numerator">Total Geral de Memoriais Avaliados</span>
            <span class="denominator">Total de TAEs Ativos Não Aposentados no IFRN (1.191)</span>
          </div>
          <span class="formula-op">)</span>
          <span class="formula-op">&times;</span>
          <span class="formula-var">100</span>
        </div>
      </div>

      <div class="formula-block">
        <div class="formula-name">2. Taxa de Adesão por Campus (%)</div>
        <div class="formula-expr">
          <span class="formula-var">Taxa de Adesão</span>
          <span class="formula-equal">=</span>
          <span class="formula-op">(</span>
          <div class="formula-fraction">
            <span class="numerator">Memoriais Avaliados no Campus</span>
            <span class="denominator">TAEs Ativos Não Aposentados no Campus (Lotação / Exercício)</span>
          </div>
          <span class="formula-op">)</span>
          <span class="formula-op">&times;</span>
          <span class="formula-var">100</span>
        </div>
      </div>

      <div class="formula-block">
        <div class="formula-name">3. Taxa de Adesão por Cargo do PCCTAE (%)</div>
        <div class="formula-expr">
          <span class="formula-var">Taxa de Adesão</span>
          <span class="formula-equal">=</span>
          <span class="formula-op">(</span>
          <div class="formula-fraction">
            <span class="numerator">Memoriais Avaliados no Cargo</span>
            <span class="denominator">TAEs Ativos Não Aposentados no Cargo</span>
          </div>
          <span class="formula-op">)</span>
          <span class="formula-op">&times;</span>
          <span class="formula-var">100</span>
        </div>
      </div>

      <div class="formula-block">
        <div class="formula-name">4. Participação Relativa no Total Institucional (%)</div>
        <div class="formula-expr">
          <span class="formula-var">Participação</span>
          <span class="formula-equal">=</span>
          <span class="formula-op">(</span>
          <div class="formula-fraction">
            <span class="numerator">Total de Memoriais do Grupo (Campus ou Cargo)</span>
            <span class="denominator">Total Geral Institucional de Memoriais Avaliados</span>
          </div>
          <span class="formula-op">)</span>
          <span class="formula-op">&times;</span>
          <span class="formula-var">100</span>
        </div>
      </div>

      <div class="formula-block">
        <div class="formula-name">5. Saldo Potencial Restante de Requerimentos</div>
        <div class="formula-expr">
          <span class="formula-var">Saldo Potencial</span>
          <span class="formula-equal">=</span>
          <span class="formula-var">Total de TAEs Ativos Não Aposentados (1.191)</span>
          <span class="formula-op">&minus;</span>
          <span class="formula-var">Total de Memoriais Avaliados</span>
        </div>
      </div>

    </article>
  </div>
</div>
