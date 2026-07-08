# -*- coding: utf-8 -*-
"""Validador do agenda.json — rodar após qualquer edição: python3 check_agenda.py"""
import json, re, sys, datetime as dt
from collections import Counter, defaultdict

CAMADAS = {"contrato", "live", "reels", "evento"}
FORMATOS = {"feed", "story", "reel", "youtube", "evento"}

erros, avisos = [], []
try:
    itens = json.load(open("agenda.json", encoding="utf-8"))
except Exception as e:
    print(f"❌ JSON inválido: {e}"); sys.exit(1)

ids = Counter()
por_semana = defaultdict(int)
for i, it in enumerate(itens):
    ref = it.get("id", f"item #{i}")
    for campo in ("id", "data", "camada", "formato", "titulo"):
        if not it.get(campo):
            erros.append(f"{ref}: falta campo '{campo}'")
    try:
        d = dt.date.fromisoformat(it.get("data", ""))
    except ValueError:
        erros.append(f"{ref}: data inválida '{it.get('data')}'"); continue
    if it.get("camada") not in CAMADAS:
        erros.append(f"{ref}: camada inválida '{it.get('camada')}'")
    if it.get("formato") not in FORMATOS:
        erros.append(f"{ref}: formato inválido '{it.get('formato')}'")
    if it.get("hora") and not re.match(r"^\d{2}:\d{2}$", it["hora"]):
        erros.append(f"{ref}: hora inválida '{it['hora']}'")
    ids[it.get("id")] += 1
    if it.get("camada") == "contrato":
        semana = min((d.day - 1) // 7 + 1, 5)
        por_semana[(d.year, d.month, semana)] += 1

for id_, n in ids.items():
    if n > 1:
        erros.append(f"id duplicado: {id_} ({n}x)")

hoje = dt.date.today()
for (ano, mes, sem), n in sorted(por_semana.items()):
    if dt.date(ano, mes, min(sem*7, 28)) < hoje:
        continue  # semanas passadas não geram aviso
    if sem == 5:
        continue  # semana parcial (dias 29-31)
    if n != 2:
        avisos.append(f"⚠ {ano}-{mes:02d} S{sem}: {n} post(s) de contrato (contrato = 2/semana)")

print(f"{len(itens)} itens · {Counter(i['camada'] for i in itens)}")
for a in avisos: print(a)
if erros:
    print("\n❌ ERROS:"); [print(" ", e) for e in erros]; sys.exit(1)
print("✅ agenda.json válido")
