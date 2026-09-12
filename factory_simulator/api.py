"""
Research API — shared facade for CLI and Streamlit lab.

One replication engine (classic Factory). Modular/hybrid paths wrap that engine.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .spec_loader import SpecLoader, SpecRegistry

ProgressCallback = Callable[[Dict[str, Any]], None]


@dataclass
class Scenario:
    """Loaded scenario ready to run."""

    spec_path: str
    profile: Optional[str]
    config: Dict[str, Any]
    recipes: Dict[str, Any]
    module_specs: Dict[str, Any]
    resource_enum: Any
    spec_dict: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    subsystem_implementations: Dict[str, str] = field(default_factory=dict)
    name: str = ""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _specs_dir() -> Path:
    return _repo_root() / "specs"


def list_specs(specs_dir: Optional[Union[str, Path]] = None) -> List[Dict[str, str]]:
    """List available factory specs with basic metadata."""
    directory = Path(specs_dir) if specs_dir else _specs_dir()
    if not directory.exists():
        return []
    registry = SpecRegistry(str(directory))
    results: List[Dict[str, str]] = []
    for name in sorted(registry.list_specs()):
        rel = registry.available_specs.get(name, name)
        path = directory / rel
        description = ""
        try:
            description = registry.get_description(name) or ""
        except Exception:
            description = ""
        results.append({
            "name": name,
            "path": str(path),
            "description": description,
        })
    return results


def resolve_spec_path(spec: Union[str, Path]) -> Path:
    """Resolve a spec name or path to an existing file."""
    path = Path(spec)
    if path.exists():
        return path
    # Try under specs/
    candidate = _specs_dir() / spec
    if candidate.exists():
        return candidate
    # Try with common extensions
    for ext in ("", ".json", ".spec", ".yaml", ".yml"):
        candidate = _specs_dir() / f"{spec}{ext}" if not spec.endswith(ext) else _specs_dir() / spec
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Spec not found: {spec}")


def load_scenario(
    spec: Union[str, Path],
    profile: Optional[str] = None,
) -> Scenario:
    """Load a factory scenario from a spec file."""
    spec_path = resolve_spec_path(spec)
    loader = SpecLoader()
    loaded = loader.load_spec(str(spec_path))
    resource_enum = loader.create_resource_enum(loaded)
    recipes = loader.create_recipes(loaded, resource_enum)
    module_specs = loader.create_module_specs(loaded)
    config = loader.create_config(loaded, profile)
    spec_dict = {
        "subsystem_data": loaded.subsystem_data,
        "resources": loaded.resources,
        "target_modules": loaded.target_modules,
    }
    return Scenario(
        spec_path=str(spec_path),
        profile=profile,
        config=config,
        recipes=recipes,
        module_specs=module_specs,
        resource_enum=resource_enum,
        spec_dict=spec_dict,
        metadata=dict(loaded.metadata or {}),
        subsystem_implementations=dict(loaded.subsystem_implementations or {}),
        name=loaded.metadata.get("name", spec_path.stem) if loaded.metadata else spec_path.stem,
    )


def run_scenario(
    spec: Optional[Union[str, Path]] = None,
    profile: Optional[str] = None,
    max_hours: float = 10000,
    modular: bool = False,
    output: Optional[Union[str, Path]] = None,
    progress_cb: Optional[ProgressCallback] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
    max_wall_time_seconds: float = 3600,
) -> Dict[str, Any]:
    """
    Run a replication scenario and return the result dict.

    Args:
        spec: Spec path or name (None = built-in CONFIG / ResourceType)
        profile: Optional profile from the spec
        max_hours: Simulation time limit
        modular: If True, run hybrid Factory with modular plugins
        output: Optional path to write JSON results
        progress_cb: Optional callback receiving progress dicts
        config_overrides: Dict merged into config (solar kW, toggles, etc.)
        max_wall_time_seconds: Wall-clock timeout
    """
    from .sim import Factory, CONFIG, RECIPES, MODULE_SPECS

    scenario: Optional[Scenario] = None
    if spec is not None:
        scenario = load_scenario(spec, profile)
        config = dict(scenario.config)
        recipes = scenario.recipes
        module_specs = scenario.module_specs
        resource_enum = scenario.resource_enum
        spec_dict = scenario.spec_dict
    else:
        config = dict(CONFIG)
        recipes = RECIPES
        module_specs = MODULE_SPECS
        resource_enum = None
        spec_dict = None

    if config_overrides:
        config.update(config_overrides)

    if progress_cb:
        progress_cb({
            "phase": "starting",
            "spec": scenario.spec_path if scenario else None,
            "max_hours": max_hours,
            "modular": modular,
        })

    if modular:
        from .factory_builder import create_factory_from_spec
        from .modular_factory_adapter import ModularFactoryBridge
        from .modular_framework import UpdateStrategy

        if scenario is not None:
            runner = create_factory_from_spec(
                scenario.spec_path,
                profile=profile,
                update_strategy=UpdateStrategy.SEQUENTIAL,
            )
            # Apply overrides onto hybrid engine config when possible
            if config_overrides and runner.hybrid_factory is not None:
                runner.hybrid_factory.config.update(config_overrides)
            results = runner.run_simulation(
                max_hours=max_hours,
                max_wall_time_seconds=max_wall_time_seconds,
            )
        else:
            bridge = ModularFactoryBridge(config=config)
            factory = bridge.create_hybrid_factory()
            results = factory.run_simulation(
                max_hours=max_hours,
                max_wall_time_seconds=max_wall_time_seconds,
            )
    else:
        factory = Factory(config, spec_dict=spec_dict, resource_enum=resource_enum)
        # Keep recipe tables aligned when loaded from spec
        if scenario is not None:
            # Module-level recipes are used deep in Factory; also store on instance
            factory.recipes = recipes  # type: ignore
            factory.module_specs = module_specs  # type: ignore
        results = factory.run_simulation(
            max_hours=max_hours,
            max_wall_time_seconds=max_wall_time_seconds,
        )

    if progress_cb and results:
        final = results.get("final_status", {})
        progress_cb({
            "phase": "complete",
            "time": final.get("time"),
            "completed_tasks": final.get("completed_tasks"),
            "blocked_tasks": final.get("blocked_tasks"),
        })

    if output and results:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(results, f, default=str)

    return results or {}


def summarize_run(source: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize a run result dict or JSON log path for UI/CLI."""
    data = _load_run(source)
    final = data.get("final_status", {}) or {}
    config = data.get("config", {}) or {}
    metrics = data.get("metrics", {}) or {}
    log_entries = data.get("log_entries", []) or []

    time_hours = float(final.get("time") or 0)
    completed = int(final.get("completed_tasks") or 0)
    blocked = int(final.get("blocked_tasks") or 0)
    modules = final.get("modules") or {}

    blockers = _extract_blockers(log_entries, data)
    energy = _extract_energy(metrics, final)

    replicated = False
    if modules:
        replicated = all(int(v or 0) > 0 for v in modules.values()) and blocked == 0

    status = "replicated" if replicated else (
        "blocked" if blocked > 0 else (
            "partial" if completed > 0 else "failed"
        )
    )

    return {
        "status": status,
        "time_hours": time_hours,
        "time_days": time_hours / 24.0,
        "completed_tasks": completed,
        "blocked_tasks": blocked,
        "active_tasks": int(final.get("active_tasks") or 0),
        "modules": modules,
        "module_count": sum(1 for v in modules.values() if int(v or 0) > 0),
        "waste_total": final.get("waste_total"),
        "transport_completed": final.get("transport_completed"),
        "software_packages": final.get("software_packages"),
        "energy": energy,
        "top_blockers": blockers[:10],
        "config_highlights": {
            "initial_solar_capacity_kw": config.get("initial_solar_capacity_kw"),
            "parallel_processing_limit": config.get("parallel_processing_limit"),
            "enable_degradation": config.get("enable_degradation"),
            "enable_weather": config.get("enable_weather"),
        },
    }


