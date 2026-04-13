# from locust import HttpUser, task, between

# class StandardUser(HttpUser):
#     # This simulates a real user waiting 1 to 3 seconds between clicks.
#     # It prevents the traffic from being too "robotic".
#     wait_time = between(1, 3)

#     @task
#     def access_website(self):
#         # The user visits the homepage of your load balancer
#         self.client.get("/")
import math
from locust import HttpUser, task, between, LoadTestShape

# 1. THE TRAFFIC GENERATOR (The "User")
class WebsiteUser(HttpUser):
    # Wait between 1 and 3 seconds between tasks (simulates reading/thinking)
    wait_time = between(1, 3)

    @task
    def index(self):
        # Hits the homepage
        self.client.get("/")

    @task
    def status(self):
        # Hits the status page (lighter weight)
        self.client.get("/status")

# 2. THE TRAFFIC CONTROLLER (The "Brain")
class SineWaveTraffic(LoadTestShape):
    """
    This class controls the number of users over time.
    It forces the user count to follow a Sine Wave pattern.
    """
    
    # Configuration for the Wave
    time_limit = 3600       # Total run time (1 hour)
    min_users = 10          # Base number of users (trough)
    peak_users = 200        # Max number of users (peak)
    period = 300            # How long is one full wave? (300s = 5 mins)

    def tick(self):
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None # Stop the test

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