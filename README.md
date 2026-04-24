# Laslo — Pauta de Reunião Mensal

Ferramenta de reunião mensal entre Estouro Marketing e Laslo Vet.

**URL:** https://estouromarketing.github.io/Laslo-Reuniao/

---

## Como usar

1. Acesse a URL acima
2. Selecione o mês de referência
3. Preencha posts, ADS, AAR, KPIs e observações
4. Clique em **Salvar reunião** — dados vão para o Google Sheets automaticamente

---

## Adicionar novo mês de KPI (todo mês após receber o relatório Reportei)

### Passo 1 — Adicionar dados no index.html

No arquivo `index.html`, localizar `const KPI_ANALYTICS_DATA = {` e adicionar o novo mês **antes** do primeiro mês existente:

```javascript
'Abr 2026': {
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
git commit -m "feat: adiciona KPIs Abr 2026"
git push origin main
```

### Passo 3 — Atualizar planilha Google Sheets

No Apps Script da planilha (Extensões → Apps Script):
1. Atualizar o array `KPI_MESES` adicionando o novo mês
2. Adicionar o novo mês no objeto `KPI_DATA`
3. Executar `migrarFlat` → atualiza aba **Base de Dados**
4. Executar `migrarPivot` → atualiza aba **Consolidado**

> Rodar as duas funções separadamente (cada uma leva ~30s)

---

## Google Sheets

**Planilha:** Reuniões Laslo 2026

| Aba | Descrição |
|-----|-----------|
| `Resumo` | Log de todos os salvamentos (data, mês, notas) |
| `Abr_2026`, `Mar_2026`... | Dados detalhados de cada reunião |
| `Base de Dados` | Tabela plana: Mês / Categoria / Métrica / Valor (para n8n) |
| `Consolidado` | Pivot: categorias x meses (leitura humana) |

---

## Apps Script

O arquivo `apps-script-laslo.gs` contém o código completo. Para atualizar:

1. Abrir a planilha → **Extensões → Apps Script**
2. Selecionar todo o conteúdo (Ctrl+A)
3. Colar o conteúdo do arquivo `apps-script-laslo.gs`
4. Salvar (Ctrl+S)
5. Reimplantar: **Implantar → Gerenciar implantações → Editar → Nova versão → Implantar**

**URL do Web App (SHEET_URL no index.html):**
```
https://script.google.com/macros/s/AKfycbwcdv-w0OXtUFx8TjgHW27pjfZ5Fh4jra066QUf9EKhlxNflsKpeucD4PN6nLlfzl4n/exec
```

> Se o salvamento parar de funcionar, criar nova implantação e atualizar a SHEET_URL no index.html

### Funções principais do Apps Script

| Função | Descrição |
|--------|-----------|
| `doGet(e)` / `doPost(e)` | Entry points — chamam `rotear(e)` |
| `rotear(e)` | Se `action === 'save_copy'` → `salvarCopy()`; senão → `salvar()` |
| `extrairParams(e)` | Tenta `JSON.parse(postData.contents)`, fallback para `e.parameter` |
| `salvar(e)` | Cria/atualiza aba do mês com estrutura completa |
| `salvarCopy(p)` | Encontra título na col A, salva copy na col E |
| `migrarFlat()` | Popula aba **Base de Dados** (tabela plana) |
| `migrarPivot()` | Popula aba **Consolidado** (pivot por meses) |

---

## n8n — Fluxo de Copy IA

**Webhook:** `https://automacao.estouro.com.br/webhook/laslo-copy`

Fluxo: `Webhook → Extrair Posts → Gerar Copy IA → Edit Fields → Atualizar Post Supabase → HTTP Request (Apps Script)`

| Nó | Função |
|----|--------|
| Webhook | Recebe lista de posts do HTML |
| Extrair Posts | Split item por item |
| Gerar Copy IA | Gera copy para Instagram (output: `$json.output`) |
| Edit Fields | Mapeia `id = $('Extrair Posts').item.json.id` e `conteudo = $json.output` |
| Atualizar Post Supabase | PATCH em `supabase.co/rest/v1/posts?id=eq.{{ $json.id }}` com `status: copy_gerada` |
| HTTP Request (Apps Script) | POST JSON `{action: 'save_copy', titulo, copy_text}` para SHEET_URL |

