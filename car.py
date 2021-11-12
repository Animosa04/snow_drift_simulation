from parameters import MAX_CAR_BATTERY_LEVEL, CAR_BATTERY_DECREASE_WHEN_TURN_ON_HEATER


class Car(object):
    def __init__(self, env):
        self.env = env
        self.battery_level = MAX_CAR_BATTERY_LEVEL

    def decrease_battery_level(self):
        self.battery_level -= CAR_BATTERY_DECREASE_WHEN_TURN_ON_HEATER
        if self.battery_level < 0:
            self.battery_level = 0
