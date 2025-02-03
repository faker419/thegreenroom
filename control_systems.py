import time
import datetime

# Global Configuration
config = {
    "target_ph": 6.5,  # Desired pH
    "increment_size": 0.1,  # Fraction of total solution to add at a time
    "max_attempts": 3,  # Maximum number of adjustment cycles
    "acid_flow_rate": 0.1,  # liters/second (example)
    "base_flow_rate": 0.1,  # liters/second (example)
    "acid_concentration": 1.0,  # Molarity of acid solution (e.g., 1.0 M HCl)
    "base_concentration": 1.0,  # Molarity of base solution (e.g., 1.0 M NaOH)
    "ph_acceptable_margin": 0.1,  # The pH difference which will be accepted as target
    "mixing_time": 20,  # Time to mix after each addition (seconds)
    "settling_time": 60,  # Time to settle before rechecking pH (seconds)
    "tank_volume": 1000,  # Volume of Tank B (liters)
}

# Sensor Class
class Sensor:
    def __init__(self, pin):
        self.pin = pin

    def read(self):
        # Replace with actual sensor reading logic
        return 0.0

# Pump Class
class Pump:
    def __init__(self, pin):
        self.pin = pin

    def on(self):
        print(f"Pump on pin {self.pin} is ON")

    def off(self):
        print(f"Pump on pin {self.pin} is OFF")

    def run(self, duration):
        self.on()
        time.sleep(duration)
        self.off()

# Mixer Class
class Mixer:
    def __init__(self, pin):
        self.pin = pin

    def on(self):
        print(f"Mixer on pin {self.pin} is ON")

    def off(self):
        print(f"Mixer on pin {self.pin} is OFF")

