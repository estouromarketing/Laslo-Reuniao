#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_pauta.py - Sincroniza POSTS_DATA e DATES_DATA entre o index.html e CSVs editáveis.

Modos:
    python gen_pauta.py export   # extrai o estado ATUAL do index.html -> posts.csv + datas.csv
    python gen_pauta.py build    # lê posts.csv + datas.csv -> imprime os blocos JS pra colar

Fluxo de uso:
1. Rode `export` uma vez para gerar os CSVs a partir do que já está no HTML.
2. Depois, edite posts.csv / datas.csv (mais fácil que editar JS aninhado).
3. Rode `build`, copie os blocos e cole no index.html (substituindo POSTS_DATA / DATES_DATA).

posts.csv: Mês, Semana, Tema, ADS, Tipo   (Tipo: vazio | webinar | elastovet | petvet)
datas.csv: Mês, Data, Descrição
"""
import sys
import re
import csv
import ast
import io

HTML = "index.html"
POSTS_CSV = "posts.csv"
DATAS_CSV = "datas.csv"


def _extrai_objeto(texto, nome):
    """Extrai 'const NOME = { ... };' e devolve o dict via ast.literal_eval.
    Funciona porque POSTS_DATA/DATES_DATA só contêm strings (literais Python válidos)."""
    m = re.search(r"const\s+" + nome + r"\s*=\s*(\{.*?\n\});", texto, re.DOTALL)
    if not m:
        raise SystemExit(f"Não achei {nome} no {HTML}")
    return ast.literal_eval(m.group(1))


def export():
    with open(HTML, encoding="utf-8") as f:
        txt = f.read()

    posts = _extrai_objeto(txt, "POSTS_DATA")
    datas = _extrai_objeto(txt, "DATES_DATA")

    with open(POSTS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Mês", "Semana", "Tema", "ADS", "Tipo"])
        for mes, itens in posts.items():
            for it in itens:
                semana, tema, ads = it[0], it[1], it[2]
                tipo = it[3] if len(it) > 3 else ""
                w.writerow([mes, semana, tema, ads, tipo])

    with open(DATAS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Mês", "Data", "Descrição"])
        for mes, itens in datas.items():
            for it in itens:
                w.writerow([mes, it[0], it[1]])

    n_posts = sum(len(v) for v in posts.values())
    n_datas = sum(len(v) for v in datas.values())
    print(f"OK: {POSTS_CSV} ({n_posts} posts) e {DATAS_CSV} ({n_datas} datas) gerados.", file=sys.stderr)


def _js_str(s):
    """String JS com aspas simples, escapando apóstrofos internos."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _ler_csv_agrupado(path, n_cols):
    """Lê CSV e agrupa por Mês (1ª coluna), preservando ordem de aparição."""
    grupos = {}
    with open(path, encoding="utf-8") as f:
        r = csv.reader(f)
        next(r, None)  # header
        for row in r:
            if not row or not row[0].strip():
                continue
            mes = row[0]
            grupos.setdefault(mes, []).append(row[1:n_cols])
    return grupos


def build():
    # POSTS_DATA
    posts = _ler_csv_agrupado(POSTS_CSV, 5)  # Mês, Semana, Tema, ADS, Tipo
    out = io.StringIO()
    out.write("const POSTS_DATA = {\n")
    for mes, itens in posts.items():
        partes = []
        for it in itens:
            semana, tema, ads = it[0], it[1], it[2]
            tipo = it[3] if len(it) > 3 else ""
            campos = [_js_str(semana), _js_str(tema), _js_str(ads)]
            if tipo.strip():
                campos.append(_js_str(tipo))
            partes.append("[" + ",".join(campos) + "]")
        out.write(f"  {_js_str(mes)}: [" + ",".join(partes) + "],\n")
    out.write("};")
    print(out.getvalue())

    print("\n")  # separador

    # DATES_DATA
    datas = _ler_csv_agrupado(DATAS_CSV, 3)  # Mês, Data, Descrição
    out = io.StringIO()
    out.write("const DATES_DATA = {\n")
    for mes, itens in datas.items():
        partes = ["[" + _js_str(it[0]) + "," + _js_str(it[1]) + "]" for it in itens]
        out.write(f"  {_js_str(mes)}: [" + ",".join(partes) + "],\n")
    out.write("};")
    print(out.getvalue())


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("export", "build"):
        print("Uso: python gen_pauta.py [export|build]", file=sys.stderr)
        sys.exit(1)
    if sys.argv[1] == "export":
        export()
    else:
        build()


if __name__ == "__main__":
    main()
