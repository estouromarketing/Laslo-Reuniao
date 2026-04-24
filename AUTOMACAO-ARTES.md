# Próxima Automação — Geração de Artes (Feed + Story)

Planejado em: 2026-04-24
Status: **em planejamento — não iniciado**

---

## Objetivo

Após aprovar a copy de um post, gerar automaticamente as artes no formato:
- **Feed**: 1080 × 1080 px
- **Story**: 1080 × 1920 px

Seguindo a identidade visual do Laslo Vet, enviando para aprovação via Telegram e arquivando no Google Drive.

---

## Arquitetura

```
[HTML] Botão "Gerar Artes" (aparece só para copies com status copy_aprovada)
    ↓
[n8n] Novo workflow separado (webhook-laslo-artes)
    ↓
Para cada post aprovado:
    → Duplica template Google Slides (feed + story)
    → Substitui {{titulo}} e {{copy}} com dados do post
    → Exporta como PNG via Google Slides API
    → Envia imagem no Telegram com botões [✓ Aprovar] [✗ Reprovar]
    ↓
[Telegram Bot] Você visualiza e decide no celular
    ↓
Se aprovado:
    → Salva PNG no Google Drive (organizado por mês)
    → Atualiza Supabase com URLs das artes (arte_feed_url, arte_story_url)
Se reprovado:
    → Notifica para revisão manual do template/copy
```

---

## Decisão: workflow separado (não integrar ao workflow de copy)

| Motivo | Detalhe |
|--------|---------|
| Timing diferente | Copy: gerada logo ao salvar a reunião. Arte: só após copy aprovada |
| Custo | APIs de imagem cobram por geração — não desperdiçar em copies que ainda vão mudar |
| Falha isolada | Se a API de imagem cair, não afeta a geração de copy |
| Reutilização | O workflow de arte pode ser reaproveitado para outros clientes, mudando só os templates |

---

## Stack planejada

| Bloco | Ferramenta | Custo | Motivo |
|-------|-----------|-------|--------|
| Render de imagem | Google Slides API | Grátis | Já no ecossistema Google, templates visuais fáceis de editar, ilimitado |
| Aprovação | Telegram Bot | Grátis | Integração nativa no n8n, funciona no celular |
| Armazenamento | Google Drive | Grátis | Organização por pasta/mês, fácil acesso |
| Automação | n8n (já existe) | Grátis (self-hosted) | Mesmo servidor de automacao.estouro.com.br |
| Banco de dados | Supabase (já existe) | Grátis | Adicionar campos arte_feed_url e arte_story_url na tabela posts |

### Alternativas ao Google Slides (caso haja limitação técnica)

| Ferramenta | Gratuito | Pago | Obs |
|-----------|----------|------|-----|
| Placid | 50 imgs/mês | $19/mês | Integração nativa no n8n |
| htmlcsstoimage.com | 50 imgs/mês | $19/mês | Via HTTP Request |
| Bannerbear | 30 imgs/mês | $49/mês | Fora do orçamento |

> Volume esperado: 8 posts × 2 formatos = 16 imagens/mês → qualquer opção gratuita cobre.

---

## Supabase — campos a adicionar na tabela `posts`

```sql
ALTER TABLE posts ADD COLUMN arte_feed_url text;
ALTER TABLE posts ADD COLUMN arte_story_url text;
ALTER TABLE posts ADD COLUMN arte_status text DEFAULT 'pendente';
-- arte_status: pendente → gerada → aprovada → reprovada
```

---

## Estrutura de pastas no Google Drive

```
Drive/
  Laslo/
    Artes/
      Mai_2026/
        feed/
          01-dia-das-maes.png
          02-clube-laslo-fidelidade.png
        story/
          01-dia-das-maes.png
          02-clube-laslo-fidelidade.png
```

---

## Templates Google Slides — o que preparar

Antes de construir o workflow, precisamos criar os templates no Google Slides:

### Template Feed (1080×1080)
- [ ] Slide configurado para 1080×1080 (Arquivo → Configurar página → Personalizado)
- [ ] Logo Laslo posicionado
- [ ] Paleta de cores da marca aplicada
- [ ] Placeholder `{{titulo}}` — caixa de texto com fonte/tamanho definido
- [ ] Placeholder `{{copy}}` — caixa de texto com fonte menor
- [ ] Compartilhar o arquivo com a conta de serviço do Google (para a API editar)

### Template Story (1080×1920)
- [ ] Mesmos elementos, layout vertical

---

## Telegram Bot — setup

1. Abrir @BotFather no Telegram
2. `/newbot` → definir nome e username
3. Guardar o **token** do bot
4. Criar um grupo ou canal privado e adicionar o bot
5. Pegar o **chat_id** do grupo
6. Configurar no n8n: credencial Telegram com o token

---

## n8n — estrutura do novo workflow

**Nome sugerido:** `laslo-artes`
**Webhook:** `https://automacao.estouro.com.br/webhook/laslo-artes`

| Nó | Tipo | Função |
|----|------|--------|
| Webhook | Trigger | Recebe lista de posts aprovados do HTML |
| Extrair Posts | Split | Processa post a post |
| Buscar Dados | Supabase GET | Busca titulo + copy_text pelo id |
| Gerar Feed | Google Slides | Duplica template feed, substitui placeholders, exporta PNG |
| Gerar Story | Google Slides | Duplica template story, substitui placeholders, exporta PNG |
| Enviar Telegram | Telegram | Envia as 2 imagens com botões Aprovar/Reprovar |
| Aguardar Resposta | Telegram Trigger | Escuta resposta do bot |
| Se Aprovado | IF | Verifica resposta |
| Salvar Drive | Google Drive | Salva PNG na pasta do mês |
| Atualizar Supabase | HTTP Request | PATCH arte_feed_url, arte_story_url, arte_status=aprovada |

---

## HTML — o que adicionar

- Botão **"Gerar Artes"** na aba Copies (visível apenas quando há copies aprovadas)
- Visualização das artes geradas (feed + story) em miniatura
- Status da arte por post: `pendente` / `gerada` / `aprovada`

---

## Pré-requisitos para começar

- [ ] Identidade visual do Laslo mapeada (cores, fontes, logo em PNG/SVG)
- [ ] Templates Google Slides criados (feed + story)
- [ ] Telegram Bot criado e token anotado
- [ ] Pasta no Google Drive criada e compartilhada com conta de serviço Google
- [ ] Decisão sobre o trigger: botão manual no HTML ou automático ao aprovar copy

---

## Referências de custo mensal

| Item | Custo |
|------|-------|
| n8n (self-hosted) | R$ 0 (já existe) |
| Google Slides API | R$ 0 |
| Google Drive | R$ 0 |
| Telegram Bot | R$ 0 |
| Supabase | R$ 0 (free tier) |
| GitHub Pages | R$ 0 |
| **Total** | **R$ 0** |
