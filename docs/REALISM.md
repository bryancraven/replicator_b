# Realism Notes

This simulation is a **modular discrete-event scheduling / BOM skeleton**, not a closed-loop process-physics model. Use it for architecture, dependency, and scenario experiments—not for publishing quantitative claims about the true material or calendar cost of autonomous self-replication without further work.

Canonical prioritized backlog: **[MAJOR_FIXES.md](./MAJOR_FIXES.md)** (manufacturing + energy + logistics critiques).

## Honest inventory (as of 2026-09-12)

| Claim often seen in older docs | Actual |
|--------------------------------|--------|
| “250+ components” | **~144** `ResourceType` values in `factory_simulator/sim.py`; **~146** in `specs/default.spec` / bootstrap load |
| “16 specialized modules” | **14** entries in `MODULE_SPECS` (power/control appear as products, not always as runtime module specs) |
| “800–1200 days” replication | **Not reproduced** by a checked-in baseline run tied to current recipes |
| “2–3× more resources than simplified models” | **Narrative only** — no coded A/B baseline multiplier |

## What currently drives the clock

**Strong:** module occupancy, throughput/setup/batch limits, recipe dependency graph, (after P0) energy shortage and optional transport waits.  
**Weak / previously cosmetic:** AGV fleet realism, thermal headroom, waste recovery, learning curve, several `enable_*` flags. P0 work starts making energy, transport, and waste bind; see MAJOR_FIXES.

## Known limits (still open — see P1/P2)

- One-step “ore → pure Si / wafer / chip” abstractions understate fab and metallurgy.
- Recipe `energy_kwh` / `time_hours` often lose to module `power × throughput` timing.
- Process chemistry, UPW/gases, lithography, and metrology chains are thin or missing.
- Cleanroom particle model is not ISO-class physics.
- Solar/battery **nameplate growth** from produced panels/packs is not yet wired (P1-E5).
- Marketing timelines and resource multipliers remain unsupported.

## How to run a more honest scenario

```bash
# Bootstrap seed (few starter modules + seed inventory) — see specs/bootstrap.spec
python3 self_replicating_factory_sim.py --spec specs/bootstrap.spec --max-hours 500

# Minimal topology for fast CI / UI smoke
python3 self_replicating_factory_sim.py --spec specs/minimal.spec --max-hours 100
```

When changing recipes or energy/transport behavior, update **MAJOR_FIXES.md** status and this file’s inventory table.
