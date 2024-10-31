from Network_Simulation_Base_Classes import BaseSimulator, plot_results
from Protocol_Implementations import SlottedALOHA, CSMACD, CSMACA
import time

def run_experiment(protocol_class, host_counts, frame_ranges):
    results = {
        'slots_by_hosts': [],
        'slots_by_frames': [],
        'success_rates': [],
        'collision_rates': []
    }
    
    print(f"\nTesting {protocol_class.__name__}...")
    
    # Test varying number of hosts
    for num_hosts in host_counts:
        print(f"Testing with {num_hosts} hosts...", end='', flush=True)
        simulator = protocol_class(num_hosts, frames_per_host=5)
        slots, collision_rate, success_rate = simulator.run()
        
        results['slots_by_hosts'].append(slots)
        results['success_rates'].append(success_rate)
        results['collision_rates'].append(collision_rate)
        
        print(f" Done: {slots} slots, "
              f"Success Rate: {success_rate:.1%}")
    
    # Test varying frame sizes with fixed 16 hosts as per requirements
    print("\nTesting frame sizes with 16 hosts...")
    for frame_range in frame_ranges:
        print(f"Testing frame range {frame_range}...", end='', flush=True)
        simulator = protocol_class(16, frames_per_host=5, frame_size_range=frame_range)
        slots, _, _ = simulator.run()
        results['slots_by_frames'].append(slots)
        print(f" Done: {slots} slots")
    
    return results

def test_protocols():
    # Full test parameters as per requirements
    host_counts = [5, 10, 15, 20, 25]
    frame_ranges = [(5, 10), (10, 15), (15, 20), (20, 25)]
    
    print("\nStarting Network Protocol Simulation...")
    print(f"Testing with host counts: {host_counts}")
    print(f"Frame ranges: {frame_ranges}")
    start_time = time.time()
    
    results = {}
    for protocol_class in [SlottedALOHA, CSMACD, CSMACA]:
        results[protocol_class.__name__] = run_experiment(
            protocol_class,
            host_counts,
            frame_ranges
        )
        elapsed = time.time() - start_time
        print(f"Completed {protocol_class.__name__} in {elapsed:.1f} seconds")
    
    print("\nGenerating plots...")
    plot_results(
        'Network Protocol Performance Comparison',
        host_counts,
        frame_ranges,
        results
    )
    
    duration = time.time() - start_time
    print(f"\nSimulation completed in {duration:.1f} seconds")

if __name__ == "__main__":
    test_protocols()