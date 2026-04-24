// ══════════════════════════════════════════════════════════
// GOOGLE APPS SCRIPT — Laslo Reuniao
// Cole em: Extensões → Apps Script → substitua tudo
// ══════════════════════════════════════════════════════════

function doGet(e)  { return rotear(e); }
function doPost(e) { return rotear(e); }

function rotear(e) {
  var p = extrairParams(e);
  var action = (p && p.action) || '';
  if (action === 'save_copy') return salvarCopy(p);
  if (action === 'save_copy_supabase') return salvarCopyDoSupabase(p);
  // Só salva reunião se tiver mes — evita apagar aba por chamada acidental sem dados
  if (p && p.mes) return salvar(e);
  return jsonResp({status:'error', msg:'action ou mes ausente'});
}

function salvarCopyDoSupabase(p) {
  var id  = p.id  || '';
  var mes = (p.mes || '').trim();
  if (!id)  return jsonResp({status:'error', msg:'id ausente'});
  if (!mes) return jsonResp({status:'error', msg:'mes ausente'});

  var SUPABASE_URL = 'https://lrrjybvdxuxgbelfozvr.supabase.co';
  var SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxycmp5YnZkeHV4Z2JlbGZvenZyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0MzM5NTAsImV4cCI6MjA5MTAwOTk1MH0.OJBvapDrm0NKQXqo4CY9ITv5H4y0Tn3Yot1uR3ybTao';

  var resp = UrlFetchApp.fetch(
    SUPABASE_URL + '/rest/v1/posts?id=eq.' + encodeURIComponent(id) + '&select=titulo,conteudo',
    { method:'GET', headers:{ 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY } }
  );
  var data = JSON.parse(resp.getContentText());
  if (!data || data.length === 0) return jsonResp({status:'error', msg:'post nao encontrado no supabase'});

  var titulo   = data[0].titulo  || '';
  var copyText = data[0].conteudo || '';
  if (!copyText) return jsonResp({status:'error', msg:'conteudo vazio no supabase'});

  var ss  = SpreadsheetApp.getActiveSpreadsheet();
  var aba = ss.getSheetByName(mes.replace(' ', '_'));
  if (!aba) return jsonResp({status:'error', msg:'aba nao encontrada: ' + mes});

  var colA = aba.getRange('A:A').getValues();
  var found = -1;
  for (var i = 0; i < colA.length; i++) {
    if (String(colA[i][0]).trim() === String(titulo).trim()) { found = i + 1; break; }
  }
  if (found === -1) return jsonResp({status:'error', msg:'titulo nao encontrado: ' + titulo});

  aba.getRange(found, 5).setValue(copyText);
  return jsonResp({status:'ok', mes:mes, titulo:titulo, row:found, copy_len:copyText.length});
}

function extrairParams(e) {
  if (!e) return {};
  if (e.postData && e.postData.contents) {
    // Tenta JSON (usado pelo save_copy do n8n)
    try { return JSON.parse(e.postData.contents); } catch(err) {}
    // Tenta form-encoded (usado pelo saveToSheets do HTML)
    try {
      var params = {};
      var pairs = e.postData.contents.split('&');
      for (var i = 0; i < pairs.length; i++) {
        var eq = pairs[i].indexOf('=');
        if (eq > 0) {
          var k = decodeURIComponent(pairs[i].slice(0, eq).replace(/\+/g, ' '));
          var v = decodeURIComponent(pairs[i].slice(eq + 1).replace(/\+/g, ' '));
          params[k] = v;
        }
      }
      if (Object.keys(params).length > 0) return params;
    } catch(err2) {}
  }
  // GET com query params
  return e.parameter || {};
}

