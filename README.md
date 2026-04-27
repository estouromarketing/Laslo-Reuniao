# Laslo — Pauta de Reunião Mensal

Ferramenta de reunião mensal entre Estouro Marketing e Laslo Vet.

**URL:** https://estouromarketing.github.io/Laslo-Reuniao/
**Repo:** https://github.com/estouromarketing/Laslo-Reuniao

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | HTML/CSS/JS puro (sem framework, sem build) + Chart.js v4 |
| Backend planilha | Google Apps Script (`apps-script-laslo.gs`) |
| Banco de dados | Supabase (postgres) — tabela `posts` |
| Automação IA | n8n workflow |
| Hospedagem | GitHub Pages (auto-deploy no push para `main`) |

---

## URLs críticas

| Variável | Valor |
|----------|-------|
| `SHEET_URL` (Apps Script) | `https://script.google.com/macros/s/AKfycbwcdv-w0OXtUFx8TjgHW27pjfZ5Fh4jra066QUf9EKhlxNflsKpeucD4PN6nLlfzl4n/exec` |
| `N8N_WEBHOOK_URL` | `https://automacao.estouro.com.br/webhook/laslo-copy` |
| `SUPABASE_URL` | `https://lrrjybvdxuxgbelfozvr.supabase.co` |
| `LASLO_CLIENT_ID` | `75c7eef6-aec1-4392-9f97-f6ef06e28936` |

> Se o Apps Script for reimplantado, a SHEET_URL muda — atualizar em `index.html` e aqui.

---

## Como usar

1. Acesse a URL acima
2. Selecione o mês de referência
3. Preencha posts, ADS, AAR, KPIs e observações
4. Clique em **Salvar Reunião** → dados vão para o Google Sheets automaticamente
5. Clique em **Gerar Copy IA** → n8n gera copies para cada post
6. Na aba **Copies**: revise, edite e clique **Aprovar** (salva na planilha) ou **Reprovar** (limpa da planilha e regenera)
7. Na aba **Copies**: use o seletor de mês para consultar copies de outros meses sem alterar o mês de referência
8. Clique em **⬇ Exportar Word** para baixar as copies do mês selecionado em formato `.doc`

---

## Fluxo completo

```
[HTML] Salvar Reunião
    → Apps Script: cria/atualiza aba do mês na planilha
    → syncCopiesToSheets(): sincroniza copies aprovadas do Supabase → planilha

[HTML] Gerar Copy IA
    → Supabase: deleta posts aguardando_copy + copy_gerada sem conteudo
    → Supabase: insere posts novos com status aguardando_copy
    → n8n webhook: processa cada post

[n8n] Webhook → Extrair Posts → Gerar Copy IA → Edit Fields1
    → Atualizar Post Supabase: PATCH status=copy_gerada, conteudo=<texto gerado>
    → HTTP Request: POST save_copy → Apps Script grava col E na planilha

[HTML] Aba Copies — Aprovar
    → PATCH Supabase: status=copy_aprovada, conteudo=<texto editado>
    → POST save_copy → Apps Script grava col E com texto final

[HTML] Aba Copies — Reprovar
    → PATCH Supabase: status=aguardando_copy, conteudo=null
    → POST save_copy com copy_text="" → Apps Script limpa col E
```

---

## Google Sheets

**Planilha:** Reuniões Laslo 2026

| Aba | Descrição |
|-----|-----------|
| `Resumo` | Log de todos os salvamentos (data, mês, notas) |
| `Mai_2026`, `Abr_2026`... | Dados detalhados de cada reunião |
| `Base de Dados` | Tabela plana: Mês / Categoria / Métrica / Valor |
| `Consolidado` | Pivot: categorias × meses (leitura humana) |

**Estrutura de cada aba de mês:**

| Linha | Coluna A | Col E |
|-------|----------|-------|
| 1 | Título (header cinza) | PAUTA — MÊS \| Data: XX/XX/XXXX |
| 2 | 1A. POSTS DO MES (laranja) | — |
| 3 | Tema / Conteudo (sub-header) | Copy IA (sub-header) |
| 4+ | Posts do mês | Texto gerado pela IA |
| … | 1B. CAMPANHAS DE ADS | — |
| … | 1C. AÇÕES ESTRATÉGICAS | — |
| … | 2A. KPIs | — |
| … | OBSERVAÇÕES GERAIS | — |

---

## Apps Script

O arquivo `apps-script-laslo.gs` contém o código completo.

**Para atualizar após mudança no arquivo:**
1. Abrir a planilha → **Extensões → Apps Script**
2. Selecionar todo o conteúdo (`Ctrl+A`) e colar o novo arquivo
3. Salvar (`Ctrl+S`)
4. **Implantar → Gerenciar implantações → Editar (lápis) → Nova versão → Implantar**

### Funções principais

