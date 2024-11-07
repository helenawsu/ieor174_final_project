class Personas:
    def __init__(self, time_cost: float, money_cost: float, safety_cost: float):
        self.time_cost = time_cost
        self.money_cost = money_cost
        self.safety_cost = safety_cost
    
    def get_total_cost(self):
        """
        Calculates a simple sum of all costs for a base total cost.
        """
        return self.time_cost + self.money_cost + self.safety_cost
    
    def __str__(self):
        return (f"Time Cost: {self.time_cost}, Money Cost: {self.money_cost}, "
                f"Safety Cost: {self.safety_cost}")


class TimePrioritizer(Personas):
    def __init__(self, time_cost: float, money_cost: float, safety_cost: float):
        super().__init__(time_cost, money_cost, safety_cost)
    
    def prioritize(self):
        return f"Prioritizing time with time cost: {self.time_cost}"


class MoneyPrioritizer(Personas):
    def __init__(self, time_cost: float, money_cost: float, safety_cost: float):
        super().__init__(time_cost, money_cost, safety_cost)
    
    def prioritize(self):
        return f"Prioritizing money with money cost: {self.money_cost}"


class SafetyPrioritizer(Personas):
    def __init__(self, time_cost: float, money_cost: float, safety_cost: float):
        super().__init__(time_cost, money_cost, safety_cost)
    
    def prioritize(self):
        return f"Prioritizing safety with safety cost: {self.safety_cost}"

time_persona = TimePrioritizer(5, 10, 3)
money_persona = MoneyPrioritizer(6, 2, 4)
safety_persona = SafetyPrioritizer(8, 12, 1)

print(time_persona)
print(time_persona.prioritize())
print(money_persona)
print(money_persona.prioritize())
print(safety_persona)
print(safety_persona.prioritize())
