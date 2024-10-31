from Network_Simulation_Base_Classes import BaseSimulator, NodeState
import random

class SlottedALOHA(BaseSimulator):
    def process_time_slot(self):
        self.medium.clear()
        
        for node in self.nodes:
            if node.state == NodeState.SENDING:
                if node.current_frame.tick():
                    self.successful_transmissions += 1
                    node.frames_sent += 1
                    node.state = NodeState.IDLE
                    self.medium.end_transmission(node.node_id)
            
            elif node.state == NodeState.IDLE and node.has_more_frames():
                if random.random() < 1.0 / (2 * self.num_hosts):
                    node.create_new_frame(*self.frame_size_range)
                    node.state = NodeState.SENDING
                    self.medium.start_transmission(node.node_id)
        
        if self.medium.has_collision():
            self.collisions += 1
            for node in self.nodes:
                if node.state == NodeState.SENDING:
                    node.state = NodeState.IDLE
            self.medium.clear()

class CSMACD(BaseSimulator):
    def process_time_slot(self):
        # Sense medium (0 slots)
        medium_busy = self.medium.is_busy()
        
        for node in self.nodes:
            if node.state == NodeState.BACKOFF:
                if node.backoff_counter > 0:
                    node.backoff_counter -= 1
                    if node.backoff_counter == 0:
                        node.state = NodeState.IDLE
            
            elif node.state == NodeState.SENDING:
                if node.current_frame.tick():
                    self.successful_transmissions += 1
                    node.frames_sent += 1
                    node.state = NodeState.IDLE
                    self.medium.end_transmission(node.node_id)
            
            elif node.state == NodeState.IDLE and node.has_more_frames():
                if not medium_busy:
                    node.create_new_frame(*self.frame_size_range)
                    node.state = NodeState.SENDING
                    self.medium.start_transmission(node.node_id)
        
        # Collision detection (1 slot)
        if self.medium.has_collision():
            self.collisions += 1
            self.total_slots += 1  # Jam signal slot
            
            for node in self.nodes:
                if node.state == NodeState.SENDING:
                    node.collision_count += 1
                    node.state = NodeState.BACKOFF
                    max_backoff = min(5, node.collision_count)  # Reduced backoff
                    node.backoff_counter = random.randint(0, 2**max_backoff - 1)
            self.medium.clear()

class CSMACA(BaseSimulator):
    def process_time_slot(self):
        # Sense medium (0 slots)
        medium_busy = self.medium.is_busy()
        
        for node in self.nodes:
            if node.state == NodeState.BACKOFF:
                if node.backoff_counter > 0:
                    node.backoff_counter -= 1
                    if node.backoff_counter == 0:
                        node.state = NodeState.IDLE
            
            elif node.state == NodeState.SENDING:
                if node.current_frame.tick():
                    self.successful_transmissions += 1
                    node.frames_sent += 1
                    node.state = NodeState.IDLE
                    self.medium.end_transmission(node.node_id)
                    self.total_slots += 2  # ACK frame (2 slots)
            
            elif node.state == NodeState.IDLE and node.has_more_frames():
                if not medium_busy:
                    if random.random() < 0.8:  # 80% chance for successful RTS/CTS
                        node.create_new_frame(*self.frame_size_range)
                        node.state = NodeState.SENDING
                        self.medium.start_transmission(node.node_id)
                        self.total_slots += 4  # RTS + CTS (2 slots each)
                    else:
                        node.state = NodeState.BACKOFF
                        node.backoff_counter = random.randint(1, 5)  # Reduced backoff
        
        if self.medium.has_collision():
            self.collisions += 1
            for node in self.nodes:
                if node.state == NodeState.SENDING:
                    node.state = NodeState.BACKOFF
                    node.backoff_counter = random.randint(1, 7)  # Reduced backoff
            self.medium.clear()