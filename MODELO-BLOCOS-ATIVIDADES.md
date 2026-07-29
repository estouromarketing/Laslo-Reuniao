# Modelo de blocos de atividades

## Objetivo

Transformar a agenda extensa da Laslo em uma visão prática, organizada por campanha e tema.

A agenda continua sendo a fonte das datas. Os blocos são uma camada de leitura e gestão.

## Blocos

### PET VET Expo

Agrupa todas as atividades relacionadas à feira:

- antecipação;
- localização do estande;
- condições comerciais;
- stories de contagem;
- cobertura;
- captação;
- pós-evento.

### Live e Webinar

Cria um bloco para cada produto da live:

- save the date;
- feed de abertura;
- stories de contagem;
- landing page;
- Grupo VIP;
- sorteio;
- transmissão;
- pós-live.

Posts do mesmo produto no mês da campanha entram no bloco da live para evitar duplicidade.

### Produtos e soluções

Agrupa:

- bombas;
- insumos;
- Clube Laslo;
- comodato;
- locação;
- venda moderada;
- conteúdos técnicos.

### Institucional

Agrupa:

- DNA VET;
- equipe;
- indústria;
- suporte;
- história;
- homenagens ligadas ao posicionamento da Laslo.

### Datas e eventos

Agrupa datas comemorativas e eventos que não pertencem a uma campanha específica.

### Reels e vídeos

Agrupa:

- cortes de lives;
- Reels;
- vídeos para YouTube;
- reaproveitamentos audiovisuais.

## Informações de cada bloco

Cada bloco mostra:

- período;
- quantidade de feeds;
- quantidade de stories;
- atividades em aberto;
- itens aguardando a Vera;
- próxima ação;
- conflitos de publicação;
- concentração de entregas internas;
- principais marcos.

## Conflitos de datas

### Conflito de publicação

Existe quando duas campanhas ou temas diferentes possuem publicação no mesmo dia.

Várias peças da mesma campanha no mesmo dia, como stories do dia da live, não são tratadas como conflito.

### Conflito de produção

Existe quando três ou mais entregas internas possuem o mesmo prazo de criação.

O alerta serve para antecipar produção ou redistribuir prazos.

## Datas

Cada atividade pode ter:

- `data_criacao`;
- `data_aprovacao`;
- `data_publicacao`;
- `hora_publicacao`.

Durante a transição:

- `data` continua sendo a data oficial de publicação;
- quando `data_criacao` não existe, o sistema calcula uma referência;
- feed usa antecedência padrão de 7 dias;
- story usa antecedência padrão de 5 dias;
- reel usa antecedência padrão de 7 dias.

As datas calculadas são apoio operacional. Datas importantes devem ser cadastradas explicitamente.

## Gestão

### Andamento

1. Não iniciado
2. Em criação
3. Revisão interna
4. Aguardando aprovação
5. Ajustes solicitados
6. Aprovado
7. Agendado
8. Publicado

### Aprovação

1. Não enviado
2. Aguardando Vera
3. Ajustes solicitados
4. Aprovado

## Visualizações

### Cliente

Mostra:

- prioridades;
- blocos resumidos;
- datas de publicação;
- formatos;
- campanhas;
- pontos que dependem da Laslo.

Não mostra:

- responsáveis internos;
- prazos de criação;
- controles operacionais;
- detalhes técnicos.

### Interna

Mostra:

- prazo de criação;
- andamento;
- aprovação;
- conflitos;
- itens em aberto;
- filtros.

## Persistência atual

Andamento e aprovação ficam salvos no navegador.

Essa solução é temporária. A evolução recomendada é persistir os campos no Supabase para:

- compartilhar status entre computadores;
- registrar usuário e horário da mudança;
- manter histórico;
- reduzir risco de perda;
- permitir uso simultâneo pela equipe.

## Regras de linguagem

Na visualização da Laslo:

- não usar emoticons;
- não usar travessões;
- usar títulos objetivos;
- manter tom industrial e profissional.

Os títulos literais do `agenda.json` não são alterados automaticamente, pois podem estar vinculados às copies. O sistema limpa os títulos apenas para exibição.
