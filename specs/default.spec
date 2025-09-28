metadata:
  name: "Ultra-Realistic Self-Replicating Factory"
  version: "1.0.0"
  description: "Complete factory with 250+ components and 16 specialized modules"
  author: "Factory Simulation Team"

resources:
  # Raw materials (directly mined)
  SILICON_ORE:
    density: 2.3
    storage_temp: 25
    contamination_sensitivity: 0.1
  IRON_ORE:
    density: 4.0
    storage_temp: 25
    contamination_sensitivity: 0.1
  COPPER_ORE:
    density: 8.9
    storage_temp: 25
    contamination_sensitivity: 0.1
  ALUMINUM_ORE:
    density: 2.7
    storage_temp: 25
    contamination_sensitivity: 0.1
  LITHIUM_ORE:
    density: 0.5
    storage_temp: 25
    contamination_sensitivity: 0.2
  RARE_EARTH_ORE:
    density: 5.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  CARBON_ORE:
    density: 2.2
    storage_temp: 25
    contamination_sensitivity: 0.1

  # Chemical products
  SULFURIC_ACID:
    density: 1.8
    storage_temp: 15
    contamination_sensitivity: 0.5
    hazardous: true
  HYDROCHLORIC_ACID:
    density: 1.2
    storage_temp: 15
    contamination_sensitivity: 0.5
    hazardous: true
  SODIUM_HYDROXIDE:
    density: 2.1
    storage_temp: 20
    contamination_sensitivity: 0.4
    hazardous: true
  ORGANIC_SOLVENT:
    density: 0.8
    storage_temp: 10
    contamination_sensitivity: 0.6
    hazardous: true
  ELECTROLYTE_SOLUTION:
    density: 1.3
    storage_temp: 20
    contamination_sensitivity: 0.7
  POLYMER_RESIN:
    density: 1.2
    storage_temp: 25
    contamination_sensitivity: 0.3
  EPOXY:
    density: 1.1
    storage_temp: 20
    contamination_sensitivity: 0.4
  SILICONE:
    density: 1.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  LUBRICANT:
    density: 0.9
    storage_temp: 25
    contamination_sensitivity: 0.2
  COOLANT:
    density: 1.0
    storage_temp: 15
    contamination_sensitivity: 0.3
  CATALYST:
    density: 2.0
    storage_temp: 20
    contamination_sensitivity: 0.8

  # Refined materials
  PURE_SILICON:
    density: 2.3
    storage_temp: 22
    contamination_sensitivity: 1.0
  STEEL:
    density: 7.8
    storage_temp: 25
    contamination_sensitivity: 0.1
  COPPER_WIRE:
    density: 8.9
    storage_temp: 25
    contamination_sensitivity: 0.2
  ALUMINUM_SHEET:
    density: 2.7
    storage_temp: 25
    contamination_sensitivity: 0.1
  LITHIUM_COMPOUND:
    density: 1.5
    storage_temp: 20
    contamination_sensitivity: 0.8
  RARE_EARTH_MAGNETS:
    density: 7.5
    storage_temp: 25
    contamination_sensitivity: 0.6
  GLASS:
    density: 2.5
    storage_temp: 25
    contamination_sensitivity: 0.3
  PLASTIC:
    density: 1.2
    storage_temp: 25
    contamination_sensitivity: 0.2
    recyclable: true
  CARBON_FIBER:
    density: 1.8
    storage_temp: 25
    contamination_sensitivity: 0.4
  CERAMIC:
    density: 3.0
    storage_temp: 25
    contamination_sensitivity: 0.3

  # Precision mechanical components
  BEARING:
    density: 7.8
    storage_temp: 25
    contamination_sensitivity: 0.3
  PRECISION_BEARING:
    density: 7.8
    storage_temp: 22
    contamination_sensitivity: 0.6
  GEAR:
    density: 7.8
    storage_temp: 25
    contamination_sensitivity: 0.2
  BALL_SCREW:
    density: 7.8
    storage_temp: 22
    contamination_sensitivity: 0.7
  LINEAR_GUIDE:
    density: 7.8
    storage_temp: 22
    contamination_sensitivity: 0.6
  SPRING:
    density: 7.8
    storage_temp: 25
    contamination_sensitivity: 0.1
  DAMPER:
    density: 5.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  COUPLING:
    density: 7.0
    storage_temp: 25
    contamination_sensitivity: 0.2

  # Fasteners and seals
  BOLT:
    density: 7.8
    storage_temp: 25
    contamination_sensitivity: 0.1
  SCREW:
    density: 7.8
    storage_temp: 25
    contamination_sensitivity: 0.1
  WASHER:
    density: 7.8
    storage_temp: 25
    contamination_sensitivity: 0.1
  ORING:
    density: 1.5
    storage_temp: 25
    contamination_sensitivity: 0.4
  GASKET:
    density: 2.0
    storage_temp: 25
    contamination_sensitivity: 0.3

  # Electronic basics
  SILICON_WAFER:
    density: 2.3
    storage_temp: 22
    contamination_sensitivity: 1.0
  TRANSISTOR:
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
  INDUCTOR:
    density: 5.0
    storage_temp: 25
    contamination_sensitivity: 0.5
  DIODE:
    density: 2.0
    storage_temp: 25
    contamination_sensitivity: 0.7
  LED:
    density: 1.5
    storage_temp: 25
    contamination_sensitivity: 0.6

  # Electronic advanced
  INTEGRATED_CIRCUIT:
    density: 0.2
    storage_temp: 22
    contamination_sensitivity: 1.0
  MICROPROCESSOR:
    density: 0.2
    storage_temp: 22
    contamination_sensitivity: 1.0
  MEMORY_CHIP:
    density: 0.2
    storage_temp: 22
    contamination_sensitivity: 1.0
  POWER_REGULATOR:
    density: 3.0
    storage_temp: 25
    contamination_sensitivity: 0.5
  VOLTAGE_REGULATOR:
    density: 3.0
    storage_temp: 25
    contamination_sensitivity: 0.5
  CRYSTAL_OSCILLATOR:
    density: 4.0
    storage_temp: 22
    contamination_sensitivity: 0.8

  # Sensors
  THERMOCOUPLE:
    density: 8.0
    storage_temp: 25
    contamination_sensitivity: 0.4
  PRESSURE_TRANSDUCER:
    density: 4.0
    storage_temp: 25
    contamination_sensitivity: 0.6
  FLOW_METER:
    density: 3.0
    storage_temp: 25
    contamination_sensitivity: 0.5
  PROXIMITY_SENSOR:
    density: 2.0
    storage_temp: 25
    contamination_sensitivity: 0.6
  ENCODER:
    density: 2.5
    storage_temp: 25
    contamination_sensitivity: 0.7
  LOAD_CELL:
    density: 5.0
    storage_temp: 25
    contamination_sensitivity: 0.6
  CAMERA_MODULE:
    density: 1.5
    storage_temp: 25
    contamination_sensitivity: 0.8
  LIDAR:
    density: 2.0
    storage_temp: 22
    contamination_sensitivity: 0.9
  STRAIN_GAUGE:
    density: 0.5
    storage_temp: 25
    contamination_sensitivity: 0.8

  # Actuators and motors
  MOTOR_COIL:
    density: 8.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  ELECTRIC_MOTOR:
    density: 6.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  SERVO_MOTOR:
    density: 5.5
    storage_temp: 25
    contamination_sensitivity: 0.5
  STEPPER_MOTOR:
    density: 6.0
    storage_temp: 25
    contamination_sensitivity: 0.4
  LINEAR_ACTUATOR:
    density: 5.0
    storage_temp: 25
    contamination_sensitivity: 0.4
  PNEUMATIC_CYLINDER:
    density: 4.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  SOLENOID_VALVE:
    density: 4.5
    storage_temp: 25
    contamination_sensitivity: 0.4
  VALVE:
    density: 4.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  REFRIGERANT_CIRCUIT:
    density: 3.5
    storage_temp: 15
    contamination_sensitivity: 0.5

  # PCB and connections
  PCB_SUBSTRATE:
    density: 1.8
    storage_temp: 25
    contamination_sensitivity: 0.7
  SOLDER_PASTE:
    density: 9.0
    storage_temp: 15
    contamination_sensitivity: 0.8
  CONNECTOR:
    density: 3.0
    storage_temp: 25
    contamination_sensitivity: 0.5
  WIRE_HARNESS:
    density: 3.5
    storage_temp: 25
    contamination_sensitivity: 0.3
  LEAD:
    density: 11.3
    storage_temp: 25
    contamination_sensitivity: 0.3
    hazardous: true
  TIN:
    density: 7.3
    storage_temp: 25
    contamination_sensitivity: 0.3
  FLUX:
    density: 1.0
    storage_temp: 20
    contamination_sensitivity: 0.6

  # Power components
  BATTERY_CELL:
    density: 2.5
    storage_temp: 20
    contamination_sensitivity: 0.7
    hazardous: true
  SOLAR_CELL:
    density: 2.3
    storage_temp: 25
    contamination_sensitivity: 0.9
  TRANSFORMER:
    density: 7.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  INVERTER:
    density: 4.0
    storage_temp: 25
    contamination_sensitivity: 0.5

  # Thermal management
  HEAT_SINK:
    density: 2.7
    storage_temp: 25
    contamination_sensitivity: 0.2
  HEAT_EXCHANGER:
    density: 5.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  COOLING_FAN:
    density: 2.0
    storage_temp: 25
    contamination_sensitivity: 0.2
  RADIATOR:
    density: 3.0
    storage_temp: 25
    contamination_sensitivity: 0.2
  CHILLER_UNIT:
    density: 6.0
    storage_temp: 25
    contamination_sensitivity: 0.4

  # Chemical processing equipment
  REACTION_VESSEL:
    density: 7.0
    storage_temp: 25
    contamination_sensitivity: 0.5
  DISTILLATION_COLUMN:
    density: 6.5
    storage_temp: 25
    contamination_sensitivity: 0.6
  SEPARATION_MEMBRANE:
    density: 1.5
    storage_temp: 20
    contamination_sensitivity: 0.8
  CHEMICAL_PUMP:
    density: 5.0
    storage_temp: 25
    contamination_sensitivity: 0.3

  # Precision manufacturing
  CNC_SPINDLE:
    density: 6.0
    storage_temp: 25
    contamination_sensitivity: 0.7
  LASER_DIODE:
    density: 3.0
    storage_temp: 22
    contamination_sensitivity: 0.9
  FOCUSING_LENS:
    density: 4.0
    storage_temp: 22
    contamination_sensitivity: 0.9
  VACUUM_PUMP:
    density: 6.0
    storage_temp: 25
    contamination_sensitivity: 0.5
  MASS_FLOW_CONTROLLER:
    density: 3.0
    storage_temp: 25
    contamination_sensitivity: 0.8
  COMPRESSOR:
    density: 7.0
    storage_temp: 25
    contamination_sensitivity: 0.3

  # Testing equipment
  OSCILLOSCOPE:
    density: 3.0
    storage_temp: 22
    contamination_sensitivity: 0.6
  MULTIMETER:
    density: 1.5
    storage_temp: 25
    contamination_sensitivity: 0.5
  TENSILE_TESTER:
    density: 8.0
    storage_temp: 25
    contamination_sensitivity: 0.4
  CMM_PROBE:
    density: 4.0
    storage_temp: 22
    contamination_sensitivity: 0.9
  DISPLAY_PANEL:
    density: 2.0
    storage_temp: 25
    contamination_sensitivity: 0.7

  # Clean room equipment
  HEPA_FILTER:
    density: 0.5
    storage_temp: 25
    contamination_sensitivity: 0.7
  LAMINAR_FLOW_HOOD:
    density: 3.0
    storage_temp: 25
    contamination_sensitivity: 0.6
  PARTICLE_COUNTER:
    density: 2.0
    storage_temp: 25
    contamination_sensitivity: 0.8

  # Transport equipment
  CONVEYOR_BELT:
    density: 2.5
    storage_temp: 25
    contamination_sensitivity: 0.2
  CONVEYOR_MOTOR:
    density: 6.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  AGV_CHASSIS:
    density: 4.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  AGV_NAVIGATION:
    density: 2.0
    storage_temp: 25
    contamination_sensitivity: 0.7

  # Software/firmware
  PLC_PROGRAM:
    density: 0.0
    storage_temp: 25
    contamination_sensitivity: 0.0
    description: "Programmable Logic Controller software"
  ROBOT_FIRMWARE:
    density: 0.0
    storage_temp: 25
    contamination_sensitivity: 0.0
    description: "Robot control firmware"
  AI_MODEL:
    density: 0.0
    storage_temp: 25
    contamination_sensitivity: 0.0
    description: "Artificial intelligence model"
  SCADA_SYSTEM:
    density: 0.0
    storage_temp: 25
    contamination_sensitivity: 0.0
    description: "Supervisory Control and Data Acquisition system"

  # Recycling equipment
  SHREDDER:
    density: 7.0
    storage_temp: 25
    contamination_sensitivity: 0.2
  MAGNETIC_SEPARATOR:
    density: 6.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  OPTICAL_SORTER:
    density: 3.0
    storage_temp: 25
    contamination_sensitivity: 0.6

  # Advanced assemblies
  CONTROL_BOARD:
    density: 2.0
    storage_temp: 22
    contamination_sensitivity: 0.8
  ROBOTIC_ARM:
    density: 5.0
    storage_temp: 25
    contamination_sensitivity: 0.5
  CONVEYOR_SYSTEM:
    density: 4.0
    storage_temp: 25
    contamination_sensitivity: 0.3
  PRINTER_HEAD_3D:
    density: 3.0
    storage_temp: 25
    contamination_sensitivity: 0.7
  FURNACE_ELEMENT:
    density: 6.0
    storage_temp: 25
    contamination_sensitivity: 0.4
  SOLAR_PANEL:
    density: 2.5
    storage_temp: 25
    contamination_sensitivity: 0.6
  BATTERY_PACK:
    density: 3.0
    storage_temp: 20
    contamination_sensitivity: 0.7

  # Factory modules
  MINING_MODULE:
    density: 10.0
    storage_temp: 25
    contamination_sensitivity: 0.1
    description: "Complete mining module"
  REFINING_MODULE:
    density: 12.0
    storage_temp: 25
    contamination_sensitivity: 0.2
    description: "Material refining module"
  CHEMICAL_MODULE:
    density: 11.0
    storage_temp: 25
    contamination_sensitivity: 0.4
    description: "Chemical processing module"
  ELECTRONICS_MODULE:
    density: 8.0
    storage_temp: 22
    contamination_sensitivity: 0.8
    description: "Electronics fabrication module"
  MECHANICAL_MODULE:
    density: 10.0
    storage_temp: 25
    contamination_sensitivity: 0.3
    description: "Mechanical parts production module"
  CNC_MODULE:
    density: 9.0
    storage_temp: 25
    contamination_sensitivity: 0.5
    description: "CNC machining module"
  LASER_MODULE:
    density: 7.0
    storage_temp: 22
    contamination_sensitivity: 0.7
    description: "Laser cutting/welding module"
  ASSEMBLY_MODULE:
    density: 8.0
    storage_temp: 25
    contamination_sensitivity: 0.4
    description: "Assembly and integration module"
  SOFTWARE_MODULE:
    density: 5.0
    storage_temp: 22
    contamination_sensitivity: 0.6
    description: "Software development module"
  TRANSPORT_MODULE:
    density: 9.0
    storage_temp: 25
    contamination_sensitivity: 0.2
    description: "Material transport module"
  RECYCLING_MODULE:
    density: 10.0
    storage_temp: 25
    contamination_sensitivity: 0.3
    description: "Waste recycling module"
  TESTING_MODULE:
    density: 7.0
    storage_temp: 22
    contamination_sensitivity: 0.6
    description: "Quality testing module"
  CLEANROOM_MODULE:
    density: 6.0
    storage_temp: 22
    contamination_sensitivity: 0.9
    description: "Cleanroom fabrication module"
  THERMAL_MODULE:
    density: 8.0
    storage_temp: 25
    contamination_sensitivity: 0.3
    description: "Thermal management module"
  POWER_MODULE:
    density: 10.0
    storage_temp: 25
    contamination_sensitivity: 0.4
    description: "Power generation/distribution module"
  CONTROL_MODULE:
    density: 6.0
    storage_temp: 22
    contamination_sensitivity: 0.7
    description: "Central control module"

