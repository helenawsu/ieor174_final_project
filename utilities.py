from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from scipy.interpolate import Akima1DInterpolator
import numpy as np

import numpy as np
from scipy.interpolate import Akima1DInterpolator


class UberAll:
    def __init__(self, time_to_cost_factor, distance):
        # Start: Downtown San Jose
        # End: Downtown Berkeley BART station
        # Data range: Jan 6 - Jan 13
        self.time_to_cost_factor = time_to_cost_factor
        self.distance = distance
        self.fare_data = {
            "time": ["5:00 AM", "8:00 AM", "1:00 PM", "5:00 PM", "9:00 PM"],
            "mon": [60.97, 72.94, 68.92, 82.93, 66.93],
            "wed": [61.98, 73.95, 68.96, 73.94, 67.95],
            "fri": [61.97, 70.97, 69.94, 74.92, 76.97],
            "sat": [65.98, 68.94, 68.92, 74.94, 68.95],
            "sun": [67.90, 68.99, 67.99, 73.94, 77.99],
        }
        self.time_data = {
            "time": ["5:00 AM", "8:00 AM", "1:00 PM", "5:00 PM", "9:00 PM"],
            "mon": [50, 75, 60, 89, 52],
            "wed": [50, 75, 64, 100, 55],
            "fri": [50, 66, 66, 94, 54],
            "sat": [50, 50, 58, 67, 53],
            "sun": [50, 49, 55, 62, 51],
        }

    def interpolate_line(self, x, y, hour):
        """
        Interpolates values using Akima interpolation for a given hour.
        """
        # Convert time strings to numerical values (5:00 AM = 5, 9:00 PM = 21)
        time_numeric = np.array([5, 8, 13, 17, 21])
        interpolator = Akima1DInterpolator(time_numeric, y)

        if hour < 5 or hour > 21:
            raise ValueError("Hour must be between 5 and 21 (inclusive).")

        return interpolator(hour)

    def fare_interpolator(self, hour, is_weekday=True):
        """
        Calculates the average cost based on the day type and interpolates for a given hour.
        """
        # Determine which days to use
        if is_weekday:
            weekdays = ["mon", "wed", "fri"]
            data = [self.fare_data[day] for day in weekdays]
        else:
            weekends = ["sat", "sun"]
            data = [self.fare_data[day] for day in weekends]
        # Calculate the average costs across the selected days
        avg_cost = np.mean(data, axis=0)
        # Interpolate the average cost for the given hour
        return self.interpolate_line(self.fare_data["time"], avg_cost, hour)

    def time_interpolator(self, hour, is_weekday=True):
        """
        Calculates the average time based on the day type and interpolates for a given hour.
        """
        # Determine which days to use
        if is_weekday:
            weekdays = ["mon", "wed", "fri"]
            data = [self.time_data[day] for day in weekdays]
        else:
            weekends = ["sat", "sun"]
            data = [self.time_data[day] for day in weekends]
        # Calculate the average times across the selected days
        avg_time = np.mean(data, axis=0)
        # Interpolate the average time for the given hour
        return self.interpolate_line(self.time_data["time"], avg_time, hour) / 60

    def get_cost(self, hour, is_weekday):
        return (
            self.distance
            + self.fare_interpolator(hour, is_weekday)
            + self.time_interpolator(hour, is_weekday) * self.time_to_cost_factor
        )


# Base class for transport costs
class TransportCost:
    def __init__(self, time, distance, traffic_time=0):
        self.time = time
        self.distance = distance
        self.traffic_time = traffic_time
        self.uber_cost = self.calculate_uber_cost()

    def calculate_uber_cost(self):
        return (
            4.15 + 0.52 * 5 * self.distance
        )  # 0.52 is emprically scaled down from 0.65 which is sf taxi rates

    def get_cost(self):
        return self.uber_cost


class UberAllCost(TransportCost):
    def __init__(self, time, distance, traffic_time=0):
        super().__init__(time, distance, traffic_time)
        self.safety_cost = 0


class UberBartMix:
    def __init__(self, time_to_cost_factor, distance, safety_cost, bart_cost=7.2):
        self.safety_cost = safety_cost
        self.bart_cost = bart_cost
        self.time_to_cost_factor = time_to_cost_factor
        self.distance = distance

    def get_fare(self):
        return (
            self.bart_cost + 4.15 + 0.52 * 5 * self.distance
        )  # 0.52 is emprically scaled down from 0.65 which is sf taxi rates

    def get_time(self):
        # breakdown: bart 60min, uber to bart 30min, rest 30min for waiting / to final dest
        return 120 / 60  # in hour

    def get_cost(self):
        return (
            self.safety_cost
            + self.get_fare()
            + self.time_to_cost_factor * self.get_time()
        )


class Drive:
    def __init__(self, time_to_cost_factor, inconvenience_fee):
        self.time_to_cost_factor = time_to_cost_factor
        self.inconvenience_fee = inconvenience_fee
        self.ua = UberAll(self.time_to_cost_factor, distance=0)
        self.gas_cost = 10  # At 50 miles, 23 miles per gallon, $4.5/gallon

    def get_time(self, hour, is_weekday=True):
        return self.ua.time_interpolator(hour, is_weekday)  # unit is hour

    def get_cost(self, hour, is_weekday):
        return (
            self.inconvenience_fee
            + self.get_time(hour, is_weekday) * self.time_to_cost_factor
            + self.gas_cost
        )


class Population:
    def __init__(self, car_percent: float):
        self.car_percent = car_percent


class Personas(ABC):
    def __init__(self, transportation_cost):
        self.transportation_cost = transportation_cost

    @abstractmethod
    def get_cost(self, time_to_money_conversion=0):
        pass
        # return self.transportation_cost.get_cost() + self.transportation_cost.safety_cost + self.transportation_cost.time * time_to_money_conversion


