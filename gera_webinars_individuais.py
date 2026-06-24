#!/usr/bin/env python3
import os

OUT_DIR = "/mnt/c/Users/alexa/laslo-reuniao/webinars"
os.makedirs(OUT_DIR, exist_ok=True)

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f0; color: #1a1a2e; }

.cover {
  background: #1a1a2e;
  color: #fff;
  padding: 48px 56px 40px;
  text-align: center;
}
.cover .produto {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: #fbab48;
  font-weight: 700;
  margin-bottom: 10px;
}
.cover h1 { font-size: 24px; font-weight: 700; line-height: 1.4; margin-bottom: 10px; }
.cover .meta { font-size: 14px; color: #aaa; margin-bottom: 16px; }
.cover .tema {
  font-size: 13px;
  font-style: italic;
  color: #ccc;
  max-width: 680px;
  margin: 0 auto;
  line-height: 1.6;
  border-top: 1px solid #333;
  padding-top: 14px;
}

.content { max-width: 840px; margin: 0 auto; padding: 36px 24px 56px; }

h2 {
  font-size: 17px;
  color: #1a1a2e;
  border-bottom: 3px solid #fbab48;
  padding-bottom: 7px;
  margin: 36px 0 16px;
}

table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 8px; }
th { background: #1a1a2e; color: #fff; padding: 9px 12px; text-align: left; font-weight: 600; }
td { padding: 9px 12px; border-bottom: 1px solid #e8e8e0; vertical-align: top; line-height: 1.5; }
tr:nth-child(even) td { background: #fafaf7; }

.badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 3px;
}
.story     { background: #e3f3fd; color: #0a558c; }
.feed      { background: #d4edda; color: #155724; }
.feedstory { background: #f3e8ff; color: #6b21a8; }
.ads       { background: #fff3cd; color: #856404; margin-left: 4px; }
.nao       { background: #f0f0f0; color: #888; }

.copy-card {
  background: #fff;
  border-left: 4px solid #fbab48;
  border-radius: 0 8px 8px 0;
  padding: 14px 18px;
  margin-bottom: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.copy-card .dx { font-size: 11px; font-weight: 700; color: #fbab48; text-transform: uppercase; margin-bottom: 4px; }
.copy-card .copy-fmt { font-size: 11px; color: #888; margin-bottom: 6px; }
.copy-card .copy-text { font-size: 13px; color: #222; line-height: 1.6; }

.alert {
  background: #fff8e1;
  border-left: 4px solid #fbab48;
  padding: 12px 16px;
  font-size: 13px;
  border-radius: 0 6px 6px 0;
  margin: 16px 0;
  color: #5a4000;
  line-height: 1.5;
}

.footer {
  text-align: center;
  font-size: 11px;
  color: #999;
  padding: 24px 0 0;
  border-top: 1px solid #e0e0d8;
  margin-top: 40px;
}

@media print {
  body { background: #fff; }
  .copy-card { box-shadow: none; border: 1px solid #ddd; border-left: 4px solid #fbab48; }
}
"""

def badge_fmt(fmt):
    if fmt == 'Story':       return '<span class="badge story">Story</span>'
    if fmt == 'Feed':        return '<span class="badge feed">Feed</span>'
    if fmt == 'Feed + Story':return '<span class="badge feedstory">Feed + Story</span>'
    return fmt

def badge_ads(ads):
    if ads == 'SIM': return '<span class="badge ads">ADS</span>'
    return '<span class="badge nao">Não</span>'

def gera(wb):
    slug  = wb['slug']
    rows  = wb['posts']

    datas_rows = ""
    for p in rows:
        datas_rows += f"""
        <tr>
          <td>{p['dx']}</td>
          <td>{p['data']}</td>
          <td>{p['semana']}</td>
          <td>{badge_fmt(p['fmt'])}</td>
          <td>{badge_ads(p['ads'])}</td>
        </tr>"""

    copy_cards = ""
    for p in rows:
        copy_cards += f"""
      <div class="copy-card">
        <div class="dx">{p['dx']} &nbsp;·&nbsp; {p['data']}</div>
        <div class="copy-fmt">{p['fmt']} {'· ADS' if p['ads'] == 'SIM' else ''}</div>
        <div class="copy-text">{p['copy']}</div>
      </div>"""

    alerta_html = ""
    if wb.get('alerta'):
        alerta_html = f'<div class="alert"><strong>Atenção:</strong> {wb["alerta"]}</div>'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Webinar Laslo — {wb['titulo']}</title>
<style>{CSS}</style>
</head>
<body>

<div class="cover">
  <div class="produto">{wb['produto']}</div>
  <h1>Webinar Laslo &nbsp;·&nbsp; {wb['titulo']}</h1>
  <div class="meta">{wb['data_hora']}</div>
  <div class="tema">"{wb['tema']}"</div>
</div>

<div class="content">

  <h2>Calendário de Posts</h2>
  {alerta_html}
  <table>
    <thead>
      <tr><th>D-X</th><th>Data</th><th>Semana</th><th>Formato</th><th>ADS</th></tr>
    </thead>
    <tbody>{datas_rows}
    </tbody>
  </table>

  <h2>Copy por Post</h2>
  {copy_cards}

  <div class="footer">
    Estouro Marketing Digital &nbsp;·&nbsp; Webinar Laslo — {wb['titulo']} &nbsp;·&nbsp; {wb['data_hora']}
  </div>

</div>
</body>
</html>"""

    path = f"{OUT_DIR}/{slug}.html"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  {path}")


WEBINARS = [
    {
        'slug':      '01-icavet-bomba-infusao',
        'titulo':    'ICAVET · Bomba de Infusão',
        'produto':   'ICAVET',
        'data_hora': '30/06/2026 às 20h',
        'tema':      'A "falsa" segurança da infusão: por que sua bomba atual pode estar falhando com pacientes críticos',
        'alerta':    None,
        'posts': [
            {'dx':'D-20','data':'10/06','semana':'Jun S2','fmt':'Story',        'ads':'Não','copy':'Webinar em 20 dias! Sua bomba pode estar falhando com pacientes críticos? Salve a data — 30/06 às 20h. Inscrição gratuita, link na bio.'},
            {'dx':'D-17','data':'13/06','semana':'Jun S2','fmt':'Story',        'ads':'Não','copy':'Salve a data! 30/06 às 20h — Webinar Laslo gratuito. Você sabe quando a bomba de infusão falha silenciosamente? A gente explica. Inscrição gratuita — link na bio.'},
            {'dx':'D-13','data':'17/06','semana':'Jun S3','fmt':'Story',        'ads':'Não','copy':'Sua bomba pode estar falhando com pacientes críticos e você nem sabe. Faltam 13 dias para o Webinar Laslo. Inscrição gratuita — link na bio.'},
            {'dx':'D-10','data':'20/06','semana':'Jun S3','fmt':'Story',        'ads':'Não','copy':'Faltam 10 dias! Webinar Laslo — 30/06 às 20h. A "falsa" segurança da infusão: tudo que você precisa saber para proteger seus pacientes. Link na bio para se inscrever.'},
            {'dx':'D-7', 'data':'23/06','semana':'Jun S4','fmt':'Feed',         'ads':'SIM','copy':'Salve a data! 30/06 às 20h — Webinar Laslo gratuito.\n\nA "falsa" segurança da infusão: por que sua bomba atual pode estar falhando com pacientes críticos.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-3', 'data':'27/06','semana':'Jun S4','fmt':'Feed',         'ads':'SIM','copy':'Inscrições abertas — faltam 3 dias!\n\nWebinar Laslo: 30/06 às 20h.\nTema: A "falsa" segurança da infusão.\n\nVagas limitadas. Inscrição gratuita — link na bio.'},
            {'dx':'D-0', 'data':'30/06','semana':'Jun S5','fmt':'Feed + Story', 'ads':'SIM','copy':'Hoje às 20h — ao vivo! 🔴\n\nWebinar Laslo: A "falsa" segurança da infusão.\n\nAinda dá tempo de se inscrever — link na bio. Nos vemos lá!'},
        ],
    },
    {
        'slug':      '02-descartaveis',
        'titulo':    'Descartáveis',
        'produto':   'Insumos Descartáveis',
        'data_hora': '21/07/2026 às 20h',
        'tema':      'Alarme de oclusão: 5 causas que você ignora e que colocam seu paciente em risco',
        'alerta':    'Julho acumula a antecipação da PET VET Expo (12–14/ago) em S1 e S2. Priorizar webinar em stories e PET VET em feed.',
        'posts': [
            {'dx':'D-20','data':'01/07','semana':'Jul S1','fmt':'Story',        'ads':'Não','copy':'Webinar em 20 dias! Alarme de oclusão — 5 causas que ignoramos e que colocam pacientes em risco. Salve a data: 21/07 às 20h. Inscrição gratuita — link na bio.'},
            {'dx':'D-17','data':'04/07','semana':'Jul S1','fmt':'Story',        'ads':'Não','copy':'Salve a data! 21/07 às 20h — Webinar Laslo gratuito. O alarme de oclusão pode estar te enganando. Faltam 17 dias. Inscrição gratuita — link na bio.'},
            {'dx':'D-13','data':'08/07','semana':'Jul S2','fmt':'Story',        'ads':'Não','copy':'O alarme de oclusão te acorda à noite? Ou pior: ele dispara quando não deveria? Faltam 13 dias para o Webinar Laslo. Inscrição gratuita — link na bio.'},
            {'dx':'D-10','data':'11/07','semana':'Jul S2','fmt':'Story',        'ads':'Não','copy':'Faltam 10 dias! Webinar Laslo — 21/07 às 20h. 5 causas de oclusão que colocam seu paciente em risco. Link na bio para garantir sua vaga.'},
            {'dx':'D-7', 'data':'14/07','semana':'Jul S3','fmt':'Feed',         'ads':'SIM','copy':'Salve a data! 21/07 às 20h — Webinar Laslo gratuito.\n\nAlarme de oclusão: 5 causas que você ignora e que colocam seu paciente em risco.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-3', 'data':'18/07','semana':'Jul S3','fmt':'Feed',         'ads':'SIM','copy':'Inscrições abertas — faltam 3 dias!\n\nWebinar Laslo: 21/07 às 20h.\nTema: Alarme de oclusão — as 5 causas que ninguém fala.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-0', 'data':'21/07','semana':'Jul S4','fmt':'Feed + Story', 'ads':'SIM','copy':'Hoje às 20h — ao vivo! 🔴\n\nWebinar Laslo: Alarme de oclusão — 5 causas que colocam seu paciente em risco.\n\nAinda dá tempo de se inscrever — link na bio. Nos vemos lá!'},
        ],
    },
    {
        'slug':      '03-bs680-bomba-seringa',
        'titulo':    'BS680 · Bomba de Seringa',
        'produto':   'BS680',
        'data_hora': '25/08/2026 às 20h',
        'tema':      'TIVA para todos: como uma bomba de seringa barata democratizou a anestesia de qualidade na veterinária',
        'alerta':    'D-13 (12/08) coincide com o Dia 1 da PET VET Expo (12–14/ago). Publicar o story nos intervalos da feira.',
        'posts': [
            {'dx':'D-20','data':'05/08','semana':'Ago S1','fmt':'Story',        'ads':'Não','copy':'Webinar em 20 dias! TIVA para todos — anestesia de qualidade acessível para qualquer clínica. Salve a data: 25/08 às 20h. Inscrição gratuita — link na bio.'},
            {'dx':'D-17','data':'08/08','semana':'Ago S2','fmt':'Story',        'ads':'Não','copy':'Salve a data! 25/08 às 20h — Webinar Laslo gratuito. TIVA acessível para qualquer clínica veterinária. Faltam 17 dias. Inscrição gratuita — link na bio.'},
            {'dx':'D-13','data':'12/08','semana':'Ago S2','fmt':'Story',        'ads':'Não','copy':'Faltam 13 dias para o Webinar Laslo BS680! Estamos na PET VET Expo, mas o webinar não para. 25/08 às 20h — inscrição gratuita, link na bio.'},
            {'dx':'D-10','data':'15/08','semana':'Ago S3','fmt':'Story',        'ads':'Não','copy':'Faltam 10 dias! Webinar Laslo — 25/08 às 20h. TIVA para todos: anestesia de qualidade ao alcance de qualquer clínica. Link na bio para garantir sua vaga.'},
            {'dx':'D-7', 'data':'18/08','semana':'Ago S3','fmt':'Feed',         'ads':'SIM','copy':'Salve a data! 25/08 às 20h — Webinar Laslo gratuito.\n\nTIVA para todos: como uma bomba de seringa barata democratizou a anestesia de qualidade na veterinária.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-3', 'data':'22/08','semana':'Ago S4','fmt':'Feed',         'ads':'SIM','copy':'Inscrições abertas — faltam 3 dias!\n\nWebinar Laslo: 25/08 às 20h.\nTema: TIVA para todos — anestesia de qualidade ao alcance de qualquer clínica.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-0', 'data':'25/08','semana':'Ago S4','fmt':'Feed + Story', 'ads':'SIM','copy':'Hoje às 20h — ao vivo! 🔴\n\nWebinar Laslo: TIVA para todos — como a BS680 democratizou a anestesia de qualidade.\n\nAinda dá tempo de se inscrever — link na bio. Nos vemos lá!'},
        ],
    },
    {
        'slug':      '04-elastovet',
        'titulo':    'Elastovet',
        'produto':   'Elastovet',
        'data_hora': '29/09/2026 às 20h',
        'tema':      'Seu pós-operatório pode ser domiciliar: controle da dor 24 horas com infusão contínua, sem gotejamento manual e sem fios',
        'alerta':    'CBAV Salvador acontece em setembro (data a confirmar). Verificar complementaridade com o tema Elastovet.',
        'posts': [
            {'dx':'D-20','data':'09/09','semana':'Set S2','fmt':'Story',        'ads':'Não','copy':'Webinar em 20 dias! Pós-operatório domiciliar com infusão contínua — sem gotejamento manual e sem fios. Salve a data: 29/09 às 20h. Inscrição gratuita — link na bio.'},
            {'dx':'D-17','data':'12/09','semana':'Set S2','fmt':'Story',        'ads':'Não','copy':'Salve a data! 29/09 às 20h — Webinar Laslo gratuito. O pós-op que libera o animal para casa com controle da dor 24h. Inscrição gratuita — link na bio.'},
            {'dx':'D-13','data':'16/09','semana':'Set S3','fmt':'Story',        'ads':'Não','copy':'Seu paciente precisa ficar internado só para receber infusão? Faltam 13 dias para o Webinar Laslo Elastovet. Inscrição gratuita — link na bio.'},
            {'dx':'D-10','data':'19/09','semana':'Set S3','fmt':'Story',        'ads':'Não','copy':'Faltam 10 dias! Webinar Laslo — 29/09 às 20h. Controle da dor 24 horas, pós-op domiciliar, sem gotejamento. Link na bio para se inscrever.'},
            {'dx':'D-7', 'data':'22/09','semana':'Set S4','fmt':'Feed',         'ads':'SIM','copy':'Salve a data! 29/09 às 20h — Webinar Laslo gratuito.\n\nSeu pós-operatório pode ser domiciliar: controle da dor 24 horas com infusão contínua, sem gotejamento manual e sem fios.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-3', 'data':'26/09','semana':'Set S4','fmt':'Feed',         'ads':'SIM','copy':'Inscrições abertas — faltam 3 dias!\n\nWebinar Laslo: 29/09 às 20h.\nTema: Pós-operatório domiciliar com Elastovet — controle da dor sem internação.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-0', 'data':'29/09','semana':'Set S5','fmt':'Feed + Story', 'ads':'SIM','copy':'Hoje às 20h — ao vivo! 🔴\n\nWebinar Laslo: Pós-op domiciliar com controle da dor 24h — sem gotejamento, sem fios.\n\nAinda dá tempo de se inscrever — link na bio. Nos vemos lá!'},
        ],
    },
    {
        'slug':      '05-bsvet-tci',
        'titulo':    'BSVET TCI · Bomba Alvo Controlado',
        'produto':   'BSVET TCI',
        'data_hora': '20/10/2026 às 20h',
        'tema':      'Anestesia alvo-controlada: você está pronto para a revolução? Entenda porque esta anestesia é o futuro da sua rotina',
        'alerta':    None,
        'posts': [
            {'dx':'D-20','data':'30/09','semana':'Set S5','fmt':'Story',        'ads':'Não','copy':'Webinar em 20 dias! Anestesia alvo-controlada — você está pronto para a revolução? Salve a data: 20/10 às 20h. Inscrição gratuita — link na bio.'},
            {'dx':'D-17','data':'03/10','semana':'Out S1','fmt':'Story',        'ads':'Não','copy':'Salve a data! 20/10 às 20h — Webinar Laslo gratuito. TCI na prática: o futuro da anestesia veterinária está mais perto do que você imagina. Inscrição gratuita — link na bio.'},
            {'dx':'D-13','data':'07/10','semana':'Out S2','fmt':'Story',        'ads':'Não','copy':'Você ainda usa anestesia convencional? Faltam 13 dias para entender por que a TCI está mudando a rotina das clínicas veterinárias. Inscrição gratuita — link na bio.'},
            {'dx':'D-10','data':'10/10','semana':'Out S2','fmt':'Story',        'ads':'Não','copy':'Faltam 10 dias! Webinar Laslo — 20/10 às 20h. Anestesia alvo-controlada: a revolução que vai mudar sua rotina. Link na bio para se inscrever.'},
            {'dx':'D-7', 'data':'13/10','semana':'Out S3','fmt':'Feed',         'ads':'SIM','copy':'Salve a data! 20/10 às 20h — Webinar Laslo gratuito.\n\nAnestesia alvo-controlada: você está pronto para a revolução? Entenda porque a TCI é o futuro da sua rotina.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-3', 'data':'17/10','semana':'Out S3','fmt':'Feed',         'ads':'SIM','copy':'Inscrições abertas — faltam 3 dias!\n\nWebinar Laslo: 20/10 às 20h.\nTema: Anestesia alvo-controlada — TCI na prática para veterinários.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-0', 'data':'20/10','semana':'Out S4','fmt':'Feed + Story', 'ads':'SIM','copy':'Hoje às 20h — ao vivo! 🔴\n\nWebinar Laslo: Anestesia alvo-controlada — você está pronto para a revolução?\n\nAinda dá tempo de se inscrever — link na bio. Nos vemos lá!'},
        ],
    },
    {
        'slug':      '06-bvvet',
        'titulo':    'BVVET',
        'produto':   'BVVET',
        'data_hora': '24/11/2026 às 20h',
        'tema':      'Erros comuns em bombas de infusão: da proteção do seu paciente de falhas humanas à hidratação de pacientes nefropatas',
        'alerta':    'D-7 (17/11) coincide com o último dia da Feira PetNor (15–17/nov). Usar o estande para anunciar o webinar presencialmente também.',
        'posts': [
            {'dx':'D-20','data':'04/11','semana':'Nov S1','fmt':'Story',        'ads':'Não','copy':'Webinar em 20 dias! Erros em bombas de infusão que colocam pacientes em risco — e como evitá-los. Salve a data: 24/11 às 20h. Inscrição gratuita — link na bio.'},
            {'dx':'D-17','data':'07/11','semana':'Nov S1','fmt':'Story',        'ads':'Não','copy':'Salve a data! 24/11 às 20h — Webinar Laslo gratuito. Você conhece os erros mais comuns em bombas de infusão? Faltam 17 dias. Inscrição gratuita — link na bio.'},
            {'dx':'D-13','data':'11/11','semana':'Nov S2','fmt':'Story',        'ads':'Não','copy':'Seu paciente nefropata recebe hidratação com a precisão certa? Faltam 13 dias para o Webinar Laslo BVVET. Inscrição gratuita — link na bio.'},
            {'dx':'D-10','data':'14/11','semana':'Nov S2','fmt':'Story',        'ads':'Não','copy':'Faltam 10 dias! Webinar Laslo — 24/11 às 20h. Erros comuns em bombas de infusão: da proteção do paciente à hidratação de nefropatas. Link na bio para se inscrever.'},
            {'dx':'D-7', 'data':'17/11','semana':'Nov S3','fmt':'Feed',         'ads':'SIM','copy':'Salve a data! 24/11 às 20h — Webinar Laslo gratuito.\n\nErros comuns em bombas de infusão: da proteção do seu paciente de falhas humanas à hidratação de nefropatas.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-3', 'data':'21/11','semana':'Nov S3','fmt':'Feed',         'ads':'SIM','copy':'Inscrições abertas — faltam 3 dias!\n\nWebinar Laslo: 24/11 às 20h.\nTema: Erros comuns em bombas de infusão — proteja seus pacientes.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-0', 'data':'24/11','semana':'Nov S4','fmt':'Feed + Story', 'ads':'SIM','copy':'Hoje às 20h — ao vivo! 🔴\n\nWebinar Laslo: Erros comuns em bombas de infusão — da falha humana à hidratação do nefropata.\n\nAinda dá tempo de se inscrever — link na bio. Nos vemos lá!'},
        ],
    },
    {
        'slug':      '07-pedestal-roama',
        'titulo':    'Pedestal Roama · Ergonomia',
        'produto':   'Pedestal Roama',
        'data_hora': '15/12/2026 às 20h',
        'tema':      'Centro cirúrgico organizado ou caos de fios: como a organização do espaço físico influencia o desfecho da anestesia',
        'alerta':    None,
        'posts': [
            {'dx':'D-20','data':'25/11','semana':'Nov S4','fmt':'Story',        'ads':'Não','copy':'Webinar em 20 dias! Centro cirúrgico organizado ou caos de fios — como o espaço influencia o desfecho da anestesia. Salve a data: 15/12 às 20h. Inscrição gratuita — link na bio.'},
            {'dx':'D-17','data':'28/11','semana':'Nov S4','fmt':'Story',        'ads':'Não','copy':'Salve a data! 15/12 às 20h — Webinar Laslo gratuito. Organização do centro cirúrgico que salva vidas. Faltam 17 dias. Inscrição gratuita — link na bio.'},
            {'dx':'D-13','data':'02/12','semana':'Dez S1','fmt':'Story',        'ads':'Não','copy':'Seu centro cirúrgico é organizado ou um caos de fios? Faltam 13 dias para o Webinar Laslo Pedestal Roama. Inscrição gratuita — link na bio.'},
            {'dx':'D-10','data':'05/12','semana':'Dez S1','fmt':'Story',        'ads':'Não','copy':'Faltam 10 dias! Webinar Laslo — 15/12 às 20h. Como a organização do espaço físico influencia diretamente o desfecho da anestesia. Link na bio para se inscrever.'},
            {'dx':'D-7', 'data':'08/12','semana':'Dez S2','fmt':'Feed',         'ads':'SIM','copy':'Salve a data! 15/12 às 20h — Webinar Laslo gratuito.\n\nCentro cirúrgico organizado ou caos de fios: como a organização do espaço físico influencia o desfecho da anestesia.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-3', 'data':'12/12','semana':'Dez S2','fmt':'Feed',         'ads':'SIM','copy':'Inscrições abertas — faltam 3 dias!\n\nWebinar Laslo: 15/12 às 20h.\nTema: Centro cirúrgico organizado — como o Pedestal Roama muda sua rotina.\n\nInscrição gratuita — link na bio.'},
            {'dx':'D-0', 'data':'15/12','semana':'Dez S3','fmt':'Feed + Story', 'ads':'SIM','copy':'Hoje às 20h — ao vivo! 🔴\n\nWebinar Laslo: Centro cirúrgico organizado ou caos de fios — o impacto da ergonomia no desfecho da anestesia.\n\nAinda dá tempo de se inscrever — link na bio. Nos vemos lá!'},
        ],
    },
]

print("Gerando HTMLs individuais...")
for wb in WEBINARS:
    gera(wb)

print(f"\nPronto! {len(WEBINARS)} arquivos em {OUT_DIR}/")
