# AGENDA EDITORIAL LASLO — regras permanentes

> Fonte de verdade das regras de planejamento de conteúdo da Laslo Vet.
> A agenda em si vive em **`agenda.json`** (lida pela aba 📅 Calendário e pela Pauta).
> Criado em 07/07/2026 a pedido do Ale ("um agente que sempre tenha essas informações, para não haver falha").

## Contrato

- **2 posts de feed por semana** no Instagram (contrato mensal)
- Stories de campanha de live e reels de cortes são **bônus, fora do contrato**
- **Nunca deixar slot vazio** ("post a definir" é proibido — sempre há produto, data ou live pra ocupar)

## Portfólio (o que alimenta o loop de produtos)

| Categoria | Itens |
|---|---|
| Bombas de infusão | ICAVet, ICAVet S, BS680 VET (seringa/TIVA), BSVET TCI (alvo-controlada), BVVET (volumétrica), ELASTOvet (elastomérica) |
| Equipamentos | Pedestal Roama |
| Insumos | Seringas Serisam (20/60ml), equipos (fotoprotetor e cristal), extensores |
| Modalidades de aquisição | **Clube Laslo (prioridade máxima)**, locação/comodato, venda (**por último, com moderação — "vendas não é tão saudável para a Laslo"**) |
| Institucional | DNA VET, 20 anos, valores, equipe — **1 post/mês** |

## Loop de produtos (regra de rotação)

Cada produto volta ao feed em ciclos, **sempre com um ângulo diferente** (nunca repetir o mesmo ângulo em ciclos consecutivos):

1. **Problema clínico** que o produto resolve
2. **Recurso técnico** / diferencial
3. **Caso de uso** / rotina real da clínica
4. **Mito vs verdade** / FAQ
5. **Como adquirir** (Clube / locação / venda)

## Sinergia com as lives (calendário oficial VetsPro — terças 20h)

| Data | Live | Produto |
|---|---|---|
| 30/06 ✅ | ICAVET | icavet |
| 21/07 | Descartáveis (alarme de oclusão) | insumos |
| 25/08 | BS680 | bs680 |
| 29/09 | ELASTOvet | elastovet |
| 20/10 | BSVET TCI | tci |
| 24/11 | BVVET | bvvet |
| 15/12 | Pedestal Roama | pedestal |

Regras:
- O produto da live ganha **1 post de aquecimento** no feed (2-4 semanas antes) e **1 post comercial pós-live** (1-3 dias depois, com modalidade de aquisição)
- **Não gastar o tema de uma live futura** em posts genéricos no mês anterior à campanha dela
- Campanha de live: **1 convite principal no feed + 7 stories essenciais**. Stories em D-3, D-1 pela manhã, D-1 com caixa de perguntas, D0 pela manhã, D0 falta 1 hora, D0 estamos ao vivo e D+1 agradecimento ou gravação.
- Stories extras entram apenas quando houver conteúdo ou objetivo claro. Não existe mais obrigação de publicação diária.
- Cortes de cada live viram **reels nas semanas seguintes** (~2/semana, ter e qui)

## Eventos e datas fixas (nunca perder)

- **Feiras**: PET VET Expo (12–14/08, Anhembi SP), CBAV Salvador (set, a confirmar), PETNOR (15–17/11, Olinda/PE), Animal Health (março)
- **Campanhas**: Black Friday (novembro), Natal/encerramento (dezembro)
- **Datas comemorativas recorrentes**: Dia Mundial do Gato (08/08 e 17/02), Dia dos Pais Pet (09/08), Dia Mundial do Cachorro (26/08), Dia do Médico Veterinário (09/09), Dia do Cliente (15/09), Dia do Vendedor (01/10), Dia Mundial dos Animais (04/10), Dia do Anestesista (16/10), Dia do Balconista (30/10), Dia do Vira-lata (31/07), Dia da Mulher (08/03), Dia do Zootecnista (13/05), Dia das Mães, Dia Nacional da Adoção (25/05)

## Como editar a agenda (processo)

1. Ale pede a mudança em linguagem natural (ou decide na reunião mensal)
2. Claude edita **`agenda.json`** — respeitando o schema:
   `{ id, data (ISO), camada: contrato|live|reels|evento, formato: feed|story|reel|youtube|evento, titulo, produto, ads, hora?, obs? }`
   - **ids são estáveis** (`YYYY-MM-DD-ct|lv|yt|ev-N`) — nunca renumerar (o status salvo no navegador usa o id)
3. Roda `python3 check_agenda.py` (valida schema + avisa semana com ≠2 posts de contrato)
4. Commit + push → GitHub Pages atualiza em ~1 min
5. O status atual da agenda pública fica no navegador. A migração para o App Estouro substituirá esse controle por histórico centralizado e autenticado.
6. A gestão de responsáveis, execução, entrega e próximos passos fica em `operacao-laslo.json`, exibido na aba Plano Mestre.

## O que NÃO mexer

- Fluxo de copies (aba Copies / Supabase / n8n / Apps Script): casa posts por **título literal** — se um post já tem copy gerada, não renomear o título no agenda.json sem saber que o Sheets vai criar linha nova
- `posts.csv` e `datas.csv`: **congelados** (histórico pré-reforma); `gen_pauta.py`: **aposentado**
