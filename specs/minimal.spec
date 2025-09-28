metadata:
  name: "Minimal Viable Self-Replicating Factory"
  version: "1.0.0"
  description: "Simplified factory with ~50 essential components for faster simulation"
  author: "Factory Simulation Team"

resources:
  # Raw materials
  IRON_ORE:
    density: 4.0
    storage_temp: 25
    contamination_sensitivity: 0.1
  SILICON_ORE:
    density: 2.3
    storage_temp: 25
    contamination_sensitivity: 0.1
  COPPER_ORE:
    density: 8.9
    storage_temp: 25
    contamination_sensitivity: 0.1

  # Refined materials
  STEEL:
    density: 7.8
    storage_temp: 25
    contamination_sensitivity: 0.1
  PURE_SILICON:
    density: 2.3
    storage_temp: 22
    contamination_sensitivity: 1.0
  COPPER_WIRE:
    density: 8.9
    storage_temp: 25
    contamination_sensitivity: 0.2
  GLASS:
    density: 2.5
    storage_temp: 25
    contamination_sensitivity: 0.3
  PLASTIC:
    density: 1.2
    storage_temp: 25
    contamination_sensitivity: 0.2

  # Electronic components
  SILICON_WAFER:
    density: 2.3
    storage_temp: 22
    contamination_sensitivity: 1.0
  INTEGRATED_CIRCUIT:
    density: 0.2
    storage_temp: 22
    contamination_sensitivity: 1.0
  CAPACITOR:
    density: 2.0
    storage_temp: 25
    contamination_sensitivity: 0.6
  RESISTOR:
    density: 2.0
    storage_temp: 25
    contamination_sensitivity: 0.5

  # Mechanical components
  BEARING:
    density: 7.8
    storage_temp: 25
    contamination_sensitivity: 0.3
  GEAR:
    density: 7.8
    storage_temp: 25
    contamination_sensitivity: 0.2
  ELECTRIC_MOTOR:
    density: 6.0
    storage_temp: 25
    contamination_sensitivity: 0.3

  # Power components
  SOLAR_CELL:
    density: 2.3
    storage_temp: 25
    contamination_sensitivity: 0.9
  BATTERY_CELL:
    density: 2.5
    storage_temp: 20
    contamination_sensitivity: 0.7
  INVERTER:
    density: 4.0
    storage_temp: 25
    contamination_sensitivity: 0.5

  # Assemblies
  CONTROL_BOARD:
    density: 2.0
    storage_temp: 22
    contamination_sensitivity: 0.8
  SOLAR_PANEL:
    density: 2.5
    storage_temp: 25
    contamination_sensitivity: 0.6
  BATTERY_PACK:
    density: 3.0
    storage_temp: 20
    contamination_sensitivity: 0.7
  ROBOTIC_ARM:
    density: 5.0
    storage_temp: 25
    contamination_sensitivity: 0.5

  # Factory modules
  MINING_MODULE:
    density: 10.0
    storage_temp: 25
    contamination_sensitivity: 0.1
  REFINING_MODULE:
    density: 12.0
    storage_temp: 25
    contamination_sensitivity: 0.2
  ELECTRONICS_MODULE:
    density: 8.0
    storage_temp: 22
    contamination_sensitivity: 0.8
  ASSEMBLY_MODULE:
    density: 8.0
    storage_temp: 25
    contamination_sensitivity: 0.4
  POWER_MODULE:
    density: 10.0
    storage_temp: 25
    contamination_sensitivity: 0.4

