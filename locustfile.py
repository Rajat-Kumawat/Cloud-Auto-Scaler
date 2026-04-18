
import math
from locust import HttpUser, task, between, LoadTestShape


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def index(self):
        self.client.get("/")

    @task
    def status(self):
        self.client.get("/status")

class SineWaveTraffic(LoadTestShape):
    """
    This class controls the number of users over time.
    It forces the user count to follow a Sine Wave pattern.
    """
    
    time_limit = 3600       
    min_users = 10          
    peak_users = 200        
    period = 300            

    def tick(self):
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None 

        # MATH LOGIC: Calculate target users based on Sine Wave
        # 1. Calculate the position in the cycle (0 to 2*pi)
        cycle_position = (run_time % self.period) / self.period * 2 * math.pi
        
        # 2. Calculate Sine value (-1 to +1)
        sine_value = math.sin(cycle_position)
        
        # 3. Normalize to our user range (0 to 1) -> (min to max)
        # (sine_value + 1) / 2 shifts the range from [-1, 1] to [0, 1]
        normalized_wave = (sine_value + 1) / 2
        
        # 4. Final User Count
        target_users = self.min_users + (normalized_wave * (self.peak_users - self.min_users))
        target_users = int(round(target_users))

        # 5. Spawn Rate (how fast to add users to reach target)
        spawn_rate = 20 

        return (target_users, spawn_rate)