def compare_runs(
    a: Union[str, Path, Dict[str, Any]],
    b: Union[str, Path, Dict[str, Any]],
) -> Dict[str, Any]:
    """Compare two runs and return a delta summary."""
    sa = summarize_run(a)
    sb = summarize_run(b)

    def _delta(key: str) -> Optional[float]:
        va, vb = sa.get(key), sb.get(key)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            return float(vb) - float(va)
        return None

    blocker_a = {b["reason"]: b["count"] for b in sa.get("top_blockers", [])}
    blocker_b = {b["reason"]: b["count"] for b in sb.get("top_blockers", [])}
    all_reasons = sorted(set(blocker_a) | set(blocker_b))
    blocker_delta = {
        reason: blocker_b.get(reason, 0) - blocker_a.get(reason, 0)
        for reason in all_reasons
    }

    return {
        "a": sa,
        "b": sb,
        "deltas": {
            "time_hours": _delta("time_hours"),
            "time_days": _delta("time_days"),
            "completed_tasks": _delta("completed_tasks"),
            "blocked_tasks": _delta("blocked_tasks"),
            "module_count": _delta("module_count"),
        },
        "blocker_delta": blocker_delta,
        "faster": (
            "a" if (sa.get("time_hours") or 0) < (sb.get("time_hours") or 0)
            else "b" if (sb.get("time_hours") or 0) < (sa.get("time_hours") or 0)
            else "tie"
        ),
    }


def _load_run(source: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    if isinstance(source, dict):
        return source
    path = Path(source)
    with open(path) as f:
        return json.load(f)


def _extract_blockers(log_entries: List[Dict], data: Dict[str, Any]) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    # Prefer structured blocked task info if present
    for entry in log_entries:
        msg = str(entry.get("message", "")).lower()
        if "blocked" not in msg:
            continue
        reason = "blocked"
        for key in (
            "blocked_energy",
            "blocked_resources",
            "blocked_module",
            "blocked_transport",
            "blocked_thermal",
            "blocked_software",
        ):
            if key in msg:
                reason = key
                break
        counts[reason] = counts.get(reason, 0) + 1

    # Also scan completed/blocked task statuses in metrics snapshots if available
    final = data.get("final_status") or {}
    if not counts and final.get("blocked_tasks"):
        counts["blocked"] = int(final["blocked_tasks"])

    return [
        {"reason": reason, "count": count}
        for reason, count in sorted(counts.items(), key=lambda x: -x[1])
    ]


def _extract_energy(metrics: Dict[str, Any], final: Dict[str, Any]) -> Dict[str, Any]:
    battery = metrics.get("battery_charge") or []
    solar = metrics.get("solar_generation") or metrics.get("energy_generated") or []
    return {
        "final_battery_kwh": battery[-1] if battery else None,
        "min_battery_kwh": min(battery) if battery else None,
        "max_battery_kwh": max(battery) if battery else None,
        "avg_solar_kw": (sum(solar) / len(solar)) if solar else None,
        "samples": len(battery) or len(solar),
    }
