import pyperclip
import math
import keyboard
import time

# /execute in minecraft:overworld run tp @s 235.84 69.00 -195.63 -134.79 -31.61

# TEst pos 1
# /execute in minecraft:overworld run tp @s 1920.48 75.00 -1259.10 139.88 -31.30
# /execute in minecraft:overworld run tp @s 1960.78 68.00 -1301.01 132.21 -31.74
"""
TODO:
Coordinate snapping /
Nether coordines
Ring additions
"""

def read_clipboard():
	result = pyperclip.paste()
	if result.startswith("/execute in minecraft"):
		return result
	else:
		return "invalid"

def parse_result(command):
	postion_dat = command.split(" ")[-5:]
	x = float(postion_dat[0])
	y = float(postion_dat[1])
	z = float(postion_dat[2])
	yaw = float(postion_dat[3])
	pitch = float(postion_dat[4])
	return x,y,z,yaw,pitch

def get_gradient(pitch):
	return -1/math.tan(math.radians(pitch))

def get_constant(x, z, gradient):
	return z-(gradient*x)

def intersect_lines(g1, g2, c1, c2):
	x = int((c2-c1)/(g1-g2))
	z = int((g1*x)+c1)
	x_snap = x - (x % 16) + 8
	z_snap = z - (z % 16) + 8
	return x_snap, z_snap



while True:
	print("waiting one")
	keyboard.wait("f3+c")
	time.sleep(0.1)
	command1 = read_clipboard()
	print("waiting two")
	keyboard.wait("f3+c")
	time.sleep(0.1)
	command2 = read_clipboard()

	if command1 != "invalid" and command2 != "invalid":
		x1, y1, z1, yaw1, pitch1 = parse_result(command1)
		x2, y2, z2, yaw2, pitch2 = parse_result(command2)

		print(x1, y1, z1, yaw1, pitch1)
		print(x2, y2, z2, yaw2, pitch2)

		gradient1 = get_gradient(yaw1)
		gradient2 = get_gradient(yaw2)

		constant1 = get_constant(x1, z1, gradient1)
		constant2 = get_constant(x2, z2, gradient2)

		x, z = intersect_lines(gradient1, gradient2, constant1, constant2)
		print(x, z)