# Recipes section will be in a separate file due to size
# See default_recipes.yaml

modules:
  mining:
    max_throughput: 10.0
    power_consumption_idle: 5.0
    power_consumption_active: 50.0
    mtbf_hours: 5000
    maintenance_interval: 500
    degradation_rate: 0.02
    physical_footprint: 500
    max_batch_size: 100
    min_batch_size: 1
    setup_time: 0.5
    quality_base_rate: 0.98

  refining:
    max_throughput: 5.0
    power_consumption_idle: 10.0
    power_consumption_active: 100.0
    mtbf_hours: 4000
    maintenance_interval: 300
    degradation_rate: 0.03
    physical_footprint: 300
    max_batch_size: 50
    min_batch_size: 5
    setup_time: 2.0
    quality_base_rate: 0.95

  chemical:
    max_throughput: 2.0
    power_consumption_idle: 20.0
    power_consumption_active: 200.0
    mtbf_hours: 3000
    maintenance_interval: 400
    degradation_rate: 0.04
    physical_footprint: 250
    max_batch_size: 500
    min_batch_size: 50
    setup_time: 4.0
    quality_base_rate: 0.92

  electronics:
    max_throughput: 1000.0
    power_consumption_idle: 20.0
    power_consumption_active: 80.0
    mtbf_hours: 3000
    maintenance_interval: 200
    degradation_rate: 0.04
    physical_footprint: 200
    max_batch_size: 10000
    min_batch_size: 100
    setup_time: 3.0
    quality_base_rate: 0.90

  mechanical:
    max_throughput: 100.0
    power_consumption_idle: 15.0
    power_consumption_active: 60.0
    mtbf_hours: 4500
    maintenance_interval: 400
    degradation_rate: 0.025
    physical_footprint: 400
    max_batch_size: 500
    min_batch_size: 10
    setup_time: 1.5
    quality_base_rate: 0.97

  cnc:
    max_throughput: 20.0
    power_consumption_idle: 10.0
    power_consumption_active: 50.0
    mtbf_hours: 3000
    maintenance_interval: 100
    degradation_rate: 0.05
    physical_footprint: 100
    max_batch_size: 50
    min_batch_size: 1
    setup_time: 1.0
    quality_base_rate: 0.98
    tolerance_capability: 5.0

  laser:
    max_throughput: 50.0
    power_consumption_idle: 5.0
    power_consumption_active: 100.0
    mtbf_hours: 2000
    maintenance_interval: 200
    degradation_rate: 0.06
    physical_footprint: 80
    max_batch_size: 100
    min_batch_size: 1
    setup_time: 0.5
    quality_base_rate: 0.99
    tolerance_capability: 1.0

  cleanroom:
    max_throughput: 100.0
    power_consumption_idle: 50.0
    power_consumption_active: 150.0
    mtbf_hours: 5000
    maintenance_interval: 300
    degradation_rate: 0.02
    physical_footprint: 500
    max_batch_size: 1000
    min_batch_size: 10
    setup_time: 5.0
    quality_base_rate: 0.99
    cleanroom_capable: true

  assembly:
    max_throughput: 50.0
    power_consumption_idle: 10.0
    power_consumption_active: 40.0
    mtbf_hours: 4000
    maintenance_interval: 400
    degradation_rate: 0.03
    physical_footprint: 300
    max_batch_size: 100
    min_batch_size: 1
    setup_time: 2.0
    quality_base_rate: 0.96

  software:
    max_throughput: 10.0
    power_consumption_idle: 100.0
    power_consumption_active: 200.0
    mtbf_hours: 10000
    maintenance_interval: 1000
    degradation_rate: 0.01
    physical_footprint: 50
    max_batch_size: 10
    min_batch_size: 1
    setup_time: 0.1
    quality_base_rate: 0.85

  transport:
    max_throughput: 100.0
    power_consumption_idle: 5.0
    power_consumption_active: 20.0
    mtbf_hours: 6000
    maintenance_interval: 500
    degradation_rate: 0.02
    physical_footprint: 100
    max_batch_size: 1000
    min_batch_size: 1
    setup_time: 0.1
    quality_base_rate: 0.99

  recycling:
    max_throughput: 50.0
    power_consumption_idle: 20.0
    power_consumption_active: 100.0
    mtbf_hours: 3500
    maintenance_interval: 400
    degradation_rate: 0.035
    physical_footprint: 400
    max_batch_size: 500
    min_batch_size: 50
    setup_time: 3.0
    quality_base_rate: 0.90

  testing:
    max_throughput: 100.0
    power_consumption_idle: 10.0
    power_consumption_active: 30.0
    mtbf_hours: 5000
    maintenance_interval: 300
    degradation_rate: 0.02
    physical_footprint: 200
    max_batch_size: 100
    min_batch_size: 1
    setup_time: 1.0
    quality_base_rate: 0.99

  thermal:
    max_throughput: 1000.0
    power_consumption_idle: 50.0
    power_consumption_active: 200.0
    mtbf_hours: 4000
    maintenance_interval: 500
    degradation_rate: 0.03
    physical_footprint: 300
    max_batch_size: 1
    min_batch_size: 1
    setup_time: 0.1
    quality_base_rate: 0.98

