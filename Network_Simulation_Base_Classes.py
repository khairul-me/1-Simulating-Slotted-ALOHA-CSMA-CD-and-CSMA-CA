import random
from enum import Enum
import matplotlib.pyplot as plt

class NodeState(Enum):
    IDLE = 0
    SENSING = 1
    SENDING = 2
    BACKOFF = 3

class Frame:
    def __init__(self, sender_id, min_size=8, max_size=16):
        self.sender_id = sender_id
        self.size = random.randint(min_size, max_size)
        self.remaining_slots = self.size
        
    def tick(self):
        if self.remaining_slots > 0:
            self.remaining_slots -= 1
        return self.remaining_slots == 0

class Node:
    def __init__(self, node_id, num_frames=5):  # Reduced to 5 frames
        self.node_id = node_id
        self.state = NodeState.IDLE
        self.frames_to_send = num_frames
        self.current_frame = None
        self.backoff_counter = 0
        self.collision_count = 0
        self.frames_sent = 0
        
    def has_more_frames(self):
        return self.frames_to_send > 0
    
    def create_new_frame(self, min_size=8, max_size=16):
        if self.has_more_frames():
            self.current_frame = Frame(self.node_id, min_size, max_size)
            self.frames_to_send -= 1
            return True
        return False

class Medium:
    def __init__(self):
        self.transmitting_nodes = set()
        self.jam_signal = False
        
    def is_busy(self):
        return bool(self.transmitting_nodes) or self.jam_signal
        
    def has_collision(self):
        return len(self.transmitting_nodes) > 1
    
    def start_transmission(self, node_id):
        self.transmitting_nodes.add(node_id)
        
    def end_transmission(self, node_id):
        self.transmitting_nodes.discard(node_id)
        
    def clear(self):
        self.transmitting_nodes.clear()
        self.jam_signal = False

class BaseSimulator:
    def __init__(self, num_hosts, frames_per_host=5, frame_size_range=(8, 16)):
        self.num_hosts = num_hosts
        self.frames_per_host = frames_per_host
        self.frame_size_range = frame_size_range
        self.medium = Medium()
        self.nodes = [Node(i, frames_per_host) for i in range(num_hosts)]
        self.total_slots = 0
        self.collisions = 0
        self.successful_transmissions = 0
        
    def all_nodes_done(self):
        return all(not node.has_more_frames() and node.state == NodeState.IDLE 
                  for node in self.nodes)
    
    def run(self):
        max_slots = 200  # Maximum slot limit
        while not self.all_nodes_done() and self.total_slots < max_slots:
            self.process_time_slot()
            self.total_slots += 1
            
            # Early termination if stuck
            if self.total_slots > 50 and self.successful_transmissions == 0:
                break
        
        total_attempts = self.collisions + self.successful_transmissions
        if total_attempts == 0:
            return self.total_slots, 0, 0
            
        collision_rate = self.collisions / total_attempts
        success_rate = self.successful_transmissions / total_attempts
        return self.total_slots, collision_rate, success_rate

def plot_results(title, host_counts, frame_ranges, results_dict):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Impact of Host Count
    for protocol, data in results_dict.items():
        ax1.plot(host_counts, data['slots_by_hosts'], marker='o', label=protocol)
    ax1.set_xlabel('Number of Hosts')
    ax1.set_ylabel('Total Time Slots')
    ax1.set_title('Impact of Host Count')
    ax1.legend()
    ax1.grid(True)
    
    # Plot 2: Impact of Frame Size
    frame_labels = [f'[{r[0]},{r[1]}]' for r in frame_ranges]
    for protocol, data in results_dict.items():
        ax2.plot(frame_labels, data['slots_by_frames'], marker='o', label=protocol)
    ax2.set_xlabel('Frame Size Range')
    ax2.set_ylabel('Total Time Slots')
    ax2.set_title('Impact of Frame Size')
    ax2.legend()
    ax2.grid(True)
    
    # Plot 3: Success Rates
    for protocol, data in results_dict.items():
        ax3.plot(host_counts, data['success_rates'], marker='s', label=protocol)
    ax3.set_xlabel('Number of Hosts')
    ax3.set_ylabel('Success Rate')
    ax3.set_title('Success Rate vs Number of Hosts')
    ax3.legend()
    ax3.grid(True)
    
    # Plot 4: Collision Rates
    for protocol, data in results_dict.items():
        ax4.plot(host_counts, data['collision_rates'], marker='d', label=protocol)
    ax4.set_xlabel('Number of Hosts')
    ax4.set_ylabel('Collision Rate')
    ax4.set_title('Collision Rate vs Number of Hosts')
    ax4.legend()
    ax4.grid(True)
    
    plt.suptitle(title)
    plt.tight_layout()
    plt.show()