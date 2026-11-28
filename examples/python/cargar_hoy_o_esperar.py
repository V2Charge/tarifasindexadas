"""¿Cargar hoy o esperar? Compara el coste de cargar X kWh en la franja más barata de cada uno de los próximos días,
con el precio oficial (hoy y mañana) y la previsión (días siguientes) de /v1/prices/forecast.

Requiere: pip install requests
Uso: python cargar_hoy_o_esperar.py [kWh] [potencia_kW] [tarifa] [días]
     python cargar_hoy_o_esperar.py 30 7.4 2.0TD 7
"""
import math
import sys
import time
from datetime import datetime, timezone

import requests

BASE = "https://electricityprices.v2charge.com"
HEADERS = {"X-API-Key": "ejemplo-carga"}  # identificador libre de tu integración


def get(path: str, **params) -> dict:
    """GET con un reintento si se supera el límite (30 peticiones por minuto)."""
    r = requests.get(BASE + path, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 429:
        time.sleep(int(r.headers.get("Retry-After", 10)))
        r = requests.get(BASE + path, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def best_block(prices: list[dict], hours: int) -> tuple[int, float, float]:
    """(índice de inicio, precio medio, precio medio "pesimista") de la franja contigua más barata del día."""
    best = None
    for i in range(len(prices) - hours + 1):
        block = prices[i:i + hours]
        avg = sum(p["compra_eur_kwh"] for p in block) / hours
        high = sum(p.get("rango_eur_kwh", [0, p["compra_eur_kwh"]])[1] for p in block) / hours
        if best is None or avg < best[1]:
            best = (i, avg, high)
    return best


def main() -> None:
    kwh = float(sys.argv[1]) if len(sys.argv) > 1 else 30
    power = float(sys.argv[2]) if len(sys.argv) > 2 else 7.4
    tariff = sys.argv[3] if len(sys.argv) > 3 else "2.0TD"
    days = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    hours = math.ceil(kwh / power)
    data = get("/v1/prices/forecast", tariff=tariff, days=days)  # una petición para toda la semana

    print(f"Cargar {kwh:g} kWh a {power:g} kW ({hours} h seguidas) · tarifa {tariff}\n")
    options = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for day in data["days"]:
        prices = [p for p in day["prices"] if p["ts_utc"] >= now[:14] + "00:00Z"]  # hoy: solo las horas que quedan
        if len(prices) < hours:
            continue
        i, avg, high = best_block(prices, hours)
        cost = kwh * avg
        kind = "previsión" if day["forecast"] else "oficial  "
        start = prices[i]["ts_local"][11:16]
        extra = f"  (hasta {kwh * high:5.2f} €)" if day["forecast"] else ""
        print(f"  {day['date']}  {kind}  desde las {start}  {avg * 100:5.1f} c€/kWh  →  {cost:5.2f} €{extra}")
        options.append((cost, day, start, high))

    if not options:
        print("Sin datos suficientes.")
        return
    today = options[0]
    best = min(options, key=lambda o: o[0])
    print()
    if best is today:
        print(f"→ Carga hoy desde las {today[2]}: es la opción más barata de los próximos {len(options)} días.")
    else:
        saving = today[0] - best[0]
        sure = kwh * best[3] < today[0]  # incluso en el extremo alto de la previsión sale más barato
        print(f"→ Espera al {best[1]['date']} desde las {best[2]}: ahorro estimado {saving:.2f} € frente a hoy"
              + ("." if sure else ", pero dentro del margen de error de la previsión."))
    print(f"\nPrevisión orientativa (oficial hasta {data['official_until']}). Fuente de la previsión: Red Eléctrica.")


if __name__ == "__main__":
    main()