recipes:
  # Raw material extraction
  - output: IRON_ORE
    output_quantity: 1000
    inputs: {}
    energy_kwh: 40
    time_hours: 0.8
    required_module: mining

  - output: SILICON_ORE
    output_quantity: 1000
    inputs: {}
    energy_kwh: 50
    time_hours: 1.0
    required_module: mining

  - output: COPPER_ORE
    output_quantity: 1000
    inputs: {}
    energy_kwh: 60
    time_hours: 1.2
    required_module: mining

  # Material refinement
  - output: STEEL
    output_quantity: 500
    inputs:
      IRON_ORE: 600
    energy_kwh: 150
    time_hours: 1.5
    required_module: refining

  - output: PURE_SILICON
    output_quantity: 100
    inputs:
      SILICON_ORE: 500
    energy_kwh: 200
    time_hours: 2.0
    required_module: refining

  - output: COPPER_WIRE
    output_quantity: 200
    inputs:
      COPPER_ORE: 250
    energy_kwh: 80
    time_hours: 1.0
    required_module: refining

  - output: GLASS
    output_quantity: 100
    inputs:
      SILICON_ORE: 150
    energy_kwh: 80
    time_hours: 0.8
    required_module: refining

  - output: PLASTIC
    output_quantity: 100
    inputs:
      SILICON_ORE: 50
    energy_kwh: 60
    time_hours: 0.5
    required_module: refining

  # Electronic components
  - output: SILICON_WAFER
    output_quantity: 100
    inputs:
      PURE_SILICON: 10
    energy_kwh: 50
    time_hours: 0.5
    required_module: electronics

  - output: INTEGRATED_CIRCUIT
    output_quantity: 100
    inputs:
      SILICON_WAFER: 1
      COPPER_WIRE: 2
    energy_kwh: 100
    time_hours: 1.0
    required_module: electronics

  - output: CAPACITOR
    output_quantity: 1000
    inputs:
      STEEL: 2
      PLASTIC: 3
    energy_kwh: 30
    time_hours: 0.4
    required_module: electronics

  - output: RESISTOR
    output_quantity: 2000
    inputs:
      COPPER_WIRE: 1
      PLASTIC: 2
    energy_kwh: 20
    time_hours: 0.3
    required_module: electronics

  # Mechanical components
  - output: BEARING
    output_quantity: 100
    inputs:
      STEEL: 20
    energy_kwh: 30
    time_hours: 0.5
    required_module: assembly

  - output: GEAR
    output_quantity: 50
    inputs:
      STEEL: 30
    energy_kwh: 40
    time_hours: 0.8
    required_module: assembly

  - output: ELECTRIC_MOTOR
    output_quantity: 10
    inputs:
      COPPER_WIRE: 20
      STEEL: 10
      BEARING: 4
    energy_kwh: 100
    time_hours: 1.2
    required_module: assembly

  # Power components
  - output: SOLAR_CELL
    output_quantity: 100
    inputs:
      SILICON_WAFER: 10
      GLASS: 10
      COPPER_WIRE: 5
    energy_kwh: 120
    time_hours: 1.2
    required_module: electronics

  - output: BATTERY_CELL
    output_quantity: 100
    inputs:
      STEEL: 10
      COPPER_WIRE: 5
      PLASTIC: 10
    energy_kwh: 200
    time_hours: 2.0
    required_module: assembly

  - output: INVERTER
    output_quantity: 10
    inputs:
      INTEGRATED_CIRCUIT: 10
      CAPACITOR: 50
      STEEL: 5
    energy_kwh: 150
    time_hours: 2.0
    required_module: assembly

  # Assemblies
  - output: CONTROL_BOARD
    output_quantity: 10
    inputs:
      INTEGRATED_CIRCUIT: 5
      CAPACITOR: 50
      RESISTOR: 100
      COPPER_WIRE: 10
    energy_kwh: 150
    time_hours: 2.0
    required_module: assembly

  - output: SOLAR_PANEL
    output_quantity: 10
    inputs:
      SOLAR_CELL: 60
      GLASS: 50
      STEEL: 20
      PLASTIC: 30
    energy_kwh: 200
    time_hours: 2.0
    required_module: assembly

  - output: BATTERY_PACK
    output_quantity: 10
    inputs:
      BATTERY_CELL: 100
      PLASTIC: 50
      CONTROL_BOARD: 2
    energy_kwh: 300
    time_hours: 3.0
    required_module: assembly

  - output: ROBOTIC_ARM
    output_quantity: 1
    inputs:
      ELECTRIC_MOTOR: 6
      STEEL: 50
      CONTROL_BOARD: 2
      BEARING: 12
    energy_kwh: 400
    time_hours: 6.0
    required_module: assembly

  # Factory modules
  - output: MINING_MODULE
    output_quantity: 1
    inputs:
      ROBOTIC_ARM: 2
      CONTROL_BOARD: 5
      STEEL: 1000
      ELECTRIC_MOTOR: 10
    energy_kwh: 1500
    time_hours: 15.0
    required_module: assembly

  - output: REFINING_MODULE
    output_quantity: 1
    inputs:
      STEEL: 1500
      CONTROL_BOARD: 8
      ELECTRIC_MOTOR: 15
    energy_kwh: 2000
    time_hours: 20.0
    required_module: assembly

  - output: ELECTRONICS_MODULE
    output_quantity: 1
    inputs:
      ROBOTIC_ARM: 4
      CONTROL_BOARD: 10
      STEEL: 800
    energy_kwh: 2000
    time_hours: 20.0
    required_module: assembly

  - output: ASSEMBLY_MODULE
    output_quantity: 1
    inputs:
      ROBOTIC_ARM: 6
      CONTROL_BOARD: 15
      STEEL: 1200
      ELECTRIC_MOTOR: 20
    energy_kwh: 2500
    time_hours: 25.0
    required_module: assembly

  - output: POWER_MODULE
    output_quantity: 1
    inputs:
      SOLAR_PANEL: 50
      BATTERY_PACK: 20
      INVERTER: 10
      CONTROL_BOARD: 10
      COPPER_WIRE: 500
    energy_kwh: 3000
    time_hours: 30.0
    required_module: assembly

