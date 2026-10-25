"""Precios de la luz indexada con la API de tarifaelectrica.v2charge.com.

Requiere: pip install requests
Uso: python precios.py [2.0TD|3.0TD|6.1TD]
"""
import sys
import time

import requests

BASE = "https://tarifaelectrica.v2charge.com"
HEADERS = {"X-API-Key": "ejemplo-python"}  # identificador libre de tu integración


def get(path: str, **params) -> dict:
    """GET con un reintento si se supera el límite (30 peticiones por minuto)."""
    r = requests.get(BASE + path, params=params, headers=HEADERS, timeout=20)
    if r.status_code == 429:
        time.sleep(int(r.headers.get("Retry-After", 10)))
        r = requests.get(BASE + path, params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


def main() -> None:
    tariff = sys.argv[1] if len(sys.argv) > 1 else "2.0TD"
    day = get("/v1/prices", tariff=tariff)  # una sola petición para todo el día
    s = day["summary"]
    print(f"{day['date']} · {tariff}")
    print(f"  Media compra: {s['compra_media'] * 100:.1f} c€/kWh · venta: {s['venta_media'] * 100:.1f} c€/kWh")
    print(f"  Más barata: {s['compra_min']['ts_local'][11:16]} ({s['compra_min']['eur_kwh'] * 100:.1f} c€/kWh)")
    print(f"  Más cara:   {s['compra_max']['ts_local'][11:16]} ({s['compra_max']['eur_kwh'] * 100:.1f} c€/kWh)")
    print()
    for h in day["prices"]:
        bar = "█" * int(h["compra_eur_kwh"] * 100)
        mark = " *" if h["provisional"] else ""
        print(f"  {h['ts_local'][11:16]} {h['period']}  {h['compra_eur_kwh'] * 100:5.1f}{mark}  {bar}")
    if s["provisional"]:
        print("\n  * Provisional: definitivo a partir de las 21:00.")


if __name__ == "__main__":
    main()
