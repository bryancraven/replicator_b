#!/usr/bin/env python3
"""
Ultra-Realistic Factory Simulation Analysis Dashboard
Provides comprehensive visualization even for failed/incomplete simulations
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle, Circle
from matplotlib.sankey import Sankey
from collections import defaultdict, Counter
import numpy as np
from datetime import datetime

def load_simulation_data(log_file="factory_simulation_log.json"):
    """Load and validate simulation data"""
    try:
        with open(log_file, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"❌ Log file '{log_file}' not found. Please run simulation first.")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error parsing '{log_file}'. File may be corrupted.")
        return None

def create_ultra_dashboard(data):
    """Create comprehensive dashboard with useful insights even for failed simulations"""

    # Create figure with custom layout - 12 panels for comprehensive analysis
    fig = plt.figure(figsize=(24, 16))
    fig.suptitle("Ultra-Realistic Factory Analysis Dashboard", fontsize=20, fontweight='bold')

    # Create grid layout - 4 rows, 3 columns
    gs = gridspec.GridSpec(4, 3, figure=fig, hspace=0.3, wspace=0.25)

    # Extract data
    config = data.get("config", {})
    final_status = data.get("final_status", {})
    metrics = data.get("metrics", {})
    log_entries = data.get("log_entries", [])
    completed_tasks = data.get("completed_tasks", [])

    simulation_time = final_status.get('time', 0)
    simulation_days = simulation_time / 24 if simulation_time > 0 else 1

    # ========== Panel 1: Resource Inventory Levels ==========
    ax1 = fig.add_subplot(gs[0, 0])
    plot_resource_inventory(ax1, completed_tasks, log_entries)

    # ========== Panel 2: Module Health Grid ==========
    ax2 = fig.add_subplot(gs[0, 1])
    plot_module_health_grid(ax2, final_status, log_entries)

    # ========== Panel 3: Blocking Reasons Breakdown ==========
    ax3 = fig.add_subplot(gs[0, 2])
    plot_blocking_breakdown(ax3, log_entries, final_status)

    # ========== Panel 4: Energy Balance Over Time ==========
    ax4 = fig.add_subplot(gs[1, 0])
    plot_energy_balance(ax4, metrics, config)

    # ========== Panel 5: Transport System Status ==========
    ax5 = fig.add_subplot(gs[1, 1])
    plot_transport_status(ax5, final_status, log_entries)

    # ========== Panel 6: Software Development Progress ==========
    ax6 = fig.add_subplot(gs[1, 2])
    plot_software_progress(ax6, final_status, completed_tasks)

    # ========== Panel 7: Production Timeline ==========
    ax7 = fig.add_subplot(gs[2, 0])
    plot_production_timeline(ax7, completed_tasks, simulation_days)

    # ========== Panel 8: Waste & Recycling Flow ==========
    ax8 = fig.add_subplot(gs[2, 1])
    plot_waste_flow(ax8, final_status, completed_tasks)

    # ========== Panel 9: Failure Cascade Analysis ==========
    ax9 = fig.add_subplot(gs[2, 2])
    plot_failure_cascade(ax9, log_entries)

    # ========== Panel 10-12: Summary Statistics ==========
    ax10 = fig.add_subplot(gs[3, :])
    plot_summary_statistics(ax10, data)

    plt.tight_layout()
    return fig

def plot_resource_inventory(ax, completed_tasks, log_entries):
    """Show top resources in inventory"""
    ax.set_title("Resource Inventory (Top 15)", fontweight='bold')

    # Count resources from completed tasks
    resources = defaultdict(float)
    for task in completed_tasks:
        output = task.get('output', 'unknown')
        quantity = task.get('actual_output', task.get('quantity', 0))
        resources[output] += quantity

    # Sort and get top 15
    sorted_resources = sorted(resources.items(), key=lambda x: x[1], reverse=True)[:15]

    if sorted_resources:
        names = [r[0].replace('_', '\n') for r in sorted_resources]
        quantities = [r[1] for r in sorted_resources]

        bars = ax.barh(names, quantities)

        # Color by category
        colors = []
        for name in [r[0] for r in sorted_resources]:
            if '_ore' in name:
                colors.append('#8B4513')
            elif 'chemical' in name or 'acid' in name:
                colors.append('#9370DB')
            elif 'module' in name:
                colors.append('#FF6347')
            elif 'board' in name or 'circuit' in name:
                colors.append('#FFD700')
            else:
                colors.append('#4682B4')

        for bar, color in zip(bars, colors):
            bar.set_color(color)

        ax.set_xlabel("Quantity")
        ax.grid(True, alpha=0.3, axis='x')
    else:
        ax.text(0.5, 0.5, 'No Resources Produced', ha='center', va='center', fontsize=12)

    ax.set_xlim(left=0)

def plot_module_health_grid(ax, final_status, log_entries):
    """Visual grid showing module status and health"""
    ax.set_title("Module Status Grid", fontweight='bold')

    modules = final_status.get('modules', {})

    # Define module layout in grid (4x4)
    module_layout = [
        ['mining', 'refining', 'chemical', 'electronics'],
        ['mechanical', 'cnc', 'laser', 'cleanroom'],
        ['assembly', 'software', 'transport', 'recycling'],
        ['testing', 'thermal', 'power', 'control']
    ]

    # Check for failures in log
    failed_modules = set()
    for entry in log_entries:
        if 'FAILED' in entry.get('message', ''):
            for module in modules.keys():
                if module in entry['message'].lower():
                    failed_modules.add(module)

    # Draw grid
    for i, row in enumerate(module_layout):
        for j, module in enumerate(row):
            x, y = j * 0.25, (3-i) * 0.25

            # Determine status and color
            if module in failed_modules:
                color = 'red'
                status = 'FAILED'
            elif module in modules:
                count = modules[module]
                if count > 0:
                    color = 'green'
                    status = f'{count}'
                else:
                    color = 'orange'
                    status = '0'
            else:
                color = 'lightgray'
                status = 'N/A'

            # Draw rectangle
            rect = Rectangle((x, y), 0.22, 0.22, facecolor=color, edgecolor='black', alpha=0.7)
            ax.add_patch(rect)

            # Add text
            ax.text(x + 0.11, y + 0.15, module.upper()[:4], ha='center', va='center', fontsize=8, fontweight='bold')
            ax.text(x + 0.11, y + 0.07, status, ha='center', va='center', fontsize=10)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    # Add legend
    legend_elements = [
        mpatches.Patch(color='green', label='Operational'),
        mpatches.Patch(color='orange', label='Not Available'),
        mpatches.Patch(color='red', label='Failed'),
        mpatches.Patch(color='lightgray', label='Unknown')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=8)

def plot_blocking_breakdown(ax, log_entries, final_status):
    """Pie chart of blocking reasons"""
    ax.set_title("Task Blocking Reasons", fontweight='bold')

    # Count blocking reasons
    blocking_reasons = defaultdict(int)
    for entry in log_entries:
        msg = entry.get('message', '')
        if 'blocked' in msg.lower():
            if 'energy' in msg.lower():
                blocking_reasons['Energy'] += 1
            elif 'module' in msg.lower() or 'no ' in msg.lower():
                blocking_reasons['Module\nUnavailable'] += 1
            elif 'resource' in msg.lower() or 'needs' in msg.lower():
                blocking_reasons['Missing\nResources'] += 1
            elif 'dependencies' in msg.lower():
                blocking_reasons['Dependencies'] += 1
            elif 'thermal' in msg.lower():
                blocking_reasons['Thermal'] += 1
            elif 'storage' in msg.lower():
                blocking_reasons['Storage'] += 1
            else:
                blocking_reasons['Other'] += 1

    if blocking_reasons:
        labels = list(blocking_reasons.keys())
        sizes = list(blocking_reasons.values())
        colors = ['#FF6347', '#FFD700', '#4682B4', '#9370DB', '#32CD32', '#FF69B4', '#708090']

        # Create pie chart
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90)

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

        # Add total blocked count
        total_blocked = final_status.get('blocked_tasks', 0)
        ax.text(0, -1.3, f'Total Blocked Tasks: {total_blocked}', ha='center', fontsize=10, fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'No Blocked Tasks', ha='center', va='center', fontsize=12)

def plot_energy_balance(ax, metrics, config):
    """Energy generation vs consumption over time"""
    ax.set_title("Energy Balance", fontweight='bold')

    if metrics and 'time' in metrics and len(metrics['time']) > 0:
        times = np.array(metrics['time']) / 24  # Convert to days

        # Calculate theoretical generation
        solar_capacity = config.get('initial_solar_capacity_kw', 100)
        generation = [solar_capacity * 8 / 24 for _ in times]  # Simplified

        # Use battery charge as proxy for consumption
        if 'battery_charge' in metrics:
            battery = metrics['battery_charge']

            ax.plot(times[:len(battery)], battery, 'b-', label='Battery Charge', linewidth=2)
            ax.fill_between(times[:len(battery)], 0, battery, alpha=0.3, color='blue')

        ax.axhline(y=solar_capacity * 8 / 24, color='orange', linestyle='--', label=f'Avg Solar ({solar_capacity}kW)', alpha=0.7)

        ax.set_xlabel("Time (days)")
        ax.set_ylabel("Energy (kWh)")
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max(times) if len(times) > 0 else 1)
    else:
        ax.text(0.5, 0.5, 'No Energy Data', ha='center', va='center', fontsize=12)

def plot_transport_status(ax, final_status, log_entries):
    """Transport system utilization"""
    ax.set_title("Transport System Status", fontweight='bold')

    transport_completed = final_status.get('transport_completed', 0)

    # Count transport events in log
    transport_events = {'scheduled': 0, 'completed': 0, 'agv_busy': 0}
    for entry in log_entries:
        msg = entry.get('message', '')
        if 'transport' in msg.lower():
            if 'scheduled' in msg.lower():
                transport_events['scheduled'] += 1
            elif 'completed' in msg.lower():
                transport_events['completed'] += 1
            elif 'agv' in msg.lower() and 'busy' in msg.lower():
                transport_events['agv_busy'] += 1

    # Create bars
    categories = ['Scheduled', 'Completed', 'AGV Busy\nEvents']
    values = [transport_events['scheduled'], transport_completed, transport_events['agv_busy']]
    colors = ['#4682B4', '#32CD32', '#FF6347']

    bars = ax.bar(categories, values, color=colors, alpha=0.7)

    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(val)}', ha='center', va='bottom', fontweight='bold')

    ax.set_ylabel("Count")
    ax.grid(True, alpha=0.3, axis='y')

    # Add AGV fleet info
    agv_fleet_size = 10  # From config
    ax.text(0.5, 0.95, f'AGV Fleet Size: {agv_fleet_size}', transform=ax.transAxes,
            ha='center', fontsize=10, fontweight='bold')

def plot_software_progress(ax, final_status, completed_tasks):
    """Software development progress"""
    ax.set_title("Software Development", fontweight='bold')

    software_packages = final_status.get('software_packages', 0)

    # Count software types from completed tasks
    software_types = {'plc_program': 0, 'robot_firmware': 0, 'ai_model': 0, 'scada_system': 0}
    for task in completed_tasks:
        output = task.get('output', '')
        if output in software_types:
            software_types[output] += task.get('actual_output', 1)

    # Create stacked bar
    labels = ['PLC\nProgram', 'Robot\nFirmware', 'AI\nModel', 'SCADA\nSystem']
    values = [software_types['plc_program'], software_types['robot_firmware'],
              software_types['ai_model'], software_types['scada_system']]
    colors = ['#4169E1', '#FF6347', '#32CD32', '#FFD700']

    bars = ax.bar(labels, values, color=colors, alpha=0.8)

    # Add value labels
    for bar, val in zip(bars, values):
        if val > 0:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(val)}', ha='center', va='bottom', fontweight='bold')

    ax.set_ylabel("Packages Developed")
    ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 1)
    ax.grid(True, alpha=0.3, axis='y')

    # Add total
    ax.text(0.5, 0.95, f'Total Software: {software_packages} packages',
            transform=ax.transAxes, ha='center', fontsize=10, fontweight='bold')

def plot_production_timeline(ax, completed_tasks, simulation_days):
    """Timeline of what was produced"""
    ax.set_title("Production Timeline", fontweight='bold')

    if completed_tasks:
        # Group by category
        categories = {
            'Raw Materials': [],
            'Chemicals': [],
            'Refined': [],
            'Components': [],
            'Software': [],
            'Modules': []
        }

        for task in completed_tasks:
            time = task.get('completion_time', 0) / 24  # Convert to days
            output = task.get('output', 'unknown')

            if '_ore' in output:
                categories['Raw Materials'].append(time)
            elif 'acid' in output or 'chemical' in output or 'solvent' in output:
                categories['Chemicals'].append(time)
            elif 'steel' in output or 'wire' in output or 'sheet' in output:
                categories['Refined'].append(time)
            elif '_module' in output:
                categories['Modules'].append(time)
            elif 'program' in output or 'firmware' in output or 'model' in output:
                categories['Software'].append(time)
            else:
                categories['Components'].append(time)

        # Plot timeline
        y_positions = list(range(len(categories)))
        colors = ['#8B4513', '#9370DB', '#4682B4', '#FFD700', '#00CED1', '#FF6347']

        for i, (cat, times) in enumerate(categories.items()):
            if times:
                ax.scatter(times, [i]*len(times), alpha=0.7, s=30, color=colors[i], label=cat)

        ax.set_yticks(y_positions)
        ax.set_yticklabels(list(categories.keys()))
        ax.set_xlabel("Time (days)")
        ax.set_xlim(0, simulation_days)
        ax.grid(True, alpha=0.3, axis='x')
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=8)
    else:
        ax.text(0.5, 0.5, 'No Production Data', ha='center', va='center', fontsize=12)

def plot_waste_flow(ax, final_status, completed_tasks):
    """Waste generation and recycling potential"""
    ax.set_title("Waste & Recycling", fontweight='bold')

    waste_total = final_status.get('waste_total', 0)

    # Estimate recyclable vs non-recyclable
    recyclable_rate = 0.75  # 75% recyclable estimate
    recyclable = waste_total * recyclable_rate
    non_recyclable = waste_total * (1 - recyclable_rate)

    # Create donut chart
    sizes = [recyclable, non_recyclable]
    labels = [f'Recyclable\n{recyclable:.1f} tons', f'Non-Recyclable\n{non_recyclable:.1f} tons']
    colors = ['#32CD32', '#FF6347']

    if waste_total > 0:
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90,
                                          wedgeprops=dict(width=0.3))

        # Add center text
        ax.text(0, 0, f'Total Waste\n{waste_total:.1f} tons',
                ha='center', va='center', fontsize=11, fontweight='bold')

        # Potential recovery value
        recovery_value = recyclable * 0.85  # 85% recovery rate
        ax.text(0, -1.3, f'Potential Recovery: {recovery_value:.1f} tons',
                ha='center', fontsize=10)
    else:
        ax.text(0.5, 0.5, 'No Waste Generated', ha='center', va='center', fontsize=12)

def plot_failure_cascade(ax, log_entries):
    """Show how failures propagated"""
    ax.set_title("Failure Cascade Timeline", fontweight='bold')

    # Find critical events
    critical_events = []
    for entry in log_entries:
        msg = entry.get('message', '')
        time = entry.get('timestamp', 0) / 24  # Convert to days

        if 'FAILED' in msg:
            critical_events.append(('FAILURE', time, msg[:50]))
        elif 'blocked' in msg and len(critical_events) < 20:  # Limit to first 20
            if 'mining' in msg.lower():
                critical_events.append(('BLOCK-MINING', time, 'Mining unavailable'))
            elif 'energy' in msg.lower():
                critical_events.append(('BLOCK-ENERGY', time, 'Energy shortage'))
            elif 'module' in msg.lower():
                critical_events.append(('BLOCK-MODULE', time, 'Module unavailable'))

    if critical_events:
        # Get unique events
        unique_events = []
        seen = set()
        for event in critical_events:
            key = (event[0], round(event[1], 1))
            if key not in seen:
                seen.add(key)
                unique_events.append(event)

        # Plot timeline
        event_types = list(set(e[0] for e in unique_events))
        colors_map = {
            'FAILURE': 'red',
            'BLOCK-MINING': 'orange',
            'BLOCK-ENERGY': 'yellow',
            'BLOCK-MODULE': 'purple'
        }

        for event in unique_events[:20]:  # Limit display
            event_type, time, msg = event
            y_pos = event_types.index(event_type)
            color = colors_map.get(event_type, 'gray')

            ax.scatter(time, y_pos, color=color, s=100, alpha=0.7, edgecolor='black')

        ax.set_yticks(range(len(event_types)))
        ax.set_yticklabels(event_types)
        ax.set_xlabel("Time (days)")
        ax.grid(True, alpha=0.3, axis='x')

        # Add annotation for first failure
        if unique_events:
            first_failure = next((e for e in unique_events if e[0] == 'FAILURE'), None)
            if first_failure:
                ax.annotate(f'First Failure\nDay {first_failure[1]:.1f}',
                          xy=(first_failure[1], 0), xytext=(first_failure[1], -0.5),
                          arrowprops=dict(arrowstyle='->', color='red'),
                          fontsize=9, ha='center')
    else:
        ax.text(0.5, 0.5, 'No Failures Detected', ha='center', va='center', fontsize=12)

def plot_summary_statistics(ax, data):
    """Summary statistics and recommendations"""
    ax.set_title("Summary Statistics & Recommendations", fontweight='bold')
    ax.axis('off')

    final_status = data.get('final_status', {})
    config = data.get('config', {})

    # Calculate key metrics
    simulation_time = final_status.get('time', 0)
    simulation_days = simulation_time / 24
    completed_tasks = final_status.get('completed_tasks', 0)
    blocked_tasks = final_status.get('blocked_tasks', 0)
    total_modules = sum(final_status.get('modules', {}).values())

    # Production rate
    production_rate = completed_tasks / simulation_days if simulation_days > 0 else 0

    # Success rate
    total_attempted = completed_tasks + blocked_tasks
    success_rate = (completed_tasks / total_attempted * 100) if total_attempted > 0 else 0

    # Create three columns
    col1_text = f"""
    SIMULATION METRICS:
    • Duration: {simulation_days:.1f} days ({simulation_time:.1f} hours)
    • Tasks Completed: {completed_tasks}
    • Tasks Blocked: {blocked_tasks}
    • Success Rate: {success_rate:.1f}%
    • Production Rate: {production_rate:.1f} tasks/day
    • Modules Built: {total_modules}
    """

    col2_text = f"""
    RESOURCE METRICS:
    • Waste Generated: {final_status.get('waste_total', 0):.1f} tons
    • Transport Jobs: {final_status.get('transport_completed', 0)}
    • Software Packages: {final_status.get('software_packages', 0)}
    • Solar Capacity: {config.get('initial_solar_capacity_kw', 0)} kW
    • AGV Fleet: {config.get('agv_fleet_size', 0)} vehicles
    • Factory Area: {config.get('factory_area_m2', 0):,} m²
    """

    # Determine main bottleneck
    log_entries = data.get('log_entries', [])
    blocking_reasons = defaultdict(int)
    for entry in log_entries:
        if 'blocked' in entry.get('message', '').lower():
            if 'mining' in entry['message'].lower():
                blocking_reasons['Mining Module'] += 1
            elif 'energy' in entry['message'].lower():
                blocking_reasons['Energy'] += 1
            elif 'module' in entry['message'].lower():
                blocking_reasons['Module Availability'] += 1

    main_bottleneck = max(blocking_reasons.items(), key=lambda x: x[1])[0] if blocking_reasons else "Unknown"

    col3_text = f"""
    RECOMMENDATIONS:
    • Main Bottleneck: {main_bottleneck}
    • {'✗ Increase mining module redundancy' if 'Mining' in main_bottleneck else '✓ Mining OK'}
    • {'✗ Increase solar to 500+ kW' if 'Energy' in main_bottleneck else '✓ Energy OK'}
    • {'✗ Add module redundancy' if 'Module' in main_bottleneck else '✓ Modules OK'}
    • {'✓ Transport system adequate' if final_status.get('transport_completed', 0) > 50 else '✗ Expand transport fleet'}
    • {'✓ Software development on track' if final_status.get('software_packages', 0) > 20 else '✗ Accelerate software dev'}
    """

    # Display text in columns
    ax.text(0.05, 0.5, col1_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='center', family='monospace')
    ax.text(0.35, 0.5, col2_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='center', family='monospace')
    ax.text(0.65, 0.5, col3_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='center', family='monospace')

    # Add status indicator
    if success_rate > 75:
        status = "✅ HEALTHY"
        color = 'green'
    elif success_rate > 25:
        status = "⚠️ STRUGGLING"
        color = 'orange'
    else:
        status = "❌ FAILED"
        color = 'red'

    ax.text(0.5, 0.95, f'Overall Status: {status}', transform=ax.transAxes,
            ha='center', fontsize=14, fontweight='bold', color=color)

def main():
    """Main analysis function"""
    print("=" * 80)
    print("ULTRA-REALISTIC FACTORY SIMULATION ANALYSIS")
    print("=" * 80)

    # Load data
    data = load_simulation_data()
    if not data:
        return

    # Print console summary
    final_status = data.get("final_status", {})
    config = data.get("config", {})

    print("\n📊 SIMULATION SUMMARY:")
    print(f"  Duration: {final_status.get('time', 0)/24:.1f} days")
    print(f"  Tasks Completed: {final_status.get('completed_tasks', 0)}")
    print(f"  Tasks Blocked: {final_status.get('blocked_tasks', 0)}")
    print(f"  Waste Generated: {final_status.get('waste_total', 0):.1f} tons")
    print(f"  Transport Jobs: {final_status.get('transport_completed', 0)}")
    print(f"  Software Packages: {final_status.get('software_packages', 0)}")

    modules = final_status.get("modules", {})
    failed_count = sum(1 for v in modules.values() if v == 0)
    print(f"\n🏭 MODULE STATUS:")
    print(f"  Operational: {sum(1 for v in modules.values() if v > 0)}/{len(modules)}")
    print(f"  Failed/Missing: {failed_count}")

    # Create visualization
    print("\n📊 Creating ultra-realistic dashboard...")
    fig = create_ultra_dashboard(data)

    # Save
    output_file = 'factory_simulation_analysis_ultra.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"  ✅ Dashboard saved to '{output_file}'")

    # Show if available
    try:
        plt.show()
    except:
        pass

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()