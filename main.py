import pyperclip
import math
import keyboard
import time
import scipy
import numpy

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

RING_REGIONS = [
	[1280, 2816, 3],  # Ring 1 - 3 Strongholds
	[4352, 5888, 6],  # Ring 2 - 6 Strongholds
	[7424, 8960, 10],  # Ring 3 - 10 Strongholds
	[10496, 12032, 15],  # Ring 4 - 15 Strongholds
	[13568, 15104, 21],  # Ring 5 - 21 Strongholds
	[16640, 18176, 28],  # Ring 6 - 28 Strongholds
	[19712, 21248, 36],  # Ring 7 - 36 Strongholds
	[22784, 24320, 9]  # Ring 8 - 9 Strongholds
				]

def integrand(x_1, a):
	val = (a * x_1) / (15 * numpy.sqrt(2))
	if val <= -1 or val >= 1:
		return 0
	return numpy.pow(1 + val, 4.5) * numpy.pow(1 - val,4.5)

def diff_ring_integrand(chunk_angle, chunk_displacement, min_dist, max_dist):
	denom = numpy.sin(-chunk_displacement)
	# prevent divide by 0 errors
	if round(denom, 8) == 0:
		return 0

	lb = chunk_displacement * numpy.sin(chunk_angle) / denom
	ub = chunk_displacement * numpy.sin(numpy.pi+chunk_angle) / denom

	if lb > ub:
		ub, lb = lb, ub

	def radial_cdf(R):
		if R < min_dist: return 0.0
		if R > max_dist: return 1.0
		return (R - min_dist)/(max_dist - min_dist)

	return (radial_cdf(ub) - radial_cdf(lb))/(2*numpy.pi)

def precompute_chance_calc(x_coord, z_coord, reigon_num):
	displacement = numpy.sqrt(pow(x_coord,2)+pow(z_coord, 2))
	p_closest = 1
	for i, region in enumerate(RING_REGIONS):
		if i != reigon_num:
			min_dist, max_dist, strng_count = region[0], region[1], region[2]
			if displacement <= min_dist:
				p_further = 0.0
			elif displacement >= max_dist:
				p_further = 1.0
			else:
				p_further = (displacement - min_dist) / (max_dist - min_dist)
			p_closer = numpy.pow(1-p_further, strng_count)
			p_closest *= p_closer
	return p_closest

def precompute_g_set():
	G_set = []
	i = 0
	for region in RING_REGIONS:
		raw_weight_total = 0
		ring_set = [0, 0, []]
		min_dist, max_dist = region[0], region[1]
		ring_set[0] = scipy.integrate.quad(integrand, (-15 * numpy.sqrt(2)) / min_dist, (15 * numpy.sqrt(2)) / min_dist, args=(min_dist))
		ring_set[1] = 1/(2*numpy.pi*(max_dist-min_dist))
		for x in range(-max_dist, max_dist + 1, 16):
			x_coord = x - (x % 16) + 8
			for z in range(-max_dist, max_dist + 1, 16):
				z_coord = z - (z % 16) + 8
				displacement = numpy.sqrt(pow(x_coord, 2) + pow(z_coord, 2))
				if min_dist <= displacement <= max_dist:
					closest_factor = precompute_chance_calc(x_coord, z_coord, i)
					angle = numpy.atan2(-x_coord, z_coord)
					raw_weight = ring_set[1] * (256 / displacement) * closest_factor
					ring_set[2].append((x_coord, z_coord, displacement, angle, raw_weight))
		ring_set[2] = numpy.array(ring_set[2], dtype=[("x_coord", "f8"), ("z_coord", numpy.float64), ("displacement", numpy.float64), ("angle", numpy.float64), ("raw_weight", numpy.float64)])
		raw_weight_total = numpy.sum(ring_set[2]["raw_weight"])
		if raw_weight_total > 0:
			ring_set[2]["raw_weight"] = region[2]*(ring_set[2]["raw_weight"]/raw_weight_total)
		else:
			ring_set[2]["raw_weight"] = 0
		i += 1
		G_set.append(ring_set)
		print(f"{i}/{len(RING_REGIONS)}")
	return G_set

def find_probablilty(player_pos: tuple, g_set, strd_dev, throws=1):
	"""
	:param player_pos: Expects a tuple of following (x, y, degree yaw angle)
	:param g_set:
	:param strd_dev:
	:param throws:
	:return:
	"""
	player_angle = numpy.radians(player_pos[2])
	strd_dev = numpy.radians(strd_dev)
	i = 0
	total_prob = 0
	for reigon in g_set:
		optimal_angle = numpy.atan2(-(reigon[2]["x_coord"]-player_pos[0]), reigon[2]["z_coord"]-player_pos[1])
		angle_diff = ((-1*optimal_angle)+player_angle+numpy.pi)%(2*numpy.pi)-numpy.pi
		chance = (1/(strd_dev*numpy.sqrt(2 * numpy.pi)))*numpy.exp(-(numpy.pow(angle_diff, 2))/(2*pow(strd_dev, 2)))
		reigon[2]["raw_weight"] *= chance
		total_prob += numpy.sum(reigon[2]["raw_weight"])
		i+=1

	for reigon in g_set:
		reigon[2]["raw_weight"] /= total_prob
	return g_set

def extract_best(g_set):
	best_val = -1
	x = 0
	z = 0
	for reigon in g_set:
		i = numpy.argmax(reigon[2]["raw_weight"])
		if best_val < numpy.max(reigon[2][i]["raw_weight"]):
			best_val = reigon[2][i]["raw_weight"]
			x = reigon[2][i]["x_coord"]
			z = reigon[2][i]["z_coord"]
	return x,z, best_val

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
	return -1/numpy.tan(numpy.radians(pitch))

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
	displacement = numpy.sqrt(x*x + z*z)
	for i, ring in enumerate(RING_REGIONS):
		if ring[0] < displacement < ring[1]:
			return i+1
	return -1

def main():
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

def main_probabilistic():
	g_set = precompute_g_set()
	count = 0
	while True:
		print("waiting one")
		keyboard.wait("f3+c")
		time.sleep(0.1)
		command1 = read_clipboard()

		if command1 != "invalid":
			x1, y1, z1, yaw1, pitch1 = parse_result(command1)

			print(x1, y1, z1, yaw1, pitch1)
			t1 = time.time()
			g_set = find_probablilty((x1, z1, yaw1), g_set, 0.1)
			count += 1
			c_x, c_z, chance= extract_best(g_set)
			print(time.time() - t1)
			print(f"Overworld coords: {int(c_x), int(c_z)}")
			print(f"Nether coords: {nether_coords(c_x, c_z)}")
			print(chance)
			ring = validate_result(c_x, c_z)
			if ring != -1:
				print(f"Calculated to be in ring {ring}")
			else:
				print(f"Likely an incorrect mesaurement")

main_probabilistic()