initial_state:
  modules:
    mining: 1
    refining: 1
    chemical: 1
    electronics: 1
    mechanical: 1
    cnc: 1
    laser: 1
    cleanroom: 1
    assembly: 1
    software: 1
    transport: 1
    recycling: 1
    testing: 1
    thermal: 1
  resources: {}  # Start with no resources
  energy:
    solar_panels: 10
    battery_charge: 100

constraints:
  # Energy parameters
  initial_solar_capacity_kw: 100
  solar_panel_efficiency: 0.22
  battery_efficiency: 0.95

  # Processing multipliers
  mining_power_multiplier: 1.0
  processing_speed_multiplier: 1.0
  assembly_speed_multiplier: 1.0
  parallel_processing_limit: 10

  # Maintenance
  maintenance_interval_hours: 500
  learning_curve_factor: 0.95
  redundancy_factor: 1.2

  # Ultra-realistic features
  enable_capacity_limits: true
  enable_degradation: true
  enable_quality_control: true
  enable_weather: true
  enable_maintenance: true
  enable_storage_limits: true
  enable_batch_processing: true
  enable_transport_time: true
  enable_contamination: true
  enable_thermal_management: true
  enable_software_production: true
  enable_waste_recycling: true

  # Physical constraints
  factory_area_m2: 20000
  max_storage_volume_m3: 15000
  max_storage_weight_tons: 10000

  # Environmental
  latitude: 35.0
  average_cloud_cover: 0.3
  ambient_temperature: 25

  # Quality targets
  target_quality_rate: 0.95
  cleanroom_class: 1000

  # Transport
  agv_fleet_size: 10
  conveyor_length_m: 500

