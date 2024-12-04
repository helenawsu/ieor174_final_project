from abc import ABC, abstractmethod

from abc import ABC, abstractmethod


# Base class for transport costs
class TransportCost:
    def __init__(self, time, distance, traffic_time=0):
        self.time = time
        self.distance = distance
        self.traffic_time = traffic_time
        self.uber_cost = self.calculate_uber_cost()

    def calculate_uber_cost(self):
        return 4.15 + 0.65 * 0.2 * self.distance + 0.65 * self.traffic_time

    def get_cost(self):
        return self.uber_cost
class UberAllCost(TransportCost):
    def __init__(self, time, distance, traffic_time=0):
        super().__init__(time, distance, traffic_time)
        self.safety_cost = 0
class UberBartMixCost(TransportCost):
    def __init__(self, time, safety_cost, distance=0, bart_cost=7.2, traffic_time=0):
        super().__init__(time, distance, traffic_time)
        self.safety_cost = safety_cost
        self.bart_cost = bart_cost

    def get_cost(self):
        return super().get_cost() + self.bart_cost
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
class Personas(ABC):
    def __init__(self, transportation_cost):
        self.transportation_cost = transportation_cost
    @abstractmethod
    def get_cost(self, time_to_money_conversion=0):
        pass
        #return self.transportation_cost.get_cost() + self.transportation_cost.safety_cost + self.transportation_cost.time * time_to_money_conversion


class TimePrioritizer(Personas):
    def get_cost(self, time_to_money_conversion):
        return (
            self.transportation_cost.get_cost()
            + self.transportation_cost.time * time_to_money_conversion
        )
class MoneyPrioritizer(Personas):
    def get_cost(self, time_to_money_conversion=0):
        return self.transportation_cost.get_cost()
class SafetyPrioritizer(Personas):
    def get_cost(self, time_to_money_conversion=0):
        return self.transportation_cost.get_cost() + self.transportation_cost.safety_cost

