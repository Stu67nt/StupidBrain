import time

def search_DT_seeds(entry):
	all_seeds = []
	print("Starting")
	for seed in range(0, 1000):
		valid_seeds = entry.DesertTempleChecker(seed)
		if len(valid_seeds) > 0:
			print(f"Seed {seed} {valid_seeds}")
			all_seeds.extend(valid_seeds)
	return all_seeds

def search_SW_seeds(entry):
	all_seeds = []
	print("Starting")
	for seed in range(0, 1000):
		t1 = time.time()
		valid_seeds = entry.ShipwreckChecker(seed)
		if len(valid_seeds) > 0:
			print(f"Seed {seed} {valid_seeds}")
			all_seeds.extend(valid_seeds)
		if time.time()-t1 > 0.5: print(round(time.time()-t1, 2))
	return all_seeds

def search_BT_seeds(entry):
	all_seeds = []
	print("Starting")
	for seed in range(0, 100000):
		t1 = time.time()
		valid_seeds = entry.BuriedTreasureChecker(seed)
		if len(valid_seeds) > 0:
			print(f"Seed {seed} {valid_seeds}")
			all_seeds.extend(valid_seeds)
		if time.time()-t1 > 0.5: print(round(time.time()-t1, 2))
	return all_seeds