function salvarCopy(p) {
  try {
    var ss      = SpreadsheetApp.getActiveSpreadsheet();
    var mes     = (p.mes || '').trim();
    var titulo  = (p.titulo || '').trim();
    var copyText = p.copy_text || '';

    var abaName = mes.replace(' ', '_');
    var aba = ss.getSheetByName(abaName);
    if (!aba) return jsonResp({status:'erro', msg:'Aba nao encontrada: ' + abaName});

    var lastRow = aba.getLastRow();
    var colA = aba.getRange(1, 1, lastRow, 1).getValues();

    var found = -1;
    for (var i = 0; i < colA.length; i++) {
      if (String(colA[i][0]).trim() === titulo) { found = i + 1; break; }
    }

    if (found === -1) {
      // Título não encontrado: insere linha nova antes de "1B. CAMPANHAS DE ADS"
      var insertBefore = -1;
      for (var j = 0; j < colA.length; j++) {
        if (String(colA[j][0]).trim().indexOf('1B.') === 0) { insertBefore = j + 1; break; }
      }
      if (insertBefore > 0) {
        aba.insertRowBefore(insertBefore);
        aba.getRange(insertBefore, 1, 1, aba.getMaxColumns()).clearFormat().setFontColor('#000000');
        aba.getRange(insertBefore, 1).setValue(titulo);
        aba.getRange(insertBefore, 5).setValue(copyText);
        found = insertBefore;
      } else {
        found = lastRow + 1;
        aba.getRange(found, 1).setValue(titulo);
        aba.getRange(found, 5).setValue(copyText);
      }
    } else {
      aba.getRange(found, 5).setValue(copyText);
    }

    // garante header na col E se ainda não existe
    var headerE = aba.getRange(4, 5).getValue();
    if (!headerE) aba.getRange(4, 5).setValue('Copy IA').setFontWeight('bold').setBackground('#F2EFE9');

    return jsonResp({status:'ok', mes:mes, titulo:titulo, row:found, copy_len:copyText.length});
  } catch(err) {
    return jsonResp({status:'erro', msg:err.toString()});
  }
}