**Supabase:**
- URL: `https://lrrjybvdxuxgbelfozvr.supabase.co`
- Cliente Laslo: `75c7eef6-aec1-4392-9f97-f6ef06e28936`
- Tabela: `posts` — campos relevantes: `id`, `titulo`, `status`, `copy_text`, `cliente_id`, `data_publicacao`

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
| Pesquisas "laslo" | Nem sempre aparece — usar null se ausente |

---

## Dados históricos disponíveis

| Mês | Status |
|-----|--------|
| Set 2025 | ok |
| Out 2025 | ok |
| Nov 2025 | ok |
| Dez 2025 | ok |
| Jan 2026 | ok |
| Fev 2026 | ok |
| Mar 2026 | ok |
| Abr 2026+ | aguardando relatório |

---

## Histórico de bugs resolvidos

### Sessão 2026-04-23 (parte 1)

| Bug | Causa | Solução |
|-----|-------|---------|
| n8n 404 no HTTP Request | Deployment do Apps Script inválido | Redeploy: Implantar → Gerenciar implantações → Nova versão |
| "Method not allowed" no Supabase | URL do nó apontava pro Apps Script em vez do Supabase | Corrigir URL para `supabase.co/rest/v1/posts` |
| `$json.id` vazio após IA | Nó IA só retorna `output`, não `id` | Adicionar nó "Edit Fields" mapeando `id` e `conteudo` |
| copy_text vazio no Apps Script | Expressão errada (`conteudo` em vez de `output`) | `$('Gerar Copy IA').item.json.output` |
| Posts acumulando no Supabase | Deleta `aguardando_copy` mas reinsere títulos com `copy_gerada` | `sendToN8n()` checa títulos existentes e pula duplicatas |
| Formatação laranja na planilha | `clearContents()` não limpa formatação | Trocar para `aba.clear()` no Apps Script |
| Planilha em branco após "Salvar reunião" | `mode: 'no-cors'` impede leitura do body em `e.parameter` | POST sem `no-cors`, captura CORS error esperado (commit d635ee5) |

### Sessão 2026-04-23 (parte 2)

| Bug | Causa | Solução |
|-----|-------|---------|
| copy_len: 0 no Apps Script | URL do GET excede limite do Google (~2KB) com copy de 800+ chars | Nova ação `save_copy_supabase`: Apps Script busca copy direto no Supabase pelo `id` |
| `$json.id` vazio no Supabase | Gerar Copy IA não passa `id` adiante | Adicionar `id = $('Extrair Posts').item.json.id` no Edit Fields1 |
| UrlFetchApp sem permissão | Deployment antigo não tinha escopo `external_request` | Criar novo deployment (não nova versão) para forçar autorização OAuth |
| Planilha apagada por n8n | HTTP Request sem `action` caía no `salvar()` padrão | Proteção no `rotear()`: só chama `salvar()` se `p.mes` estiver presente |
| SHEET_URL desatualizada | Novo deployment gerou nova URL | Atualizada em `index.html` e `README.md` (commit 72892a5) |

**URL atual do Apps Script:**
```
https://script.google.com/macros/s/AKfycbwcdv-w0OXtUFx8TjgHW27pjfZ5Fh4jra066QUf9EKhlxNflsKpeucD4PN6nLlfzl4n/exec
```

---

## Pendências

- [ ] **Salvar copy na planilha (col E)** — fluxo `save_copy_supabase` implementado mas não confirmado funcionando. Próximo passo: testar com n8n publicado e verificar col E
- [ ] Verificar se planilha não apaga mais dados com a proteção do `rotear()`
- [ ] Re-salvar dados de Abr 2026 na planilha (foram apagados acidentalmente em 2026-04-23)
- [ ] Fluxo n8n atual: Webhook → Extrair Posts → Gerar Copy IA → Edit Fields1 → Atualizar Post Supabase → HTTP Request (save_copy_supabase) → Salvar Histórico

---

## Stack

- HTML/CSS/JS puro (sem framework, sem build)
- Chart.js v4.4.0 (gráficos de KPI)
- Google Apps Script (salvar reunião na planilha)
- GitHub Pages (hospedagem)
