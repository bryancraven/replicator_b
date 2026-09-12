#!/usr/bin/env python3
"""
Visualization module for self-replicating factory system.
Generates intuitive flow diagrams showing material flow through production stages.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np
from enum import Enum

try:
    # Prefer the live simulation enum so diagrams match the engine
    from .sim import ResourceType as _SimResourceType
    ResourceType = _SimResourceType
except Exception:  # pragma: no cover - fallback for partial installs
    class ResourceType(Enum):
        """Fallback resource types when sim import is unavailable"""
        SILICON_ORE = "silicon_ore"
        IRON_ORE = "iron_ore"
        COPPER_ORE = "copper_ore"
        ALUMINUM_ORE = "aluminum_ore"
        LITHIUM_ORE = "lithium_ore"
        RARE_EARTH_ORE = "rare_earth_ore"
        PURE_SILICON = "pure_silicon"
        STEEL = "steel"
        COPPER_WIRE = "copper_wire"
        ALUMINUM_SHEET = "aluminum_sheet"
        LITHIUM_COMPOUND = "lithium_compound"
        RARE_EARTH_MAGNETS = "rare_earth_magnets"
        GLASS = "glass"
        PLASTIC = "plastic"
        SILICON_WAFER = "silicon_wafer"
        TRANSISTOR = "transistor"
        CAPACITOR = "capacitor"
        RESISTOR = "resistor"
        LED = "led"
        BEARING = "bearing"
        GEAR = "gear"
        MOTOR_COIL = "motor_coil"
        INTEGRATED_CIRCUIT = "integrated_circuit"
        MICROPROCESSOR = "microprocessor"
        MEMORY_CHIP = "memory_chip"
        POWER_REGULATOR = "power_regulator"
        SENSOR = "sensor"
        ACTUATOR = "actuator"
        ELECTRIC_MOTOR = "electric_motor"
        BATTERY_CELL = "battery_cell"
        DISPLAY_PANEL = "display_panel"
        SOLAR_CELL = "solar_cell"
        SOLAR_PANEL = "solar_panel"
        BATTERY_PACK = "battery_pack"
        CONTROL_BOARD = "control_board"
        ROBOTIC_ARM = "robotic_arm"
        CONVEYOR_SYSTEM = "conveyor_system"
        THREE_D_PRINTER_HEAD = "3d_printer_head"
        FURNACE_ELEMENT = "furnace_element"
        MINING_MODULE = "mining_module"
        REFINING_MODULE = "refining_module"
        ELECTRONICS_MODULE = "electronics_module"
        MECHANICAL_MODULE = "mechanical_module"
        ASSEMBLY_MODULE = "assembly_module"
        POWER_MODULE = "power_module"
        CONTROL_MODULE = "control_module"
        FACTORY = "factory"

class FactoryVisualizer:
    """Generates system schematic diagrams for factory simulation"""

    def __init__(self):
        # Define component hierarchy levels
        self.levels = {
            0: "Raw Materials",
            1: "Refined Materials",
            2: "Basic Components",
            3: "Intermediate Components",
            4: "Advanced Components",
            5: "Factory Modules",
            6: "Complete Factory"
        }

        def _rt(*names):
            """Resolve ResourceType members that exist in the live enum."""
            out = []
            for name in names:
                member = getattr(ResourceType, name, None)
                if member is not None:
                    out.append(member)
            return out

        # Map resource types to levels (only members present in ResourceType)
        level_names = {
            0: [
                "SILICON_ORE", "IRON_ORE", "COPPER_ORE", "ALUMINUM_ORE",
                "LITHIUM_ORE", "RARE_EARTH_ORE", "CARBON_ORE", "WATER",
            ],
            1: [
                "PURE_SILICON", "STEEL", "COPPER_WIRE", "ALUMINUM_SHEET",
                "LITHIUM_COMPOUND", "RARE_EARTH_MAGNETS", "GLASS", "PLASTIC",
            ],
            2: [
                "SILICON_WAFER", "TRANSISTOR", "CAPACITOR", "RESISTOR", "LED",
                "BEARING", "GEAR", "MOTOR_COIL",
            ],
            3: [
                "INTEGRATED_CIRCUIT", "MICROPROCESSOR", "MEMORY_CHIP",
                "POWER_REGULATOR", "ELECTRIC_MOTOR", "BATTERY_CELL",
                "DISPLAY_PANEL", "PROXIMITY_SENSOR", "LINEAR_ACTUATOR",
            ],
            4: [
                "SOLAR_CELL", "SOLAR_PANEL", "BATTERY_PACK", "CONTROL_BOARD",
                "ROBOTIC_ARM", "CONVEYOR_SYSTEM", "FURNACE_ELEMENT",
            ],
            5: [
                "MINING_MODULE", "REFINING_MODULE", "ELECTRONICS_MODULE",
                "MECHANICAL_MODULE", "ASSEMBLY_MODULE", "POWER_MODULE",
                "CONTROL_MODULE", "CHEMICAL_MODULE", "CNC_MODULE",
                "SOFTWARE_MODULE", "TRANSPORT_MODULE",
            ],
            6: ["FACTORY"],
        }
        self.resource_levels = {}
        for level, names in level_names.items():
            for member in _rt(*names):
                self.resource_levels[member] = level

        # Color scheme for different levels
        self.level_colors = {
            0: '#8B4513',  # Brown for raw materials
            1: '#4682B4',  # Steel blue for refined
            2: '#32CD32',  # Lime green for basic
            3: '#FFD700',  # Gold for intermediate
            4: '#FF6347',  # Tomato for advanced
            5: '#9370DB',  # Medium purple for modules
            6: '#FF1493'   # Deep pink for factory
        }

        # Module colors
        self.module_colors = {
            'mining': '#8B4513',
            'refining': '#4682B4',
            'electronics': '#FFD700',
            'mechanical': '#708090',
            'assembly': '#FF6347',
            'power': '#32CD32',
            'control': '#9370DB'
        }

        # Load recipes to understand dependencies
        self.load_recipes()

    def load_recipes(self):
        """Load production recipes to understand material flow"""
        self.dependencies = {}

        def add(output_name, *input_names):
            out = getattr(ResourceType, output_name, None)
            if out is None:
                return
            inputs = [
                getattr(ResourceType, n) for n in input_names
                if getattr(ResourceType, n, None) is not None
            ]
            if inputs:
                self.dependencies[out] = inputs

        # Prefer live simulation recipes when available
        try:
            from .sim import RECIPES
            for recipe in RECIPES.values() if isinstance(RECIPES, dict) else RECIPES:
                output = getattr(recipe, "output", None)
                inputs = getattr(recipe, "inputs", None) or {}
                if output is not None and inputs:
                    self.dependencies[output] = list(inputs.keys())
                    # Ensure outputs appear in hierarchy
                    if output not in self.resource_levels:
                        name = getattr(output, "name", "")
                        if name.endswith("_MODULE"):
                            self.resource_levels[output] = 5
                        elif "ORE" in name or name in {"WATER", "SALT", "LIMESTONE"}:
                            self.resource_levels[output] = 0
                        else:
                            self.resource_levels[output] = 3
            if self.dependencies:
                return
        except Exception:
            pass

        # Fallback simplified key recipes
        add("PURE_SILICON", "SILICON_ORE")
        add("STEEL", "IRON_ORE")
        add("COPPER_WIRE", "COPPER_ORE")
        add("ALUMINUM_SHEET", "ALUMINUM_ORE")
        add("LITHIUM_COMPOUND", "LITHIUM_ORE")
        add("RARE_EARTH_MAGNETS", "RARE_EARTH_ORE")
        add("SILICON_WAFER", "PURE_SILICON")
        add("TRANSISTOR", "SILICON_WAFER")
        add("CAPACITOR", "ALUMINUM_SHEET", "PLASTIC")
        add("RESISTOR", "COPPER_WIRE")
        add("LED", "SILICON_WAFER")
        add("BEARING", "STEEL")
        add("GEAR", "STEEL")
        add("MOTOR_COIL", "COPPER_WIRE", "RARE_EARTH_MAGNETS")
        add("INTEGRATED_CIRCUIT", "TRANSISTOR", "CAPACITOR", "RESISTOR")
        add("MICROPROCESSOR", "INTEGRATED_CIRCUIT", "TRANSISTOR")
        add("MEMORY_CHIP", "INTEGRATED_CIRCUIT", "CAPACITOR")
        add("PROXIMITY_SENSOR", "INTEGRATED_CIRCUIT", "LED")
        add("ELECTRIC_MOTOR", "MOTOR_COIL", "BEARING", "RARE_EARTH_MAGNETS")
        add("BATTERY_CELL", "LITHIUM_COMPOUND", "ALUMINUM_SHEET")
        add("SOLAR_CELL", "SILICON_WAFER", "GLASS")
        add("SOLAR_PANEL", "SOLAR_CELL", "ALUMINUM_SHEET")
        add("BATTERY_PACK", "BATTERY_CELL", "CONTROL_BOARD")
        add("CONTROL_BOARD", "MICROPROCESSOR", "MEMORY_CHIP", "PROXIMITY_SENSOR")
        add("ROBOTIC_ARM", "ELECTRIC_MOTOR", "LINEAR_ACTUATOR", "PROXIMITY_SENSOR")
        add("MINING_MODULE", "ROBOTIC_ARM", "CONVEYOR_SYSTEM", "CONTROL_BOARD")
        add("REFINING_MODULE", "FURNACE_ELEMENT", "CONTROL_BOARD")
        add("ELECTRONICS_MODULE", "CONTROL_BOARD")
        add("MECHANICAL_MODULE", "ROBOTIC_ARM", "CONTROL_BOARD")
        add("ASSEMBLY_MODULE", "ROBOTIC_ARM", "CONVEYOR_SYSTEM")
        add("POWER_MODULE", "SOLAR_PANEL", "BATTERY_PACK")
        add("CONTROL_MODULE", "MICROPROCESSOR", "MEMORY_CHIP", "DISPLAY_PANEL")

    def generate_flow_diagram(self, output_file="factory_system_diagram.png"):
        """Generate comprehensive flow diagram showing material flow"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 14))

        # Left panel: Hierarchical flow diagram
        self._draw_hierarchical_flow(ax1)
        ax1.set_title("Material Flow Hierarchy", fontsize=16, fontweight='bold')

        # Right panel: Module production network
        self._draw_module_network(ax2)
        ax2.set_title("Module Production Network", fontsize=16, fontweight='bold')

        # Main title
        fig.suptitle("Self-Replicating Factory System Architecture", fontsize=20, fontweight='bold', y=0.98)

        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"✅ System diagram saved to {output_file}")

    def _draw_hierarchical_flow(self, ax):
        """Draw hierarchical flow from raw materials to factory"""
        ax.set_xlim(-1, 11)
        ax.set_ylim(-0.5, 7.5)

        # Component positions by level
        positions = {}
        components_by_level = {}

        # Group components by level
        for resource, level in self.resource_levels.items():
            if level not in components_by_level:
                components_by_level[level] = []
            components_by_level[level].append(resource)

        # Calculate positions
        for level, components in components_by_level.items():
            n = len(components)
            if n == 1:
                x_positions = [5]
            else:
                x_positions = np.linspace(0.5, 9.5, n)

            for i, comp in enumerate(components):
                positions[comp] = (x_positions[i], level)

        # Draw components as boxes
        for resource, (x, y) in positions.items():
            # Determine box width based on name length
            name = resource.value.replace('_', '\n')
            if len(resource.value) > 15:
                name = resource.value.replace('_', ' ')[:12] + '...'

            width = 1.2 if y < 5 else 1.4
            height = 0.35

            # Draw box
            box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                                boxstyle="round,pad=0.05",
                                facecolor=self.level_colors[y],
                                edgecolor='black',
                                alpha=0.7,
                                linewidth=1.5)
            ax.add_patch(box)

            # Add text
            fontsize = 7 if y < 3 else 8
            ax.text(x, y, name, ha='center', va='center',
                   fontsize=fontsize, fontweight='bold', color='white')

        # Draw dependencies as arrows
        arrow_props = dict(arrowstyle='->', lw=1, alpha=0.4, color='gray')

        for output, inputs in self.dependencies.items():
            if output in positions:
                out_x, out_y = positions[output]
                for input_res in inputs:
                    if input_res in positions:
                        in_x, in_y = positions[input_res]
                        ax.annotate('', xy=(out_x, out_y - 0.18),
                                  xytext=(in_x, in_y + 0.18),
                                  arrowprops=arrow_props)

        # Add level labels
        for level, name in self.levels.items():
            ax.text(-0.5, level, name, ha='right', va='center',
                   fontsize=10, fontweight='bold', style='italic')

        # Add production flow indicators
        for level in range(6):
            ax.annotate('', xy=(10.5, level + 0.8), xytext=(10.5, level + 0.2),
                       arrowprops=dict(arrowstyle='->', lw=3, color='red', alpha=0.5))

        ax.text(10.5, -0.3, 'Production\nFlow', ha='center', fontsize=9,
               fontweight='bold', color='red')

        ax.axis('off')

    def _draw_module_network(self, ax):
        """Draw module interaction network"""
        ax.set_xlim(-2, 10)
        ax.set_ylim(-2, 8)

        # Module positions in a circular layout
        modules = ['mining', 'refining', 'electronics', 'mechanical',
                  'assembly', 'power', 'control']

        n = len(modules)
        angles = np.linspace(0, 2*np.pi, n, endpoint=False)
        radius = 3
        center = (4, 3)

        module_pos = {}
        for i, module in enumerate(modules):
            x = center[0] + radius * np.cos(angles[i] - np.pi/2)
            y = center[1] + radius * np.sin(angles[i] - np.pi/2)
            module_pos[module] = (x, y)

        # Draw module circles
        for module, (x, y) in module_pos.items():
            circle = Circle((x, y), 0.8, facecolor=self.module_colors[module],
                          edgecolor='black', linewidth=2, alpha=0.8)
            ax.add_patch(circle)

            # Add module name
            ax.text(x, y, module.upper(), ha='center', va='center',
                   fontsize=9, fontweight='bold', color='white')

        # Draw module dependencies
        module_deps = {
            'refining': ['mining'],
            'electronics': ['refining'],
            'mechanical': ['refining'],
            'assembly': ['electronics', 'mechanical'],
            'power': ['electronics'],
            'control': ['electronics', 'power']
        }

        for module, deps in module_deps.items():
            if module in module_pos:
                x2, y2 = module_pos[module]
                for dep in deps:
                    if dep in module_pos:
                        x1, y1 = module_pos[dep]
                        # Calculate arrow positions to stop at circle edge
                        dx, dy = x2 - x1, y2 - y1
                        length = np.sqrt(dx**2 + dy**2)
                        dx, dy = dx/length, dy/length

                        arrow = FancyArrowPatch((x1 + 0.8*dx, y1 + 0.8*dy),
                                              (x2 - 0.8*dx, y2 - 0.8*dy),
                                              arrowstyle='->', mutation_scale=20,
                                              lw=2, color='darkblue', alpha=0.6)
                        ax.add_patch(arrow)

        # Add central factory icon
        factory_box = FancyBboxPatch((center[0] - 1, center[1] - 0.5), 2, 1,
                                    boxstyle="round,pad=0.1",
                                    facecolor='gold',
                                    edgecolor='black',
                                    linewidth=3)
        ax.add_patch(factory_box)
        ax.text(center[0], center[1], 'FACTORY\nCORE', ha='center', va='center',
               fontsize=10, fontweight='bold')

        # Add energy flow indicators
        solar_pos = (0, 6)
        battery_pos = (8, 6)

        # Solar panel
        solar_box = FancyBboxPatch((solar_pos[0] - 0.6, solar_pos[1] - 0.4), 1.2, 0.8,
                                  facecolor='yellow',
                                  edgecolor='black',
                                  linewidth=2)
        ax.add_patch(solar_box)
        ax.text(solar_pos[0], solar_pos[1], '☀️ SOLAR', ha='center', va='center',
               fontsize=9, fontweight='bold')

        # Battery
        battery_box = FancyBboxPatch((battery_pos[0] - 0.6, battery_pos[1] - 0.4), 1.2, 0.8,
                                    facecolor='lightgreen',
                                    edgecolor='black',
                                    linewidth=2)
        ax.add_patch(battery_box)
        ax.text(battery_pos[0], battery_pos[1], '🔋 BATTERY', ha='center', va='center',
               fontsize=9, fontweight='bold')

        # Energy flow arrows
        power_x, power_y = module_pos['power']
        ax.annotate('', xy=(power_x - 0.5, power_y + 0.7),
                   xytext=(solar_pos[0] + 0.6, solar_pos[1] - 0.2),
                   arrowprops=dict(arrowstyle='->', lw=2, color='orange', alpha=0.7))
        ax.annotate('', xy=(battery_pos[0] - 0.6, battery_pos[1] - 0.2),
                   xytext=(power_x + 0.5, power_y + 0.7),
                   arrowprops=dict(arrowstyle='->', lw=2, color='green', alpha=0.7))

        # Add legend
        legend_items = [
            mpatches.Patch(color='darkblue', alpha=0.6, label='Material Flow'),
            mpatches.Patch(color='orange', alpha=0.7, label='Solar Energy'),
            mpatches.Patch(color='green', alpha=0.7, label='Stored Energy')
        ]
        ax.legend(handles=legend_items, loc='lower right', fontsize=9)

        # Add info box
        info_text = ("Each module specializes in:\n"
                    "• Mining: Raw material extraction\n"
                    "• Refining: Material processing\n"
                    "• Electronics: Circuit fabrication\n"
                    "• Mechanical: Part manufacturing\n"
                    "• Assembly: System integration\n"
                    "• Power: Energy management\n"
                    "• Control: System coordination")

        ax.text(0, 0, info_text, fontsize=8, bbox=dict(boxstyle="round,pad=0.5",
                                                       facecolor='lightyellow',
                                                       edgecolor='gray',
                                                       alpha=0.8))

        ax.axis('off')

    def generate_production_graph(self, log_file="factory_simulation_log.json",
                                 output_file="factory_production_graph.png"):
        """Generate detailed production dependency graph from simulation data"""
        # Load simulation log if available
        try:
            with open(log_file, 'r') as f:
                sim_data = json.load(f)
                config = sim_data.get('configuration', {})
        except FileNotFoundError:
            print(f"⚠️ {log_file} not found, generating default diagram")
            config = {}

        fig, ax = plt.subplots(figsize=(16, 12))

        # Create a more detailed dependency graph
        self._draw_detailed_dependency_graph(ax, config)

        ax.set_title("Production Dependency Graph", fontsize=18, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"✅ Production graph saved to {output_file}")

    def _draw_detailed_dependency_graph(self, ax, config):
        """Draw detailed production dependency graph"""
        ax.set_xlim(-1, 15)
        ax.set_ylim(-1, 8)

        # Get all unique resources in order of dependency
        all_resources = set()
        for res in ResourceType:
            all_resources.add(res)

        # Topological sort to arrange resources
        levels = {}
        for res in all_resources:
            level = self.resource_levels.get(res, 0)
            if level not in levels:
                levels[level] = []
            levels[level].append(res)

        # Create grid layout
        positions = {}
        for level, resources in sorted(levels.items()):
            n = len(resources)
            if n > 0:
                x_positions = np.linspace(1, 13, min(n, 8))
                for i, res in enumerate(resources[:8]):  # Limit to 8 per row
                    positions[res] = (x_positions[i % 8], level + (i // 8) * 0.5)

        # Draw all connections first (behind nodes)
        for output, inputs in self.dependencies.items():
            if output in positions:
                out_x, out_y = positions[output]
                for input_res in inputs:
                    if input_res in positions:
                        in_x, in_y = positions[input_res]
                        # Draw curved arrow
                        mid_x = (in_x + out_x) / 2
                        mid_y = (in_y + out_y) / 2 + 0.3

                        ax.annotate('', xy=(out_x, out_y - 0.12),
                                  xytext=(in_x, in_y + 0.12),
                                  arrowprops=dict(arrowstyle='->',
                                                connectionstyle="arc3,rad=0.2",
                                                lw=1.5, alpha=0.5, color='#444444'))

        # Draw nodes on top
        for res, (x, y) in positions.items():
            # Get level for color
            level = self.resource_levels.get(res, 0)
            color = self.level_colors[level]

            # Shorten long names
            name = res.value.replace('_', ' ').title()
            if len(name) > 12:
                name = name[:10] + '..'

            # Draw node
            node = FancyBboxPatch((x - 0.55, y - 0.15), 1.1, 0.3,
                                 boxstyle="round,pad=0.02",
                                 facecolor=color, edgecolor='black',
                                 alpha=0.85, linewidth=1)
            ax.add_patch(node)

            # Add text
            ax.text(x, y, name, ha='center', va='center',
                   fontsize=7, fontweight='bold', color='white')

        # Add level bands
        for level in range(7):
            ax.axhspan(level - 0.25, level + 0.25, alpha=0.1,
                      color=self.level_colors[level], zorder=0)

        # Add level labels
        for level, name in self.levels.items():
            ax.text(14, level, name, ha='left', va='center',
                   fontsize=10, fontweight='bold', style='italic',
                   bbox=dict(boxstyle="round,pad=0.3",
                           facecolor=self.level_colors[level],
                           alpha=0.3))

        # Add title and info
        if config:
            mode = "REALISTIC" if config.get('enable_capacity_limits', False) else "IDEALIZED"
            ax.text(7, 7.5, f"Mode: {mode}", ha='center', fontsize=11,
                   fontweight='bold', bbox=dict(boxstyle="round,pad=0.5",
                                              facecolor='lightblue', alpha=0.7))

        ax.axis('off')


def main():
    """Main entry point for visualization"""
    visualizer = FactoryVisualizer()

    # Generate main system diagram
    visualizer.generate_flow_diagram("factory_system_diagram.png")

    # Generate production dependency graph if simulation has been run
    visualizer.generate_production_graph("factory_simulation_log.json",
                                        "factory_production_graph.png")

    print("\n🎨 Visualization complete!")
    print("Generated files:")
    print("  • factory_system_diagram.png - System architecture overview")
    print("  • factory_production_graph.png - Detailed production dependencies")


if __name__ == "__main__":
    main()