import time

class AcidDosingSystem:
    def __init__(self, target_pH, initial_volume=1000, buffer_window=5, recalculate_threshold=0.1):
        self.target_pH = target_pH  # Desired pH
        self.tank_volume = initial_volume  # Liters
        self.buffer_capacities = []  # Stores last buffer capacity values
        self.buffer_window = buffer_window  # Number of cycles to track buffer capacity
        self.recalculate_threshold = recalculate_threshold  # When to recalculate buffer capacity
        self.current_pH = 7.0  # Initial assumption
        self.sensor = self.MockPHSensor()  # Mock sensor
        self.pump = self.MockPump()  # Mock acid/base pump

    class MockPHSensor:
        """Simulates a pH sensor"""
        def read_pH(self):
            return round(6.8 + (0.4 * (time.time() % 10) / 10), 2)  # Simulated pH variation

    class MockPump:
        """Simulates an acid/base dosing pump"""
        def dose_acid(self, volume_ml):
            print(f"Adding {volume_ml:.2f} mL of acid to tank...")

    def estimate_buffer_capacity(self):
        """Estimates buffer capacity (β) by adding a known small acid dose and measuring pH change"""
        test_acid_dose = 0.5  # 10 mL of acid
        initial_pH = self.sensor.read_pH()
        self.pump.dose_acid(test_acid_dose)
        time.sleep(1)  # Simulating mixing time
        final_pH = self.sensor.read_pH()
        pH_change = abs(final_pH - initial_pH)

        if pH_change == 0:
            print("Warning: No pH change detected! Check sensors or acid concentration.")
            return None

        buffer_capacity = test_acid_dose / pH_change  # Simple linear estimation
        print(f"Estimated buffer capacity: {buffer_capacity:.2f} mL/pH")
        return buffer_capacity

    def get_buffer_capacity(self):
        """Returns a rolling average of buffer capacities"""
        if not self.buffer_capacities:
            return self.estimate_buffer_capacity()
        return sum(self.buffer_capacities) / len(self.buffer_capacities)

    def adjust_ph(self):
        """Main function that adjusts pH using buffer capacity"""
        current_pH = self.sensor.read_pH()
        print(f"Current pH: {current_pH}")

        buffer_capacity = self.get_buffer_capacity()
        if buffer_capacity is None:
            print("Error: Could not estimate buffer capacity. Skipping this cycle.")
            return

        required_pH_change = self.target_pH - current_pH
        if abs(required_pH_change) < 0.05:
            print("pH is within acceptable range. No action needed.")
            return

        required_acid_volume = buffer_capacity * required_pH_change
        self.pump.dose_acid(required_acid_volume)
        time.sleep(1)  # Simulating mixing time
        new_pH = self.sensor.read_pH()

        # If the pH correction deviates significantly, recalculate buffer capacity
        actual_pH_change = abs(new_pH - current_pH)
        expected_pH_change = abs(required_pH_change)
        deviation = abs(actual_pH_change - expected_pH_change)

        if deviation > self.recalculate_threshold:
            print(f"pH adjustment deviated by {deviation:.2f}. Recalculating buffer capacity.")
            new_buffer_capacity = self.estimate_buffer_capacity()
            if new_buffer_capacity:
                self.buffer_capacities.append(new_buffer_capacity)

        # Maintain a rolling buffer history
        if len(self.buffer_capacities) > self.buffer_window:
            self.buffer_capacities.pop(0)

    def run(self, cycles=10):
        """Runs multiple adjustment cycles"""
        for cycle in range(cycles):
            print(f"\n--- Cycle {cycle+1} ---")
            self.adjust_ph()
            time.sleep(2)

# Example usage
dosing_system = AcidDosingSystem(target_pH=6.5)
dosing_system.run(10)
