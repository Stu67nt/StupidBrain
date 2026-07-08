import pyperclip
import math
import keyboard
import time
import scipy

# /execute in minecraft:overworld run tp @s 235.84 69.00 -195.63 -134.79 -31.61

# TEst pos 1
# /execute in minecraft:overworld run tp @s 1920.48 75.00 -1259.10 139.88 -31.30
# /execute in minecraft:overworld run tp @s 1960.78 68.00 -1301.01 132.21 -31.74
"""
TODO:
Coordinate snapping /
Nether coordines /
Ring additions /
"""

RING_REGIONS = [[1280, 2816, 3],   # Ring 1 - 3 Strongholds
				[4352, 5888, 6],   # Ring 2 - 6 Strongholds
				[7424, 8960, 10],  # Ring 3 - 10 Strongholds
				[10496, 12032, 15],# Ring 4 - 15 Strongholds
				[13568, 15104, 21],# Ring 5 - 21 Strongholds
				[16640, 18176, 28],# Ring 6 - 28 Strongholds
				[19712, 21248, 36],# Ring 7 - 36 Strongholds
				[22784, 24320, 9]  # Ring 8 - 9 Strongholds
				]

def precompute_g_set():
	def integrand(x_1, a): return (math.pow(1 + ((a * x_1) / (15 * math.sqrt(2))), 4.5) * math.pow(1 - ((a * x_1) / (15 * math.sqrt(2))),4.5))

	G_set = []
	for region in RING_REGIONS:
		ring_set = [0, 0, []]
		min_dist, max_dist = region[0], region[1]
		ring_set[0] = scipy.integrate.quad(integrand, (-15 * math.sqrt(2)) / min_dist, (15 * math.sqrt(2)) / min_dist, args=(min_dist))
		ring_set[1] = 1/(2*math.pi*(max_dist-min_dist))
		for x in range(-max_dist, max_dist + 1, 16):
			x_coord = x - (x % 16) + 8
			for z in range(-max_dist, max_dist + 1, 16):
				z_coord = z - (z % 16) + 8
				displacement = math.sqrt(x_coord * x_coord + z_coord * z_coord)
				if min_dist <= displacement <= max_dist:
					ring_set[2].append([x_coord, z_coord])
		G_set.append(ring_set)

	i = 0
	for reigon in G_set:
		raw_weight_total = 0
		for chunk in reigon[2]:
			displacement = math.sqrt((chunk[0] * chunk[0]) + (chunk[1] * chunk[1]))
			angle = math.atan2(-chunk[0], chunk[1])
			raw_weight = reigon[1]*(256/displacement)
			chunk.append(displacement)
			chunk.append(angle)
			chunk.append(raw_weight)
			raw_weight_total += raw_weight
		for chunk in reigon[2]:
			chunk.append(RING_REGIONS[i][2]*((chunk[4])/raw_weight_total))
			i+=1

	return G_set

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

def nether_coords(x, z):
	return x//8, z//8

def validate_result(x, z):
	displacement = math.sqrt(x*x + z*z)
	for i, ring in enumerate(RING_REGIONS):
		if ring[0] < displacement < ring[1]:
			return i+1
	return -1

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

		c_x, c_z = intersect_lines(gradient1, gradient2, constant1, constant2)
		print(f"Overworld coords: {c_x, c_z}")
		print(f"Nether coords: {nether_coords(c_x, c_z)}")
		ring = validate_result(c_x, c_z)
		if ring != -1:
			print(f"Calculated to be in ring {ring}")
		else:
			print(f"Likely an incorrect mesaurement")
