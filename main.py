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
optimise precompute (turns out its alr pretty decent)

"""

RING_REGIONS = [[1280, 2816, 3],   # Ring 1 - 3 Strongholds
				[4352, 5888, 6],   # Ring 2 - 6 Strongholds
				]

def integrand(x_1, a):
	val = (a * x_1) / (15 * math.sqrt(2))
	if val <= -1 or val >= 1:
		return 0
	return math.pow(1 + val, 4.5) * math.pow(1 - val,4.5)

def diff_ring_integrand(chunk_angle, chunk_displacement, min_dist, max_dist):
	denom = math.sin(-chunk_displacement)
	# prevent divide by 0 errors
	if round(denom, 8) == 0:
		return 0

	lb = chunk_displacement * math.sin(chunk_angle) / denom
	ub = chunk_displacement * math.sin(math.pi+chunk_angle) / denom

	if lb > ub:
		ub, lb = lb, ub

	def radial_cdf(R):
		if R < min_dist: return 0.0
		if R > max_dist: return 1.0
		return (R - min_dist)/(max_dist - min_dist)

	return (radial_cdf(ub) - radial_cdf(lb))/(2*math.pi)

def precompute_chance_calc(x_coord, z_coord, reigon_num):
	displacement = math.sqrt(pow(x_coord,2)+pow(z_coord, 2))
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
			p_closer = math.pow(1-p_further, strng_count)
			p_closest *= p_closer
	return p_closest

def precompute_g_set():
	G_set = []
	i = 0
	for region in RING_REGIONS:
		raw_weight_total = 0
		ring_set = {"angle_density": 0,
					"joint_desnity": 0,
					"chunk_info": []}
		min_dist, max_dist = region[0], region[1]
		ring_set["angle_density"] = scipy.integrate.quad(integrand, (-15 * math.sqrt(2)) / min_dist, (15 * math.sqrt(2)) / min_dist, args=(min_dist))
		ring_set["joint_desnity"] = 1/(2*math.pi*(max_dist-min_dist))
		for x in range(-max_dist, max_dist + 1, 16):
			x_coord = x - (x % 16) + 8
			for z in range(-max_dist, max_dist + 1, 16):
				z_coord = z - (z % 16) + 8
				displacement = math.sqrt(pow(x_coord, 2) + pow(z_coord, 2))
				if min_dist <= displacement <= max_dist:
					closest_factor = precompute_chance_calc(x_coord, z_coord, i)
					angle = math.atan2(-x_coord, z_coord)
					raw_weight = ring_set["joint_desnity"] * (256 / displacement) * closest_factor
					ring_set["chunk_info"].append({"coords": [x_coord, z_coord],
												   "displacment": displacement,
												   "angle": angle,
												   "weight": raw_weight})
					raw_weight_total += raw_weight
		if raw_weight_total > 0:
			for chunk in ring_set["chunk_info"]:
				chunk["weight"] = region[2]*((chunk["weight"])/raw_weight_total)
		else:
			for chunk in ring_set["chunk_info"]:
				chunk["weight"] = 0
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
	player_angle = math.radians(player_pos[2])
	strd_dev = math.radians(strd_dev)
	i = 0
	total_prob = 0
	for reigon in g_set:
		for chunk in reigon["chunk_info"]:
			optimal_angle = math.atan2(-(chunk["coords"][0]-player_pos[0]), chunk["coords"][1]-player_pos[1])
			angle_diff = player_angle - optimal_angle
			if angle_diff > math.pi:
				angle_diff = angle_diff - 2*math.pi
			elif angle_diff < -math.pi:
				angle_diff = 2*math.pi + angle_diff
			chance = (1/(strd_dev*math.sqrt(2 * math.pi)))*math.exp(-(pow(angle_diff, 2))/(2*pow(strd_dev, 2)))
			displacement = math.sqrt(pow(chunk["coords"][0]-player_pos[0], 2) + pow(chunk["coords"][1]-player_pos[1], 2))
			chunk["weight"] *= chance
			total_prob += chunk["weight"]
		i+=1

	for reigon in g_set:
		for chunk in reigon["chunk_info"]:
			chunk["weight"] /= total_prob
	return g_set

def extract_best(g_set):
	best_val = -1
	x = 0
	z = 0
	for reigon in g_set:
		for chunk in reigon["chunk_info"]:
			if chunk["weight"] > best_val:
				best_val = chunk["weight"]
				x = chunk["coords"][0]
				z = chunk["coords"][1]
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
			print(f"Overworld coords: {c_x, c_z}")
			print(f"Nether coords: {nether_coords(c_x, c_z)}")
			print(chance)
			ring = validate_result(c_x, c_z)
			if ring != -1:
				print(f"Calculated to be in ring {ring}")
			else:
				print(f"Likely an incorrect mesaurement")

main_probabilistic()