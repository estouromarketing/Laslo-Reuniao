#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_kpi.py - Gera o bloco KPI_ANALYTICS_DATA de um mês a partir do Supabase.

Uso:
    python sync_kpi.py "Jun 2026"

O script lê os dados do mês na tabela `relatorios` (cliente Laslo) no Supabase,
traduz os nomes dos campos para o formato do index.html e imprime o bloco JS
pronto para colar/substituir dentro de `const KPI_ANALYTICS_DATA = { ... }`.

Fluxo mensal:
1. Atualizar o mês no Supabase (PATCH em /relatorios)
2. python sync_kpi.py "Jun 2026"
3. Colar o bloco impresso no index.html (substituindo o mês, ou adicionando)
4. git commit + push

Obs: a anon key abaixo é a mesma já presente no index.html (chave pública).
"""
import sys
import json
import urllib.request
import urllib.parse

SUPABASE_URL = "https://lrrjybvdxuxgbelfozvr.supabase.co"
SUPABASE_KEY = "sb_publishable_o31aljnSp_CoQSQV4W9S6w_sqpnktJP"
LASLO_ID = "75c7eef6-aec1-4392-9f97-f6ef06e28936"

MESES = {
    "Jan": "01", "Fev": "02", "Mar": "03", "Abr": "04", "Mai": "05", "Jun": "06",
    "Jul": "07", "Ago": "08", "Set": "09", "Out": "10", "Nov": "11", "Dez": "12",
}

# (chave_no_html, chave_no_supabase) - ordem preservada para imitar o index.html
MAPS = {
    "instagram": [
        ("Alcance total (org+pago)", "Alcance total"),
        ("Alcance orgânico", "Alcance organico"),
        ("Alcance pago", "Alcance pago"),
        ("Engajamento total", "Engajamento total"),
        ("Novos seguidores", "Novos seguidores"),
        ("Seguidores totais", "Seguidores totais"),
        ("Visitas do perfil", "Visitas do perfil"),
        ("Visualizações totais", "Visualizacoes totais"),
        ("Postagens feed", "Postagens feed"),
        ("Curtidas em postagens", "Curtidas"),
        ("Comentários em postagens", "Comentarios"),
        ("Salvamentos", "Salvamentos"),
        ("Compartilhamentos", "Compartilhamentos"),
        ("Interações totais", "Interacoes totais"),
        ("Interações nas postagens", "Interacoes posts"),
        ("Alcance das postagens", "Alcance posts"),
        ("Número de Reels", "Num Reels"),
        ("Alcance dos Reels", "Alcance Reels"),
        ("Interações nos Reels", "Interacoes Reels"),
        ("Curtidas nos Reels", "Curtidas Reels"),
        ("Comentários nos Reels", "Comentarios Reels"),
        ("Salvamentos nos Reels", "Salvamentos Reels"),
        ("Compartilhamentos nos Reels", "Compartilhamentos Reels"),
        ("Número de Stories", "Num Stories"),
        ("Visualizações dos Stories", "Views Stories"),
        ("Interações com Stories", "Interacoes Stories"),
    ],
    "metaads": [
        ("Valor gasto (R$)", "Valor gasto"),
        ("Impressões", "Impressoes"),
        ("Alcance", "Alcance"),
        ("Cliques totais", "Cliques totais"),
        ("Cliques no link", "Cliques link"),
        ("Conversas iniciadas", "Conversas"),
        ("CTR (%)", "CTR"),
        ("CPC médio (R$)", "CPC"),
        ("CPM médio (R$)", "CPM"),
        ("Frequência", "Frequencia"),
        ("Leads", "Leads"),
        ("Custo por lead (R$)", "Custo por lead"),
        ("Custo por conversa (R$)", "Custo por conversa"),
        ("Alcance Facebook", "Alcance Facebook"),
        ("Alcance Instagram", "Alcance Instagram"),
        ("Investimento Facebook (R$)", "Investimento Facebook"),
        ("Investimento Instagram (R$)", "Investimento Instagram"),
    ],
    "gmn": [
        ("Total de ações", "Total acoes"),
        ("Cliques no website", "Cliques site"),
        ("Visualizações totais", "Visualizacoes"),
        ("Ligações", "Ligacoes"),
        ("Visualizações de pesquisa", "Views pesquisa"),
        ("Solicitações de rotas", "Rotas"),
        ("Visualizações no Maps", "Views Maps"),
        ('Pesquisas "laslo"', "Pesquisas marca"),
    ],
    "linkedin": [
        ("Seguidores totais", "Seguidores"),
        ("Novos seguidores", "Novos seguidores"),
        ("Alcance", "Alcance"),
        ("Impressões", "Impressoes"),
        ("Engajamento", "Engajamento"),
        ("Reações", "Reacoes"),
        ("Cliques", "Cliques"),
        ("Postagens", "Postagens"),
    ],
}


def js_val(v):
    """Converte valor Python para literal JS."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        # remove .0 desnecessário (ex: 5316.0 -> 5316)
        return str(int(v)) if v.is_integer() else str(v)
    return str(v)


