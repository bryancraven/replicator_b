# Major Fixes Backlog (Canonical)

Prioritized realism and correctness work merged from three critiques:

- **Manufacturing** — [bc-460067ec](https://cursor.com/agents/bc-460067ec-0e41-569d-b9bc-4e422054c97a)
- **Energy / solar** — [bc-0dd5219e](https://cursor.com/agents/bc-0dd5219e-d8ca-5510-94cf-de1582854e8f)
- **Logistics / ops** — [bc-398dae1f](https://cursor.com/agents/bc-398dae1f-2b77-5190-b6fc-f42ba5e5095b)

Status legend: `todo` | `doing` | `done`  
Owner areas: `sim` (engine), `recipes` (specs/BOM), `docs`

See also: [REALISM.md](./REALISM.md)

---

## P0 — Must fix for credible runs

| ID | Item | Source | Owner | Status | Notes |
|----|------|--------|-------|--------|-------|
| P0-M1 | Bootstrap / seed profile (not one-of-every-module) | mfg | recipes + sim | done | `specs/bootstrap.spec` + `seed_modules` / `bootstrap_mode` in CONFIG |
| P0-M2 | Fix wrong chemistry (acids, Pb/Sn precursors) | mfg | recipes + sim | done | Sulfur/salt/lead/tin ores; acid & metal recipes corrected |
| P0-E1 | Single energy ledger (no double-count) | energy | sim | done | Task start no longer deducts battery; step accounts continuous load |
| P0-E2 | HVAC / envelope cooling sized sanely | energy | sim | done | Conditioned fraction × W/m² instead of 0.1 kW/m² whole factory |
| P0-E3 | Unmet electrical load blocks work | energy | sim | done | Shortage pauses new starts / can block active path |
| P0-L1 | Transport gates production when enabled | logistics | sim | done | `awaiting_transport` until inbound jobs complete |
| P0-L2 | Waste recycling credits storage inventory | logistics | sim | done | Recovered mass added to `storage` |
| P0-D1 | Honest component / module counts in docs | mfg + docs | docs | done | ~140 resources, 14 module specs — not “250+” |

---

## P1 — High impact next

| ID | Item | Source | Owner | Status | Notes |
|----|------|--------|-------|--------|-------|
| P1-M3 | Multi-stage materials + realistic SEC (Si, Al, steel) | mfg | recipes | todo | Bayer/Hall–Héroult, MG-Si→poly→CZ, steel routes |
| P1-M4 | Fab abstraction fix (ICs ≠ discrete transistor BOM) | mfg | recipes | todo | Wafer process steps / mask sets, not PCB-style assembly |
| P1-M5 | Recipe energy/time authoritative (or drop vs module power) | mfg + energy | sim + recipes | todo | Unify `energy_kwh` with `power×time`; consistent units |
| P1-E4 | Battery C-rate, RT efficiency, health→capacity | energy | sim | todo | Apply cycle health to usable kWh; duration-aware C-rate |
| P1-E5 | Solar + battery capacity grow from produced assets | energy + mfg | sim | todo | Completing `SOLAR_*` / `BATTERY_*` bumps nameplate |
| P1-L3 | AGV maintenance recovery (escape maintenance state) | logistics | sim | doing | Was permanent stick; recovery timer added |
| P1-L4 | Honor `enable_*` flags in sim paths | logistics | sim | doing | transport / thermal / waste / quality gates wired for P0 paths |
| P1-L5 | Thermal that bites (capacity & temps matter) | logistics | sim | todo | Lower cooling headroom; use module temps |

---

## P2 — Depth / fidelity

| ID | Item | Source | Owner | Status | Notes |
|----|------|--------|-------|--------|-------|
| P2-M6 | Missing resources / process chemistry depth | mfg | recipes | todo | UPW, N₂/O₂/Ar/H₂, photoresist, CMP, dopants, refractories |
| P2-M7 | Tooling & metrology generation chain | mfg | recipes + sim | todo | Mother machines; fix CMM-on-assembly loophole |
| P2-M8 | Process waste mass balance (`waste_products`) | mfg | recipes + sim | todo | Populate recipe waste; slag/spent acid/scrap Si |
| P2-M9 | Credible cleanroom model + `cleanroom_capable` type | mfg | sim + recipes | todo | ISO limits; fix bool vs class int in specs |
| P2-M10 | Software as schedule + reliability bottleneck | mfg | sim + recipes | todo | Wire `software_required` onto equipment BOMs |
| P2-M11 | PV cell process + Li-ion electrode realism | mfg | recipes | todo | Beyond wafer+glass+Al+Cu cell BOM |
| P2-E6 | Clear-sky GHI, cloud autocorrelation, panel cleaning | energy | sim | todo | AM attenuation; reset dust on clean schedule |
| P2-E7 | Document or apply `solar_panel_efficiency` | energy | sim + docs | todo | Nameplate vs area×η honesty |
| P2-L6 | Learning curve / parallel_processing_limit actually used | logistics | sim | todo | Config exists; unused in timing today |

---

## Docs / claims hygiene

| ID | Item | Owner | Status | Notes |
|----|------|-------|--------|-------|
| DOC-1 | Replace “250+ components” with measured enum/spec counts | docs | done | README + CLAUDE/SPEC touchpoints |
| DOC-2 | Qualify “800–1200 days” / “2–3× resources” as unsupported | docs | todo | No reproducible baseline in-repo |
| DOC-3 | Keep REALISM.md + this backlog in sync after each P0/P1 land | docs | doing | Canonical pair |

---

## Implementation order (suggested)

1. **P0 ledger + HVAC + unmet load** — energy numbers become trustworthy  
2. **P0 transport gate + waste credit + enable flags** — ops constraints bite  
3. **P0 chemistry + bootstrap + honest docs** — BOM and narrative match code  
4. **P1 capacity growth + SEC/fab + battery health** — replication question becomes meaningful  
5. **P2 depth** — chemistry, cleanroom, software, metrology

---

## Change log

| Date | Change |
|------|--------|
| 2026-09-12 | Initial backlog merged from three critiques; P0 items implemented in engine/recipes/docs |