| Função | Descrição |
|--------|-----------|
| `doGet(e)` / `doPost(e)` | Entry points — chamam `rotear(e)` |
| `rotear(e)` | `save_copy` → `salvarCopy()`; se `p.mes` presente → `salvar()` |
| `extrairParams(e)` | Tenta `JSON.parse(postData.contents)`, fallback para form-encoded, fallback para `e.parameter` |
| `salvar(e)` | Cria/atualiza aba do mês com estrutura completa (header + seções laranja) |
| `salvarCopy(p)` | Encontra título na col A → grava copy na col E; se não encontrar, insere linha antes de "1B." |
| `migrarFlat()` | Popula aba **Base de Dados** |
| `migrarPivot()` | Popula aba **Consolidado** |

---

## n8n — Workflow Copy IA

**ID:** `wCingzgclv2hQwVq`
**Webhook:** `https://automacao.estouro.com.br/webhook/laslo-copy`

### Configuração dos nós

| Nó | Tipo | Configuração chave |
|----|------|--------------------|
| Webhook | Trigger | POST, path `laslo-copy` |
| Extrair Posts | Split In Batches | processa post a post |
| Gerar Copy IA | AI / LLM | saída em `$json.output` |
| Edit Fields1 | Set | `id = $('Extrair Posts').item.json.id`, `titulo = $('Extrair Posts').item.json.titulo` |
| Atualizar Post Supabase | HTTP Request | PATCH `supabase.co/rest/v1/posts?id=eq.{{ $json.id }}` — body: `status=copy_gerada`, `conteudo={{ $('Gerar Copy IA').item.json.output }}` |
| HTTP Request (save_copy) | HTTP Request | POST JSON para SHEET_URL — body fields: `action=save_copy`, `mes=$('Extrair Posts').item.json.mes`, `titulo=$('Edit Fields1').item.json.titulo`, `copy_text=$('Gerar Copy IA').item.json.output` |
| Salvar Histórico | — | log interno |

> **Atenção no nó "Atualizar Post Supabase":** o campo `conteudo` deve usar `{{ $('Gerar Copy IA').item.json.output }}`, NÃO `$json.conteudo` (que chega vazio).

---

## Supabase — Tabela `posts`

| Campo | Tipo | Uso |
|-------|------|-----|
| `id` | uuid | PK |
| `cliente_id` | uuid | `75c7eef6-aec1-4392-9f97-f6ef06e28936` para Laslo |
| `titulo` | text | Tema do post |
| `plataforma` | text | `Instagram` |
| `ads` | bool | Se é ADS |
| `semana` | int | 1–4 |
| `data_publicacao` | date | Estimada pela semana |
| `status` | text | `aguardando_copy` → `copy_gerada` → `copy_aprovada` |
| `conteudo` | text | Texto gerado pela IA |
| `copy_gerada_em` | timestamp | Quando a IA gerou |

**Ciclo de status:**
```
aguardando_copy → (n8n) → copy_gerada → (HTML: Aprovar) → copy_aprovada
                                       → (HTML: Reprovar) → aguardando_copy
```

---

## Adicionar novo mês de KPI

### Passo 1 — `index.html`

Localizar `const KPI_ANALYTICS_DATA = {` e adicionar o novo mês antes do primeiro existente:

```javascript
'Mai 2026': {
  instagram: {
    'Alcance total (org+pago)': 0000, 'Alcance orgânico': 000, 'Alcance pago': 000,
    'Engajamento total': 000, 'Novos seguidores': 00, 'Seguidores totais': 0000,
    'Visitas do perfil': 000, 'Visualizações totais': 00000,
    'Postagens feed': 0, 'Curtidas em postagens': 00, 'Comentários em postagens': 0,
    'Salvamentos': 0, 'Compartilhamentos': 0, 'Interações totais': 00,
    'Interações nas postagens': 00, 'Alcance das postagens': 000,
    'Número de Reels': 0, 'Alcance dos Reels': 00, 'Interações nos Reels': 0,
    'Curtidas nos Reels': 0, 'Comentários nos Reels': 0, 'Salvamentos nos Reels': 0, 'Compartilhamentos nos Reels': 0,
    'Número de Stories': 0, 'Visualizações dos Stories': 000, 'Interações com Stories': 0,
  },
  metaads: {
    'Valor gasto (R$)': 000.00, 'Impressões': 00000, 'Alcance': 0000,
    'Cliques totais': 000, 'Cliques no link': 000, 'Conversas iniciadas': 00,
    'CTR (%)': 0.00, 'CPC médio (R$)': 0.00, 'CPM médio (R$)': 00.00, 'Frequência': 0.00,
  },
  gmn: {
    'Total de ações': 00, 'Cliques no website': 00, 'Visualizações totais': 000,
    'Ligações': 0, 'Visualizações de pesquisa': 000,
    'Solicitações de rotas': 00, 'Visualizações no Maps': 00, 'Pesquisas "laslo"': 00,
  },
  linkedin: {
    'Seguidores totais': 000, 'Novos seguidores': 0, 'Alcance': 000,
    'Impressões': 000, 'Engajamento': 00, 'Reações': 00, 'Cliques': 0, 'Postagens': 0,
  },
},
```