subsystems:
  transport:
    enabled: true
    agv_fleet_size: 10
    conveyor_length_m: 500
    enable_transport_time: true

  waste:
    enabled: true
    enable_waste_recycling: true
    recycling_efficiency: 0.75

  thermal:
    enabled: true
    ambient_temperature: 25
    enable_thermal_management: true

  software:
    enabled: true
    enable_software_production: true

  cleanroom:
    enabled: true
    cleanroom_class: 1000
    enable_contamination: true

  storage:
    enabled: true
    max_storage_volume_m3: 15000
    max_storage_weight_tons: 10000
    enable_storage_limits: true

  energy:
    enabled: true
    initial_solar_capacity_kw: 100
    solar_panel_efficiency: 0.22
    battery_efficiency: 0.95
    enable_weather: true
    latitude: 35.0
    average_cloud_cover: 0.3

profiles:
  high_throughput:
    description: "Optimized for maximum production rate"
    parallel_processing_limit: 20
    processing_speed_multiplier: 1.5
    assembly_speed_multiplier: 1.5
    agv_fleet_size: 20
    initial_solar_capacity_kw: 500

  energy_efficient:
    description: "Minimized energy consumption"
    processing_speed_multiplier: 0.8
    assembly_speed_multiplier: 0.8
    solar_panel_efficiency: 0.25
    battery_efficiency: 0.98

  high_quality:
    description: "Maximum quality and reliability"
    target_quality_rate: 0.99
    cleanroom_class: 100
    enable_quality_control: true
    learning_curve_factor: 0.90

  experimental:
    description: "Advanced AI-driven subsystems with genetic algorithms and smart grid"
    # Enable advanced subsystems for this profile
    subsystem_implementations:
      transport: "genetic_routing"
      energy: "smart_grid"
      quality_control: "spc_quality"
      maintenance: "predictive_maintenance"
    # Enhanced performance parameters
    parallel_processing_limit: 25
    processing_speed_multiplier: 1.3
    initial_solar_capacity_kw: 300
    # Advanced subsystem configurations
    subsystem_data:
      transport:
        population_size: 100
        mutation_rate: 0.15
        crossover_rate: 0.7
        selection_pressure: 2.0
      energy:
        grid_connection: true
        battery_strategy: "economic"
        demand_response: true
        renewable_forecasting: true
      quality_control:
        control_limits_sigma: 3.0
        sample_size: 10
        alert_threshold: 0.05
      maintenance:
        prediction_horizon_hours: 168
        alert_threshold: 0.8
        enable_prognostics: true