function jsonResp(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function salvar(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var p = extrairParams(e);
    var mes = (p.mes || '').trim();
    if (!mes) return jsonResp({status:'erro', msg:'mes nao informado'});

    var resumo = ss.getSheetByName('Resumo');
    if (!resumo) {
      resumo = ss.insertSheet('Resumo');
      resumo.appendRow(['Data do Registro','Mes','Data da Reuniao','Observacoes']);
      resumo.getRange(1,1,1,4).setBackground('#CACDD9').setFontWeight('bold').setFontSize(11);
      resumo.setFrozenRows(1);
    }
    resumo.appendRow([new Date().toLocaleString('pt-BR'), mes, p.data_reuniao || '', p.notas || '']);

    var abaName = mes.replace(' ', '_');
    var aba = ss.getSheetByName(abaName);
    if (!aba) {
      aba = ss.insertSheet(abaName);
    } else {
      // Desmescla tudo antes de limpar para evitar artefatos de formatação
      try { aba.getRange(1,1,Math.max(aba.getLastRow(),1),aba.getMaxColumns()).breakApart(); } catch(e2) {}
      aba.clear();
    }

    var row = 1;
    aba.getRange(row,1).setValue('Titulo');
    aba.getRange(row,2).setValue('Semana');
    aba.getRange(row,3).setValue('ADS');
    aba.getRange(row,4).setValue('Status');
    aba.getRange(row,5).setValue('PAUTA — ' + mes.toUpperCase() + ' | Data: ' + (p.data_reuniao || ''));
    aba.getRange(row,1,1,5).setBackground('#CACDD9').setFontWeight('bold').setFontSize(11);
    row += 1;

    aba.getRange(row,1,1,4).merge().setValue('1A. POSTS DO MES').setBackground('#E8690A').setFontColor('#FFFFFF').setFontWeight('bold');
    row++;
    aba.getRange(row,1,1,5).setValues([['Tema / Conteudo','Semana','ADS?','Status','Copy IA']]).setFontWeight('bold').setBackground('#F2EFE9');
    aba.setColumnWidth(5,400);
    row++;
    try {
      var posts = JSON.parse(p.posts || '[]');
      posts.forEach(function(p2, i) {
        aba.getRange(row,1).setValue(p2.tema || '');
        aba.getRange(row,2).setValue('S' + (Math.floor(i/2)+1));
        aba.getRange(row,3).setValue(p2.ads || '');
        aba.getRange(row,4).setValue(p2.status || '');
        // Define background explicitamente em toda a linha para apagar formatação residual
        aba.getRange(row,1,1,5).setBackground(i % 2 === 0 ? '#F2EFE9' : '#FFFFFF')
          .setFontColor('#000000').setFontWeight('normal');
        row++;
      });
    } catch(err) {}
    row++;

    aba.getRange(row,1,1,4).merge().setValue('1B. CAMPANHAS DE ADS').setBackground('#E8690A').setFontColor('#FFFFFF').setFontWeight('bold');
    row++;
    aba.getRange(row,1,1,4).setValues([['Campanha','Plataforma','Investido (R$)','Status']]).setFontWeight('bold').setBackground('#F2EFE9');
    row++;
    try {
      var ads = JSON.parse(p.ads || '[]');
      ads.forEach(function(a) {
        aba.getRange(row,1).setValue(a.campanha || '');
        aba.getRange(row,2).setValue(a.plataforma || '');
        aba.getRange(row,3).setValue(a.valor || '');
        aba.getRange(row,4).setValue(a.status || '');
        row++;
      });
    } catch(err) {}
    row++;

    aba.getRange(row,1,1,2).merge().setValue('1C. ACOES ESTRATEGICAS (AAR)').setBackground('#E8690A').setFontColor('#FFFFFF').setFontWeight('bold');
    row++;
    aba.getRange(row,1,1,2).setValues([['Acao','Status']]).setFontWeight('bold').setBackground('#F2EFE9');
    row++;
    try {
      var aar = JSON.parse(p.aar || '[]');
      aar.forEach(function(a) {
        aba.getRange(row,1).setValue(a.acao || '');
        aba.getRange(row,2).setValue(a.status || '');
        row++;
      });
    } catch(err) {}
    row++;

    aba.getRange(row,1,1,2).merge().setValue('2A. KPIs DO MES ANTERIOR').setBackground('#E8690A').setFontColor('#FFFFFF').setFontWeight('bold');
    row++;
    aba.getRange(row,1,1,2).setValues([['Indicador','Valor']]).setFontWeight('bold').setBackground('#F2EFE9');
    row++;
    try {
      var kpis = JSON.parse(p.kpis || '[]');
      kpis.forEach(function(k, i) {
        aba.getRange(row,1).setValue(k.label || '');
        aba.getRange(row,2).setValue(k.valor || '');
        if (i % 2 === 0) aba.getRange(row,1,1,2).setBackground('#FAFAFA');
        row++;
      });
    } catch(err) {}
    row++;

    aba.getRange(row,1,1,2).merge().setValue('2B. SITE & E-COMMERCE').setBackground('#E8690A').setFontColor('#FFFFFF').setFontWeight('bold');
    row++;
    aba.getRange(row,1,1,2).setValues([['Indicador','Valor']]).setFontWeight('bold').setBackground('#F2EFE9');
    row++;
    try {
      var ecom = JSON.parse(p.ecom || '[]');
      ecom.forEach(function(e2, i) {
        aba.getRange(row,1).setValue(e2.label || '');
        aba.getRange(row,2).setValue(e2.valor || '');
        if (i % 2 === 0) aba.getRange(row,1,1,2).setBackground('#FAFAFA');
        row++;
      });
    } catch(err) {}
    row++;

    aba.getRange(row,1,1,4).merge().setValue('3B. BRIEFINGS / ARTES PENDENTES').setBackground('#E8690A').setFontColor('#FFFFFF').setFontWeight('bold');
    row++;
    aba.getRange(row,1,1,4).setValues([['Material','Formato','Prazo','Status']]).setFontWeight('bold').setBackground('#F2EFE9');
    row++;
    try {
      var brf = JSON.parse(p.briefings || '[]');
      brf.forEach(function(b) {
        aba.getRange(row,1).setValue(b.material || '');
        aba.getRange(row,2).setValue(b.formato || '');
        aba.getRange(row,3).setValue(b.prazo || '');
        aba.getRange(row,4).setValue(b.status || '');
        row++;
      });
    } catch(err) {}
    row++;

    aba.getRange(row,1,1,4).merge().setValue('OBSERVACOES GERAIS').setBackground('#E8690A').setFontColor('#FFFFFF').setFontWeight('bold');
    row++;
    aba.getRange(row,1,1,4).merge().setValue(p.notas || '').setWrap(true);

    aba.setColumnWidth(1,340);
    aba.setColumnWidth(2,130);
    aba.setColumnWidth(3,130);
    aba.setColumnWidth(4,150);

    return jsonResp({status:'ok', mes:mes});
  } catch (err) {
    return jsonResp({status:'erro', msg:err.toString()});
  }
}

