import random

import pyperclip
import math
import keyboard
import time
from calc_math import *

# /tp @s -1816 ~ 120

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
			angle_diff = measured_angle-optimal_angle
			if abs(math.degrees(angle_diff)) < 2:
				measurements.append((math.degrees(angle_diff))**2)
				if len(measurements) > 1:
					strd_dev = math.sqrt(sum(measurements)/(len(measurements)-1))
			else:
				print("Too inaccurate measurement ignored")
			tp_x, tp_z = tp_position(coords[0], coords[1])
			print(strd_dev)
			print("/tp @s %s ~ %s" % (tp_x, tp_z))

ting()

