#!/usr/bin/env sh
# Ejemplos de la API de tarifas indexadas. Límite: 30 peticiones por minuto por IP.
BASE="https://tarifaelectrica.v2charge.com"

# ¿Están publicados los precios de mañana? ¿Son definitivos?
curl -s "$BASE/v1/status"

# Precio de la hora actual en 2.0TD
curl -s "$BASE/v1/prices/now?tariff=2.0TD"

# Precios de mañana en 3.0TD (404 antes de las ~13:00)
curl -s "$BASE/v1/prices/tomorrow?tariff=3.0TD"

# Las 4 horas más baratas y la mejor franja de 3 horas
curl -s "$BASE/v1/prices/cheapest?tariff=2.0TD&n=4&block=3"

# Formato por fecha (medias diarias del mes, 6.1TD)
curl -s "$BASE/mi-instalacion/indexada/2026-10/6/"