function testar() {
  var fakeEvent = {
    parameter: {
      mes: 'Abr 2026',
      data_reuniao: '17/04/2026',
      posts: '[{"tema":"Abril Laranja","ads":"Nao","status":"Feito"}]',
      aar: '[{"acao":"E-commerce","status":"Em andamento"}]',
      kpis: '[{"label":"Alcance organico","valor":"310"}]',
      ecom: '[{"label":"Visitas ao site","valor":"189"}]',
      ads: '[{"campanha":"Teste ADS","plataforma":"Meta Ads","valor":"R$ 262","status":"Feito"}]',
      briefings: '[{"material":"Banner Abril","formato":"Feed","prazo":"01/04","status":"Pendente"}]',
      notas: 'Reuniao de teste.'
    }
  };
  Logger.log('Teste mes: ' + fakeEvent.parameter.mes);
  var result = salvar(fakeEvent);
  Logger.log('Resultado: ' + result.getContent());
}

// ══════════════════════════════════════════════════════════
// MIGRAÇÃO KPIs — rodar em 2 etapas separadas:
//   1) Selecionar migrarFlat  → executa → cria aba KPIs
//   2) Selecionar migrarPivot → executa → cria aba Consolidado
// ══════════════════════════════════════════════════════════

var KPI_MESES = ['Set 2025','Out 2025','Nov 2025','Dez 2025','Jan 2026','Fev 2026','Mar 2026'];
var KPI_CATS = ['instagram','metaads','gmn','linkedin'];
var KPI_CAT_LABELS = {instagram:'Instagram',metaads:'Meta Ads',gmn:'Google Meu Negocio',linkedin:'LinkedIn'};

