# Plano de migração: Reunião Laslo (standalone) → estouro-app

**Objetivo:** levar a ferramenta de reunião do standalone público (GitHub Pages, com a chave Supabase exposta e sem login) para a versão autenticada dentro do estouro-app (`/cliente/[id]/reuniao`), aposentando o standalone. Resolve a segurança de raiz (auth real) e elimina a duplicação de dados.

## Situação atual (24/06/2026)

| Recurso | Standalone (público) | estouro-app (autenticado) |
|---|---|---|
| Pauta, Gráficos, Diagnóstico, KPIs | ✅ | ✅ |
| Copies (aprovar/reprovar) | ✅ | ❌ |
| Webinars (7 HTMLs) | ✅ | ❌ |
| Brief de Arte | ✅ | ❌ |
| Importar correções | ✅ | ❌ |
| Escritas no banco (n8n, PATCH) | ✅ | ❌ |
| Exportar PDF / .doc | ✅ | print page existe |

O estouro-app é hoje uma versão de **visualização**; o standalone é a ferramenta de trabalho completa, e é onde estão as escritas (o risco de segurança).

## O que portar para o estouro-app

1. **Copies** — aba de aprovação/reprovação de copies (PATCH em `posts`). No estouro-app vira ação server-side (rota API com service_role), sem expor escrita no cliente.
2. **Webinars** — aba com os 7 HTMLs (já versionados em `webinars/`).
3. **Brief de Arte** — modal de geração de brief.
4. **Importar correções** — upload/parse e PATCH.
5. **Escritas via n8n** — manter o disparo, mas a partir de rota autenticada.
6. **KPIs lendo direto do Supabase** — eliminar o `KPI_ANALYTICS_DATA` hardcoded; a página passa a ler `relatorios.dados_completos`. Acaba a duplicação e o passo de colar bloco no HTML (o `sync_kpi.py` deixa de ser necessário).
7. **Pauta/Datas do Supabase** — idealmente `POSTS_DATA`/`DATES_DATA` viram tabelas/JSON no Supabase em vez de hardcoded (`gen_pauta.py` deixa de ser necessário).

## Ganhos
- **Segurança:** login real; escritas server-side; anon key deixa de ter poder de escrita exposto.
- **Fonte única:** Supabase é a verdade; sem editar HTML/CSV todo mês.
- **Dados ricos:** aproveitar `Leads`, `Custo por lead`, breakdown FB/IG e demais campos que o Supabase já guarda.

## Cuidados
- Garantir paridade de UX antes de desligar o standalone (Ale usa na reunião com o cliente).
- Migrar/validar os webinars e a pauta editorial sem perder conteúdo.
- Depois de migrado e validado: despublicar o GitHub Pages e arquivar o repo standalone.

## Status
Decidido em 24/06/2026 deixar a migração como projeto à parte (sem data). Até lá, o standalone segue em uso com os scripts `sync_kpi.py` e `gen_pauta.py` facilitando a manutenção mensal.