modules:
  mining:
    max_throughput: 20.0
    power_consumption_idle: 5.0
    power_consumption_active: 50.0
    mtbf_hours: 8000
    maintenance_interval: 1000
    degradation_rate: 0.01
    physical_footprint: 300
    max_batch_size: 200
    min_batch_size: 1
    setup_time: 0.3
    quality_base_rate: 0.99

  refining:
    max_throughput: 10.0
    power_consumption_idle: 10.0
    power_consumption_active: 100.0
    mtbf_hours: 6000
    maintenance_interval: 800
    degradation_rate: 0.02
    physical_footprint: 250
    max_batch_size: 100
    min_batch_size: 5
    setup_time: 1.0
    quality_base_rate: 0.97

  electronics:
    max_throughput: 2000.0
    power_consumption_idle: 15.0
    power_consumption_active: 60.0
    mtbf_hours: 5000
    maintenance_interval: 500
    degradation_rate: 0.02
    physical_footprint: 150
    max_batch_size: 20000
    min_batch_size: 100
    setup_time: 1.5
    quality_base_rate: 0.95

  assembly:
    max_throughput: 100.0
    power_consumption_idle: 10.0
    power_consumption_active: 40.0
    mtbf_hours: 6000
    maintenance_interval: 600
    degradation_rate: 0.02
    physical_footprint: 200
    max_batch_size: 200
    min_batch_size: 1
    setup_time: 1.0
    quality_base_rate: 0.98

initial_state:
  modules:
    mining: 1
    refining: 1
    electronics: 1
    assembly: 1
  resources: {}
  energy:
    solar_panels: 20
    battery_charge: 200

constraints:
  # Energy parameters
  initial_solar_capacity_kw: 200
  solar_panel_efficiency: 0.25
  battery_efficiency: 0.98

  # Processing multipliers
  mining_power_multiplier: 1.0
  processing_speed_multiplier: 1.2
  assembly_speed_multiplier: 1.2
  parallel_processing_limit: 5

  # Maintenance
  maintenance_interval_hours: 1000
  learning_curve_factor: 0.90
  redundancy_factor: 1.1

  # Features (simplified)
  enable_capacity_limits: true
  enable_degradation: false
  enable_quality_control: false
  enable_weather: false
  enable_maintenance: false
  enable_storage_limits: true
  enable_batch_processing: true
  enable_transport_time: false
  enable_contamination: false
  enable_thermal_management: false
  enable_software_production: false
  enable_waste_recycling: false

  # Physical constraints
  factory_area_m2: 10000
  max_storage_volume_m3: 10000
  max_storage_weight_tons: 5000

  # Environmental
  latitude: 35.0
  average_cloud_cover: 0.2
  ambient_temperature: 25

  # Quality targets
  target_quality_rate: 0.98
  cleanroom_class: 10000

subsystems:
  transport:
    enabled: false

  waste:
    enabled: false

  thermal:
    enabled: false

  software:
    enabled: false

  cleanroom:
    enabled: false

  storage:
    enabled: true
    max_storage_volume_m3: 10000
    max_storage_weight_tons: 5000
    enable_storage_limits: true

  energy:
    enabled: true
    initial_solar_capacity_kw: 200
    solar_panel_efficiency: 0.25
    battery_efficiency: 0.98
    enable_weather: false

profiles:
  fast_simulation:
    description: "Optimized for quick simulation runs"
    parallel_processing_limit: 10
    processing_speed_multiplier: 2.0
    assembly_speed_multiplier: 2.0
    initial_solar_capacity_kw: 500
    enable_degradation: false
    enable_maintenance: false

  realistic:
    description: "More realistic constraints"
    enable_degradation: true
    enable_quality_control: true
    enable_weather: true
    enable_maintenance: true
    target_quality_rate: 0.95
    learning_curve_factor: 0.95