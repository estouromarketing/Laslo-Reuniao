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
https://script.google.com/macros/s/AKfycbwQUEdrLThoqA6FVdh-2ZQ9vFU10AA9-L4w8puv5eMn29rZ8vrtEtlTGbnrTRKy3NhC/exec
```

> Se o salvamento parar de funcionar, criar nova implantação e atualizar a SHEET_URL no index.html

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

## Stack

- HTML/CSS/JS puro (sem framework, sem build)
- Chart.js v4.4.0 (gráficos de KPI)
- Google Apps Script (salvar reunião na planilha)
- GitHub Pages (hospedagem)