# Recipes are in default_recipes.yaml - loaded automatically
recipes_file: default_recipes.yaml

# Subsystem implementations for modular architecture
# Uses standard wrappers for core systems with optional advanced subsystems
subsystem_implementations:
  transport: "transport_wrapper"
  waste: "waste_wrapper"
  thermal: "thermal_wrapper"
  software: "software_wrapper"
  cleanroom: "cleanroom_wrapper"
  storage: "storage_wrapper"
  energy: "energy_wrapper"
  # Optional: advanced subsystems (commented out by default)
  # predictive_maintenance: "predictive_maintenance"
  # quality_control: "spc_quality"

# Configuration data for subsystems when using modular mode
subsystem_data:
  transport:
    # Standard transport configuration
    agv_fleet_size: 10
    routing_algorithm: "dijkstra"
    enable_transport_time: true

  waste:
    # Waste management configuration
    enable_waste_recycling: true
    recycling_efficiency: 0.75

  thermal:
    # Thermal management configuration
    ambient_temperature: 25
    enable_thermal_management: true

  software:
    # Software production configuration
    enable_software_production: true
    bug_rate_base: 0.05

  cleanroom:
    # Cleanroom configuration
    cleanroom_class: 1000
    enable_contamination: true

  storage:
    # Storage system configuration
    max_storage_volume_m3: 15000
    max_storage_weight_tons: 10000
    enable_storage_limits: true

  energy:
    # Energy system configuration
    initial_solar_capacity_kw: 100
    solar_panel_efficiency: 0.22
    battery_efficiency: 0.95
    enable_weather: true
    latitude: 35.0
    average_cloud_cover: 0.3