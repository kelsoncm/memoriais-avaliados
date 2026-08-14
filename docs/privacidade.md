---
layout: default
title: Privacidade e LGPD
description: Regras de anonimização, descarte de dados pessoais sensíveis, conformidade com a LGPD e k-anonimato.
---

<div class="content-container">
  <div class="doc-wrapper">
    <article class="doc-article">
      <h1>Privacidade, Ética e Conformidade LGPD</h1>

      <div class="callout success">
        <strong>Compromisso Institucional:</strong> O RSC-TAE Dashboard é estritamente aderente à <strong>Lei Geral de Proteção de Dados Pessoais (Lei Federal nº 13.709/2018 - LGPD)</strong>, às diretrizes de Governança de Dados Públicos e às melhores práticas internacionais de <em>Privacy by Design</em>.
      </div>

      <h2>1. Dados Efetivamente Descartados</h2>
      <p>
        O script de processamento e anonimização (<code>src/process.py</code>) atua como barreira estrita e descarta irreversivelmente todos os campos diretos ou indiretamente identificáveis contidos na resposta original da API do SUAP:
      </p>

      <table class="data-table" style="margin-bottom: 1.5rem;">
        <thead>
          <tr>
            <th>Campo Original da API</th>
            <th>Tratamento Aplicado</th>
            <th>Justificativa de Privacidade</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>identificacao.nome</code></td>
            <td><span class="badge slate">Descarte Total</span></td>
            <td>Identificador direto do servidor público.</td>
          </tr>
          <tr>
            <td><code>identificacao.siape</code></td>
            <td><span class="badge slate">Descarte Total</span></td>
            <td>Matrícula funcional única do Poder Executivo Federal.</td>
          </tr>
          <tr>
            <td><code>id</code> do processo original</td>
            <td><span class="badge amber">Hash SHA-256</span></td>
            <td>Substituído por hash unidirecional (sem chave reversível).</td>
          </tr>
          <tr>
            <td><code>processo_anterior_id</code></td>
            <td><span class="badge slate">Descarte Total</span></td>
            <td>Elimina possibilidade de encadeamento histórico externo.</td>
          </tr>
          <tr>
            <td><code>memorial.introducao</code></td>
            <td><span class="badge slate">Descarte Total</span></td>
            <td>Texto livre autobiográfico com potencial de reidentificação.</td>
          </tr>
          <tr>
            <td><code>memorial.requisitos</code></td>
            <td><span class="badge slate">Descarte Total</span></td>
            <td>Descrições narrativas de projetos e comissões do servidor.</td>
          </tr>
          <tr>
            <td><code>conclusao.texto</code> / <code>resumo</code></td>
            <td><span class="badge slate">Descarte Total</span></td>
            <td>Textos narrativos do autor do memorial.</td>
          </tr>
          <tr>
            <td><code>documentos[].descricao</code></td>
            <td><span class="badge slate">Descarte Total</span></td>
            <td>Descrições de portarias, certificados e diplomas pessoais.</td>
          </tr>
        </tbody>
      </table>

      <h2>2. Princípio da Privacidade por Design (Privacy by Design)</h2>
      <p>
        A proteção à privacidade neste projeto não depende de supressão ou distorção estatística de pequenas contagens, mas sim da <strong>completa descaracterização e eliminação de todos os dados pessoais identificáveis na origem</strong>:
      </p>
      <ul>
        <li><strong>Sem Identificadores Pessoais:</strong> Nomes, matrículas SIAPE, CPFs, e-mails e contatos são eliminados antes de qualquer agregação.</li>
        <li><strong>Sem Textos Livres ou Comprovações:</strong> Narrativas autobiográficas, portarias individuais e relatórios de atividades não são armazenados.</li>
        <li><strong>Metadados Puramente Institucionais:</strong> Os dados publicados contêm exclusivamente atributos públicos da estrutura do IFRN (Campus de lotação, cargo da carreira PCCTAE, nível de RSC pleiteado e deferido).</li>
      </ul>

      <h2>3. Transparência Plena e Não-Reidentificação</h2>
      <p>
        Como os memoriais avaliados constituem atos administrativos formais já de domínio e publicidade legal no IFRN (Art. 37 da Constituição Federal e Lei de Acesso à Informação), a publicação agregada por campus e cargo reflete fielmente a totalidade das concessões institucionais, permitindo a verificação exata por parte do sindicato, comissões de acompanhamento e pesquisadores.
      </p>
      <p>
        Não há armazenamento de notas, pontuações individuais por requisito, pareceres avaliativos ou qualquer atributo privado que possa violar a intimidade ou a vida privada de servidores.
      </p>

      <h2>4. Legislação de Referência</h2>
      <ul>
        <li><strong>Lei nº 13.709/2018 (LGPD):</strong> Art. 12 (dados anonimizados não são considerados dados pessoais para os fins da lei).</li>
        <li><strong>Lei nº 12.527/2011 (LAI):</strong> Transparência ativa na administração pública federal.</li>
        <li><strong>Decreto nº 13.048/2026:</strong> Regulamentação do RSC no âmbito das Instituições Federais de Ensino.</li>
      </ul>
    </article>
  </div>
</div>