var KPI_DATA = {
  'Set 2025': {
    instagram: {'Alcance total':852,'Alcance organico':401,'Alcance pago':0,'Engajamento total':145,'Novos seguidores':4,'Seguidores totais':2298,'Visitas perfil':null,'Visualizacoes totais':5629,'Postagens feed':8,'Curtidas':47,'Comentarios':4,'Salvamentos':0,'Compartilhamentos':3,'Interacoes totais':88,'Interacoes postagens':60,'Alcance postagens':252,'Num Reels':2,'Alcance Reels':148,'Interacoes Reels':27,'Curtidas Reels':18,'Comentarios Reels':1,'Salvamentos Reels':0,'Compartilhamentos Reels':3,'Num Stories':5,'Views Stories':358,'Interacoes Stories':0},
    metaads: {'Valor gasto':0,'Impressoes':0,'Alcance':0,'Cliques totais':0,'Cliques link':0,'Conversas iniciadas':0,'CTR':null,'CPC':null,'CPM':null,'Frequencia':null},
    gmn: {'Total acoes':59,'Cliques website':21,'Visualizacoes':236,'Ligacoes':2,'Views pesquisa':192,'Rotas':36,'Views Maps':44,'Pesquisas laslo':null},
    linkedin: {'Seguidores totais':176,'Novos seguidores':4,'Alcance':451,'Impressoes':792,'Engajamento':67,'Reacoes':45,'Cliques':21,'Postagens':7}
  },
  'Out 2025': {
    instagram: {'Alcance total':1274,'Alcance organico':503,'Alcance pago':0,'Engajamento total':211,'Novos seguidores':10,'Seguidores totais':2303,'Visitas perfil':106,'Visualizacoes totais':7379,'Postagens feed':12,'Curtidas':89,'Comentarios':1,'Salvamentos':2,'Compartilhamentos':1,'Interacoes totais':129,'Interacoes postagens':96,'Alcance postagens':224,'Num Reels':1,'Alcance Reels':160,'Interacoes Reels':29,'Curtidas Reels':24,'Comentarios Reels':0,'Salvamentos Reels':0,'Compartilhamentos Reels':2,'Num Stories':21,'Views Stories':1525,'Interacoes Stories':4},
    metaads: {'Valor gasto':0,'Impressoes':0,'Alcance':0,'Cliques totais':0,'Cliques link':0,'Conversas iniciadas':0,'CTR':null,'CPC':null,'CPM':null,'Frequencia':null},
    gmn: {'Total acoes':84,'Cliques website':8,'Visualizacoes':279,'Ligacoes':2,'Views pesquisa':239,'Rotas':74,'Views Maps':40,'Pesquisas laslo':null},
    linkedin: {'Seguidores totais':181,'Novos seguidores':5,'Alcance':738,'Impressoes':1243,'Engajamento':98,'Reacoes':72,'Cliques':26,'Postagens':9}
  },
  'Nov 2025': {
    instagram: {'Alcance total':4257,'Alcance organico':285,'Alcance pago':2855,'Engajamento total':202,'Novos seguidores':0,'Seguidores totais':2329,'Visitas perfil':230,'Visualizacoes totais':18273,'Postagens feed':12,'Curtidas':62,'Comentarios':0,'Salvamentos':0,'Compartilhamentos':14,'Interacoes totais':124,'Interacoes postagens':90,'Alcance postagens':324,'Num Reels':1,'Alcance Reels':169,'Interacoes Reels':14,'Curtidas Reels':12,'Comentarios Reels':1,'Salvamentos Reels':1,'Compartilhamentos Reels':0,'Num Stories':9,'Views Stories':816,'Interacoes Stories':24},
    metaads: {'Valor gasto':211,'Impressoes':8391,'Alcance':3378,'Cliques totais':144,'Cliques link':88,'Conversas iniciadas':22,'CTR':1.05,'CPC':1.47,'CPM':25.15,'Frequencia':2.48},
    gmn: {'Total acoes':65,'Cliques website':7,'Visualizacoes':213,'Ligacoes':1,'Views pesquisa':179,'Rotas':57,'Views Maps':34,'Pesquisas laslo':null},
    linkedin: {'Seguidores totais':181,'Novos seguidores':0,'Alcance':245,'Impressoes':441,'Engajamento':27,'Reacoes':20,'Cliques':6,'Postagens':4}
  },
  'Dez 2025': {
    instagram: {'Alcance total':2161,'Alcance organico':303,'Alcance pago':672,'Engajamento total':88,'Novos seguidores':28,'Seguidores totais':2345,'Visitas perfil':166,'Visualizacoes totais':6444,'Postagens feed':4,'Curtidas':25,'Comentarios':0,'Salvamentos':1,'Compartilhamentos':17,'Interacoes totais':75,'Interacoes postagens':61,'Alcance postagens':187,'Num Reels':1,'Alcance Reels':87,'Interacoes Reels':5,'Curtidas Reels':4,'Comentarios Reels':0,'Salvamentos Reels':0,'Compartilhamentos Reels':0,'Num Stories':7,'Views Stories':611,'Interacoes Stories':15},
    metaads: {'Valor gasto':65.16,'Impressoes':2513,'Alcance':1573,'Cliques totais':44,'Cliques link':23,'Conversas iniciadas':5,'CTR':0.92,'CPC':1.48,'CPM':25.93,'Frequencia':1.6},
    gmn: {'Total acoes':47,'Cliques website':6,'Visualizacoes':187,'Ligacoes':2,'Views pesquisa':142,'Rotas':39,'Views Maps':45,'Pesquisas laslo':79},
    linkedin: {'Seguidores totais':193,'Novos seguidores':10,'Alcance':119,'Impressoes':246,'Engajamento':30,'Reacoes':23,'Cliques':7,'Postagens':2}
  },
  'Jan 2026': {
    instagram: {'Alcance total':1082,'Alcance organico':739,'Alcance pago':1,'Engajamento total':181,'Novos seguidores':9,'Seguidores totais':null,'Visitas perfil':87,'Visualizacoes totais':4032,'Postagens feed':8,'Curtidas':47,'Comentarios':1,'Salvamentos':1,'Compartilhamentos':3,'Interacoes totais':139,'Interacoes postagens':55,'Alcance postagens':343,'Num Reels':1,'Alcance Reels':495,'Interacoes Reels':79,'Curtidas Reels':52,'Comentarios Reels':4,'Salvamentos Reels':3,'Compartilhamentos Reels':9,'Num Stories':0,'Views Stories':0,'Interacoes Stories':0},
    metaads: {'Valor gasto':0,'Impressoes':0,'Alcance':0,'Cliques totais':0,'Cliques link':0,'Conversas iniciadas':0,'CTR':null,'CPC':null,'CPM':null,'Frequencia':null},
    gmn: {'Total acoes':50,'Cliques website':12,'Visualizacoes':198,'Ligacoes':2,'Views pesquisa':177,'Rotas':36,'Views Maps':21,'Pesquisas laslo':98},
    linkedin: {'Seguidores totais':200,'Novos seguidores':9,'Alcance':331,'Impressoes':596,'Engajamento':64,'Reacoes':48,'Cliques':19,'Postagens':7}
  },
  'Fev 2026': {
    instagram: {'Alcance total':5424,'Alcance organico':310,'Alcance pago':3250,'Engajamento total':529,'Novos seguidores':4,'Seguidores totais':2367,'Visitas perfil':107,'Visualizacoes totais':13246,'Postagens feed':4,'Curtidas':45,'Comentarios':4,'Salvamentos':3,'Compartilhamentos':4,'Interacoes totais':82,'Interacoes postagens':61,'Alcance postagens':342,'Num Reels':0,'Alcance Reels':72,'Interacoes Reels':3,'Curtidas Reels':0,'Comentarios Reels':0,'Salvamentos Reels':0,'Compartilhamentos Reels':0,'Num Stories':3,'Views Stories':241,'Interacoes Stories':10},
    metaads: {'Valor gasto':262.79,'Impressoes':87746,'Alcance':4445,'Cliques totais':657,'Cliques link':264,'Conversas iniciadas':40,'CTR':0.30,'CPC':0.40,'CPM':2.99,'Frequencia':19.74},
    gmn: {'Total acoes':47,'Cliques website':16,'Visualizacoes':189,'Ligacoes':2,'Views pesquisa':146,'Rotas':29,'Views Maps':43,'Pesquisas laslo':87},
    linkedin: {'Seguidores totais':205,'Novos seguidores':3,'Alcance':299,'Impressoes':523,'Engajamento':65,'Reacoes':54,'Cliques':12,'Postagens':4}
  },
  'Mar 2026': {
    instagram: {'Alcance total':7259,'Alcance organico':427,'Alcance pago':4764,'Engajamento total':194,'Novos seguidores':37,'Seguidores totais':2397,'Visitas perfil':160,'Visualizacoes totais':16019,'Postagens feed':4,'Curtidas':32,'Comentarios':0,'Salvamentos':1,'Compartilhamentos':6,'Interacoes totais':93,'Interacoes postagens':47,'Alcance postagens':212,'Num Reels':0,'Alcance Reels':64,'Interacoes Reels':23,'Curtidas Reels':16,'Comentarios Reels':0,'Salvamentos Reels':3,'Compartilhamentos Reels':2,'Num Stories':6,'Views Stories':373,'Interacoes Stories':16},
    metaads: {'Valor gasto':305.88,'Impressoes':19733,'Alcance':6299,'Cliques totais':200,'Cliques link':105,'Conversas iniciadas':30,'CTR':0.53,'CPC':2.91,'CPM':15.50,'Frequencia':3.13},
    gmn: {'Total acoes':59,'Cliques website':17,'Visualizacoes':212,'Ligacoes':0,'Views pesquisa':176,'Rotas':42,'Views Maps':36,'Pesquisas laslo':null},
    linkedin: {'Seguidores totais':208,'Novos seguidores':7,'Alcance':223,'Impressoes':378,'Engajamento':44,'Reacoes':38,'Cliques':5,'Postagens':2}
  }
};

