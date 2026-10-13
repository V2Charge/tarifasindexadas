// Mejor franja para cargar mañana (o hoy si mañana aún no está publicado).
// Node 18+:  node precios.mjs 2.0TD 3
const BASE = "https://tarifaelectrica.v2charge.com";
const tariff = process.argv[2] ?? "2.0TD";
const hours = Number(process.argv[3] ?? 3);

async function get(path) {
  let r = await fetch(BASE + path, { headers: { "X-API-Key": "ejemplo-js" } });
  if (r.status === 429) {
    await new Promise((ok) => setTimeout(ok, 1000 * Number(r.headers.get("Retry-After") ?? 10)));
    r = await fetch(BASE + path, { headers: { "X-API-Key": "ejemplo-js" } });
  }
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}

const data = await get(`/v1/prices/cheapest?tariff=${tariff}&n=${hours}&block=${hours}`);
const b = data.best_block;
console.log(`${data.date} · ${tariff}${data.provisional ? " (provisional)" : ""}`);
console.log(`Mejor franja de ${hours} h: ${b.from.slice(11, 16)} → ${b.to.slice(11, 16)} (fin +1 h), ` +
            `media ${(b.avg_eur_kwh * 100).toFixed(1)} c€/kWh`);
console.log("Horas más baratas:", data.cheapest_hours.map((h) => h.ts_local.slice(11, 16)).join(", "));
