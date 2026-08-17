import random
import math
import keyboard
import time
from PySide6 import QtCore
from PySide6.QtCore import Slot, QObject, Signal

from calc_math import *

# Used for coms between thread and GUI
class ConfigSignals(QObject):
	results = Signal(float, str)

class StrdDevCalc(QtCore.QRunnable):
	def __init__(self, stronghold_coords):
		super().__init__()

		self.signals = ConfigSignals()
		self.strd_dev = get_strd_dev()
		self.coords = stronghold_coords
		self.all_commands_data = []
		self.measurements = []
		self.tp_command = ""
		self.is_running = True

	@Slot()
	def run(self):
		self.all_commands_data = []
		print("hai")
		while self.is_running:
			try:
				keyboard.wait("f3+c")
			except:
				pass
			if not self.is_running:
				break
			time.sleep(0.02)
			command1 = read_clipboard()
			if command1 != "invalid" and self.is_running:
				x, y, z, yaw, pitch = command1
				if [x, y, z, yaw, pitch] not in self.all_commands_data:
					self.all_commands_data.append([x, y, z, yaw, pitch])
					self.strd_dev, self.tp_command, self.measurements = calc_strd_dev(self.coords, [x, z, yaw],
																					  self.measurements)
					self.signals.results.emit(self.strd_dev, self.tp_command)

def standarise_degrees(mc_ang:float):
	"""Keeps angles between minecraft's normal -180 - 180 range"""
	while mc_ang < -180:
		mc_ang += 360
	while mc_ang >= 180:
		mc_ang -= 360
	return mc_ang

def filter_command(cmd):
	parts = cmd.split(" ")
	if len(parts) != 5:
		return []
	if parts[0] != "/tp":
		return []
	if parts[1] != "@s":
		return []
	if parts[3] != "~":
		return []
	return [int(parts[2]), int(parts[4])]

def tp_position(stronghold_x, stronghold_z):
	MAGNITUDE = 200
	direction = math.radians(random.randint(0, 360))
	new_x = stronghold_x + (MAGNITUDE*math.cos(direction))
	new_z = stronghold_z + (MAGNITUDE*math.sin(direction))
	return round(new_x, 3), round(new_z, 3)

def calc_strd_dev(stronghold_coords, player_pos_data, measurements):
	x, z, yaw = player_pos_data
	strd_dev = get_strd_dev()
	optimal_angle = (math.atan2(-(stronghold_coords[0] - x), stronghold_coords[1] - z))
	measured_angle = math.radians(standarise_degrees(yaw))
	angle_diff = measured_angle - optimal_angle
	if abs(math.degrees(angle_diff)) < 2:
		measurements.append((math.degrees(angle_diff)) ** 2)
		if len(measurements) > 1:
			strd_dev = math.sqrt(sum(measurements) / (len(measurements) - 1))
	else:
		print("Too inaccurate measurement ignored")
	tp_x, tp_z = tp_position(stronghold_coords[0], stronghold_coords[1])
	print(strd_dev)
	tp_command = f"/tp @s {tp_x} ~ {tp_z}"
	return strd_dev, tp_command, measurements

def ting():
	coords = []
	measurements = []
	strd_dev = 0
	while coords == []:
		stronghold_pos_command = input("Paste in the stronghold tp command: ")
		coords = filter_command(stronghold_pos_command)
	while True:
		print("waiting one")
		keyboard.wait("f3+c")
		time.sleep(0.02)
		command1 = read_clipboard()

		if command1 != "invalid":
			x1, y1, z1, yaw1, pitch1 = command1
			optimal_angle = (math.atan2(-(coords[0] - x1), coords[1] - z1))
			measured_angle = math.radians(standarise_degrees(yaw1))
			angle_diff = measured_angle - optimal_angle
			if abs(math.degrees(angle_diff)) < 2:
				measurements.append((math.degrees(angle_diff)) ** 2)
				if len(measurements) > 1:
					strd_dev = math.sqrt(sum(measurements) / (len(measurements) - 1))
			else:
				print("Too inaccurate measurement ignored")
			tp_x, tp_z = tp_position(coords[0], coords[1])
			print(strd_dev)
			print("/tp @s %s ~ %s" % (tp_x, tp_z))

if __name__ == "__main__":
	ting()