### Passo 2 — Commit e push

```bash
git add index.html
git commit -m "feat: adiciona KPIs Mai 2026"
git push origin main
```

### Passo 3 — Apps Script (planilha Consolidado)

1. Abrir planilha → **Extensões → Apps Script**
2. Atualizar array `KPI_MESES` com o novo mês
3. Adicionar dados no objeto `KPI_DATA`
4. Executar `migrarFlat` → atualiza **Base de Dados**
5. Executar `migrarPivot` → atualiza **Consolidado**

---

## Mapeamento de métricas (Reportei → KPI_ANALYTICS_DATA)

| Campo no código | Origem no Reportei |
|----------------|--------------------|
| Alcance total (org+pago) | "Alcance total das contas" |
| Alcance orgânico | "Alcance Orgânico dos últimos 30 dias" |
| Alcance pago | "Alcance Pago dos últimos 30 dias" |
| Engajamento total | "Engajamento das postagens" |
| Visualizações totais | "Visualizações totais (orgânicas + pagas)" |
| Visitas do perfil | "Visitas do perfil" |
| Interações totais | "Interações totais" |
| Valor gasto (R$) | Meta Ads — "Valor investido" |
| CTR (%) | Meta Ads — "CTR (Taxa de cliques no link)" |
| CPC médio (R$) | Meta Ads — "CPC médio" |
| CPM médio (R$) | Meta Ads — "CPM médio" |
| Total de ações (GMN) | "Total de ações" |
| Pesquisas "laslo" | Nem sempre aparece — usar `null` se ausente |

---

## Histórico de bugs resolvidos

### Sessão 2026-04-23

| Bug | Causa | Solução |
|-----|-------|---------|
| n8n 404 | Deployment do Apps Script inválido | Redeploy: nova versão |
| "Method not allowed" no Supabase | URL do nó apontava pro Apps Script | Corrigir URL para `supabase.co/rest/v1/posts` |
| `$json.id` vazio após IA | Nó IA só retorna `output` | Adicionar nó "Edit Fields" mapeando `id` |
| copy_text vazio no Apps Script | Expressão errada | `$('Gerar Copy IA').item.json.output` |
| Posts acumulando no Supabase | Re-inserção de títulos já processados | `sendToN8n()` checa títulos existentes |
| Formatação laranja na planilha | `clearContents()` não limpa formatação | Trocar para `aba.clear()` |
| Planilha em branco | `mode: 'no-cors'` impede leitura do body | POST sem `no-cors` |
| Planilha apagada pelo n8n | HTTP Request sem `action` caía em `salvar()` | `rotear()` só chama `salvar()` se `p.mes` presente |

### Sessão 2026-04-27

| Funcionalidade | Descrição |
|---------------|-----------|
| Exportar Word | Botão "⬇ Exportar Word" na aba Copies — gera `.doc` com todas as copies (aprovadas + aguardando) do mês, em formato de parágrafos simples, sem tabelas |
| Seletor de mês nas Copies | Seletor independente no header da aba Copies — sincroniza com o mês de referência ao abrir a aba, mas pode ser alterado livremente sem afetar o restante da ferramenta |

### Sessão 2026-04-24

| Bug | Causa | Solução |
|-----|-------|---------|
| Linha vazia no topo da planilha | `row += 2` criava linha em branco na row 2 | Mudado para `row += 1` |
| Fundo cinza não cobria col E (PAUTA) | Range era `(row,1,1,4)` | Mudado para `(row,1,1,5)` |
| "Copy IA" aparecendo na row 4 (dados) | `salvarCopy` tinha checagem hardcoded em row 4 (era row do sub-header no layout antigo, virou dado no novo) | Removida a checagem — `salvar()` sempre escreve o header |
| 6 copies presas com status `copy_gerada` e `conteudo` nulo | n8n "Atualizar Post Supabase" usava `$json.conteudo` (vazio) | Corrigido para `$('Gerar Copy IA').item.json.output` |
| `copy_gerada` sem conteudo bloqueava regeneração | `sendToN8n()` excluía `copy_gerada` da regeneração | DELETE adicional para `copy_gerada` com `conteudo IS NULL` |
| Aprovar não salvava na planilha imediatamente | `aprovarCopy()` só atualizava Supabase | Adicionado POST `save_copy` ao Apps Script após o PATCH |
| Reprovar não limpava col E imediatamente | `reprovarCopy()` só atualizava Supabase | Adicionado POST `save_copy` com `copy_text=""` após o PATCH |

---

## Dados históricos

| Mês | Status |
|-----|--------|
| Set 2025 | ok |
| Out 2025 | ok |
| Nov 2025 | ok |
| Dez 2025 | ok |
| Jan 2026 | ok |
| Fev 2026 | ok |
| Mar 2026 | ok |
| Abr 2026 | ok |
| Mai 2026 | em andamento |