# pH Adjuster Class
class PHAdjuster:
    def __init__(self, ph_sensor, acid_pump, base_pump, mixer, config):
        self.ph_sensor = ph_sensor
        self.acid_pump = acid_pump
        self.base_pump = base_pump
        self.mixer = mixer
        self.config = config
        self.buffer_capacities = []  # Store buffer capacities

    def estimate_buffer_capacity(self, current_ph, target_ph):
        """Estimates buffer capacity (β) using moles of acid/base and multiple data points."""
        # Select the appropriate pump and flow rate
        if current_ph > target_ph:
            pump = self.acid_pump
            flow_rate = self.config["acid_flow_rate"]
            concentration = self.config["acid_concentration"]  # Molarity of acid
        else:
            pump = self.base_pump
            flow_rate = self.config["base_flow_rate"]
            concentration = self.config["base_concentration"]  # Molarity of base

        self.mixer.on()  # Start mixing

        # Collect multiple data points
        ph_changes = []
        moles_added = []
        max_pumping_time = 60  # Maximum time to pump (seconds)
        start_time = datetime.datetime.now()

        while (datetime.datetime.now() - start_time).total_seconds() < max_pumping_time:
            # Add a small volume of acid/base
            volume_added = flow_rate * 1  # Add 1 second worth of solution
            moles = volume_added * concentration  # Calculate moles added
            pump.run(1)  # Run pump for 1 second

            # Allow time for mixing and stabilization
            time.sleep(self.config["mixing_time"])

            # Measure pH change
            new_ph = self.ph_sensor.read()
            ph_change = abs(new_ph - current_ph)
            ph_changes.append(ph_change)
            moles_added.append(moles)

            # Stop if pH change is significant
            if ph_change >= 0.5:
                break

        pump.off()
        self.mixer.off()

        # Calculate buffer capacity
        if len(ph_changes) > 0:
            total_moles = sum(moles_added)
            total_ph_change = sum(ph_changes)
            buffer_capacity = total_moles / total_ph_change if total_ph_change != 0 else 0
            return buffer_capacity, new_ph
        else:
            return 0, current_ph  # No change in pH
        
    def update_buffer_capacity(self, total_moles_added, pH_change):
        """
        Updates the buffer capacity based on the total moles added and pH change.
        """
        if pH_change > 1e-6:  # Avoid division by zero
            estimated_buffer = total_moles_added / pH_change
            self.buffer_capacities.append(estimated_buffer)
            print(f"Updated buffer capacity: {estimated_buffer} moles/pH unit")


    def calculate_adjustment_volume(self, current_ph, target_ph):
        """
        Calculate the volume of acid or base needed to adjust pH.
        Returns a tuple: (adjustment_type, volume)
        - adjustment_type: "acid" or "base"
        - volume: volume of solution to add (liters)
        """
        if not self.buffer_capacities:
            new_buffer_capacity, new_ph = self.estimate_buffer_capacity(current_ph, target_ph)
            self.buffer_capacities.append(new_buffer_capacity)
            current_ph = new_ph

        ph_change = abs(current_ph - target_ph)
        adjustment_moles = ph_change * self.buffer_capacities[-1]  # Use latest buffer capacity

        if current_ph > target_ph:
            adjustment_volume = adjustment_moles / self.config["acid_concentration"]
            return "acid", adjustment_volume  # Solution is too alkaline, add acid
        else:
            adjustment_volume = adjustment_moles / self.config["base_concentration"]
            return "base", adjustment_volume  # Solution is too acidic, add base
        


    def adjust_ph(self):
        """
        Adjust the pH of the solution incrementally.
        Returns True if successful, False if failed after max attempts.
        """
        current_ph = self.ph_sensor.read()
        if abs(current_ph - self.config["target_ph"]) <= self.config["ph_acceptable_margin"]:
            return True

        for attempt in range(self.config["max_attempts"]):
            stored_ph = current_ph
            adjustment_type, total_volume_needed = self.calculate_adjustment_volume(
                current_ph, self.config["target_ph"]
            )
            incremental_volume = total_volume_needed * self.config["increment_size"]

            # Select the appropriate pump and flow rate
            if adjustment_type == "acid":
                pump = self.acid_pump
                flow_rate = self.config["acid_flow_rate"]
            else:
                pump = self.base_pump
                flow_rate = self.config["base_flow_rate"]

            self.mixer.on()  # Start mixing
            total_moles_added = 0

            for i in range(int(1 / self.config["increment_size"])):  # Add in increments
                # Calculate moles of acid/base added
                if adjustment_type == "acid":
                    moles_added = incremental_volume * self.config["acid_concentration"]
                else:
                    moles_added = incremental_volume * self.config["base_concentration"]

                total_moles_added += moles_added

                # Calculate pump run time
                pump_time = incremental_volume / flow_rate

                # Add the increment
                pump.run(pump_time)  # Run pump for the calculated time
                time.sleep(self.config["mixing_time"])  # Allow time for mixing and stabilization
                current_ph = self.ph_sensor.read()  # Check pH

                # Check if pH is within acceptable margin
                if abs(current_ph - self.config["target_ph"]) <= self.config["ph_acceptable_margin"]:
                    # Update buffer capacity
                    pH_change = abs(current_ph - stored_ph)
                    self.update_buffer_capacity(total_moles_added, pH_change)
                    self.mixer.off()  # Stop mixing
                    return True  # pH adjustment successful

                # Check if pH has overshot the target
                if (adjustment_type == "acid" and current_ph < self.config["target_ph"]) or (adjustment_type == "base" and current_ph > self.config["target_ph"]):
                    print("pH overshot the target. Switching adjustment type.")
                    break  # Exit the increment loop and recalculate

            # If all increments are added but pH is still not reached
            self.mixer.off()  # Stop mixing
            time.sleep(self.config["settling_time"])  # Allow solution to settle
            current_ph = self.ph_sensor.read()  # Recheck pH

            # Check if pH is within acceptable margin after settling
            if abs(current_ph - self.config["target_ph"]) <= self.config["ph_acceptable_margin"]:
                # Update buffer capacity
                pH_change = abs(current_ph - stored_ph)
                self.update_buffer_capacity(total_moles_added, pH_change)
                return True  # pH adjustment successful

        # If max attempts reached and pH is still not adjusted
        print("pH adjustment failed after maximum attempts!")
        return False  # pH adjustment failed


# Irrigation System Class
class IrrigationSystem:
    def __init__(self, ph_adjuster, water_pump, irrigation_valves):
        self.ph_adjuster = ph_adjuster
        self.water_pump = water_pump
        self.irrigation_valves = irrigation_valves

    def run(self):
        # Step 1: Adjust pH
        if not self.ph_adjuster.adjust_ph():
            print("System halted due to pH adjustment failure.")
            return

        # Step 2: Start irrigation
        self.water_pump.on()
        for valve in self.irrigation_valves:
            valve.open()
            time.sleep(10)  # Example irrigation time
            valve.close()
        self.water_pump.off()

# Main Program
if __name__ == "__main__":
    # Initialize components
    ph_sensor = Sensor(pin=1)
    acid_pump = Pump(pin=2)
    base_pump = Pump(pin=3)
    mixer = Mixer(pin=4)
    water_pump = Pump(pin=5)
    irrigation_valves = [Pump(pin=6), Pump(pin=7)]  # Example valves

    # Initialize pH adjuster and irrigation system
    ph_adjuster = PHAdjuster(ph_sensor, acid_pump, base_pump, mixer, config)
    irrigation_system = IrrigationSystem(ph_adjuster, water_pump, irrigation_valves)

    # Run the irrigation system
    irrigation_system.run()