def js_key(k):
    """Chave JS entre aspas simples (lida com aspas duplas internas)."""
    return "'" + k + "'"


def fetch_mes(data_iso):
    qs = urllib.parse.urlencode({
        "cliente_id": f"eq.{LASLO_ID}",
        "mes": f"eq.{data_iso}",
        "select": "dados_completos",
    })
    url = f"{SUPABASE_URL}/rest/v1/relatorios?{qs}"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data:
        return None
    return data[0].get("dados_completos") or {}


def gerar_bloco(label, dados):
    avisos = []
    linhas = [f"  '{label}': {{"]
    for plat in ("instagram", "metaads", "gmn", "linkedin"):
        plat_data = dados.get(plat, {})
        usados = set()
        campos = []
        for html_key, sb_key in MAPS[plat]:
            if sb_key in plat_data:
                usados.add(sb_key)
                val = plat_data[sb_key]
            else:
                val = None
                avisos.append(f"  [!] {plat}: campo '{sb_key}' não encontrado no Supabase (usei null)")
            campos.append(f"{js_key(html_key)}: {js_val(val)}")
        # campos no Supabase que não foram mapeados (informativo)
        extras = [k for k in plat_data.keys() if k not in usados]
        for ek in extras:
            avisos.append(f"  [i] {plat}: campo extra no Supabase ignorado: '{ek}'")
        # 3 campos por linha para legibilidade
        bloco_campos = ""
        for i in range(0, len(campos), 3):
            bloco_campos += "      " + ", ".join(campos[i:i+3]) + ",\n"
        linhas.append(f"    {plat}: {{")
        linhas.append(bloco_campos.rstrip("\n"))
        linhas.append("    },")
    linhas.append("  },")
    return "\n".join(linhas), avisos


def main():
    if len(sys.argv) != 2:
        print('Uso: python sync_kpi.py "Mes AAAA"   (ex: "Jun 2026")', file=sys.stderr)
        sys.exit(1)
    label = sys.argv[1].strip()
    partes = label.split()
    if len(partes) != 2 or partes[0] not in MESES:
        print(f"Mês inválido: '{label}'. Use formato como 'Jun 2026'.", file=sys.stderr)
        print(f"Meses válidos: {', '.join(MESES.keys())}", file=sys.stderr)
        sys.exit(1)
    mes_abbr, ano = partes
    data_iso = f"{ano}-{MESES[mes_abbr]}-01"

    print(f"Buscando {label} ({data_iso}) no Supabase...", file=sys.stderr)
    dados = fetch_mes(data_iso)
    if dados is None:
        print(f"Nenhum registro encontrado para {data_iso}. Atualize o Supabase primeiro.", file=sys.stderr)
        sys.exit(2)

    bloco, avisos = gerar_bloco(label, dados)

    if avisos:
        print("\n--- AVISOS (revise) ---", file=sys.stderr)
        for a in avisos:
            print(a, file=sys.stderr)
        print("-----------------------\n", file=sys.stderr)

    print(f"--- Cole este bloco dentro de KPI_ANALYTICS_DATA no index.html ---", file=sys.stderr)
    print(bloco)


if __name__ == "__main__":
    main()
