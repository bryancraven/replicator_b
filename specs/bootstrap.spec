metadata:
  name: "Bootstrap Seed Factory"
  version: "1.0.0"
  description: "Honest bootstrap profile — few starter modules + seed inventory; advanced modules must be produced"
  author: "Factory Simulation Team"
  parent: "default.spec"

# Keep parent resources/recipes/modules; override only start conditions & energy
initial_state:
  modules:
    mining: 1
    refining: 1
    mechanical: 1
    assembly: 1
    transport: 1
  resources:
    IRON_ORE: 2000
    SILICON_ORE: 2000
    COPPER_ORE: 1000
    CARBON_ORE: 500
    SULFUR_ORE: 200
    SALT: 300
    WATER: 2000
    STEEL: 100
  energy:
    solar_panels: 40
    battery_charge: 1000

constraints:
  bootstrap_mode: true
  seed_modules:
    - mining
    - refining
    - mechanical
    - assembly
    - transport
  seed_resources:
    IRON_ORE: 2000
    SILICON_ORE: 2000
    COPPER_ORE: 1000
    CARBON_ORE: 500
    SULFUR_ORE: 200
    SALT: 300
    WATER: 2000
    STEEL: 100
  require_transport_completion: true
  initial_solar_capacity_kw: 400
  battery_capacity_kwh: 2000
  battery_c_rate: 0.5
  conditioned_floor_fraction: 0.35
  hvac_specific_w_per_m2: 25.0
  process_heat_hvac_fraction: 0.0
  enable_transport_time: true
  enable_thermal_management: true
  enable_waste_recycling: true
  enable_weather: true

profiles:
  harsh_bootstrap:
    initial_solar_capacity_kw: 250
    battery_capacity_kwh: 1200
    seed_resources:
      IRON_ORE: 500
      SILICON_ORE: 500
      WATER: 500
