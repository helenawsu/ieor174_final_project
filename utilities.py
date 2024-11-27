class TransportCost:
    def __init__(self, uber_all_time, uber_bart_mix_time, safety_cost, uber_cost_per_mile, uber_distance=0):
        self.uber_all_time = uber_all_time
        self.uber_bart_mix_time = uber_bart_mix_time
        self.uber_distance = uber_distance
        self.uber_cost_per_mile = uber_cost_per_mile
        self.monetary_cost = uber_cost_per_mile * uber_distance
        self.safety_cost = safety_cost

    def get_cost(self, time_to_money_conversion):
        return self.monetary_cost + self.time_cost * time_to_money_conversion
class Population:
    def __init__(self, TimePrioritizer_percentage: float, MoneyPrioritizer_percentage: float, SafetyPrioritizer_percentage: float):
        total_percentage = TimePrioritizer_percentage + MoneyPrioritizer_percentage + SafetyPrioritizer_percentage
        if not abs(total_percentage - 1.0) < 1e-5:  # have some tolerance
            raise ValueError(
                f"Percentages must add up to 1. Given: "
                f"{TimePrioritizer_percentage} (time), "
                f"{MoneyPrioritizer_percentage} (money), "
                f"{SafetyPrioritizer_percentage} (safety). Total: {total_percentage}"
            )
        
        self.time_prioritizer_percentage = TimePrioritizer_percentage
        self.money_prioritizer_percentage = MoneyPrioritizer_percentage
        self.safety_prioritizer_percentage = SafetyPrioritizer_percentage
class Personas:
    def __init__(self, transpotation_cost):
        self.transport_cost = transpotation_cost
        self.monetary_cost = self.transport_cost.monetary_cost
        self.uber_all_time = self.transport_cost.uber_all_time
        self.uber_bart_mix_time = self.transport_cost.uber_bart_mix_time
        self.distance = self.transport_cost.uber_distance
        self.uber_cost_per_mile = self.transport_cost.uber_cost_per_mile
        self.safety_cost = self.transport_cost.safety_cost
    def __str__(self):
        return (f"Time Cost: {self.placeholder}")
class TimePrioritizer(Personas):
    def __init__(self, transpotation_cost):
        super().__init__(transpotation_cost)
    def uber_all_cost(self, time_to_money_conversion):
        # this is hard coded, change later
        return 80 + self.uber_all_time * time_to_money_conversion
    def uber_bart_mix_cost(self, time_to_money_conversion):
        return self.uber_cost_per_mile * self.distance + self.uber_bart_mix_time * time_to_money_conversion



class MoneyPrioritizer(Personas):
    def __init__(self, transpotation_cost):
        super().__init__(transpotation_cost)
    def uber_all_cost(self):
        # this is hard coded, change later
        return 80
    def uber_bart_mix_cost(self):
        return self.uber_cost_per_mile * self.distance


class SafetyPrioritizer(Personas):
    def __init__(self, transpotation_cost):
        super().__init__(transpotation_cost)
    def uber_all_cost(self):
        # this is hard coded, change later
        return 80 + self.safety_cost
    def uber_bart_mix_cost(self):
        return self.uber_cost_per_mile * self.distance + self.safety_cost


# time_persona = TimePrioritizer(5, 10, 3)
# money_persona = MoneyPrioritizer(6, 2, 4)
# safety_persona = SafetyPrioritizer(8, 12, 1)

# print(time_persona)
# print(time_persona.prioritize())
# print(money_persona)
# print(money_persona.prioritize())
# print(safety_persona)
# print(safety_persona.prioritize())