function migrarFlat() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Base de Dados');
  if (!sheet) sheet = ss.insertSheet('Base de Dados');
  else sheet.clearContents();

  var rows = [['Mes','Categoria','Metrica','Valor']];
  KPI_MESES.forEach(function(mes) {
    KPI_CATS.forEach(function(cat) {
      var metricas = KPI_DATA[mes][cat] || {};
      Object.keys(metricas).forEach(function(m) {
        var v = metricas[m];
        rows.push([mes, KPI_CAT_LABELS[cat], m, v === null ? '' : v]);
      });
    });
  });
  sheet.getRange(1,1,rows.length,4).setValues(rows);
  Logger.log('KPIs gravado: ' + (rows.length-1) + ' linhas');
}

function migrarPivot() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Consolidado');
  if (!sheet) sheet = ss.insertSheet('Consolidado');
  else sheet.clearContents();

  var header = ['Categoria','Metrica'].concat(KPI_MESES);
  var rows = [header];

  KPI_CATS.forEach(function(cat) {
    var metricas = [];
    KPI_MESES.forEach(function(mes) {
      Object.keys(KPI_DATA[mes][cat] || {}).forEach(function(k) {
        if (metricas.indexOf(k) === -1) metricas.push(k);
      });
    });
    metricas.forEach(function(m) {
      var row = [KPI_CAT_LABELS[cat], m];
      KPI_MESES.forEach(function(mes) {
        var v = KPI_DATA[mes][cat] ? KPI_DATA[mes][cat][m] : undefined;
        row.push(v === null || v === undefined ? '' : v);
      });
      rows.push(row);
    });
    rows.push(new Array(header.length).fill(''));
  });

  sheet.getRange(1,1,rows.length,header.length).setValues(rows);
  Logger.log('Consolidado gravado: ' + (rows.length-1) + ' linhas');
}
