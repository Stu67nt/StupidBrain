import time
import random
from PySide6 import QtCore
from PySide6.QtCore import QObject, Signal, Slot
from py4j.java_gateway import JavaGateway


class SearchSignals(QObject):
	results = Signal(list)

class SeedSearch(QtCore.QRunnable):
	def __init__(self, struct, entry):
		super().__init__()
		self.java_gw = entry
		self.signal = SearchSignals()
		self.struct = struct
		self.start = random.randint(1, 999999999999999)
		self.end = self.start + 100

	@Slot()
	def run(self):
		match self.struct:
			case "Village":
				results = []
				while results == []:
					results = self.search_VIL_seeds(self.java_gw, self.start, self.end)
					self.start += 100
					self.end += 100
			case "Shipwreck":
				results = []
				while results == []:
					results = self.search_SW_seeds(self.java_gw, self.start, self.end)
					self.start += 100
					self.end += 100
			case "Desert Temple":
				results = []
				while results == []:
					results = self.search_DT_seeds(self.java_gw, self.start, self.end)
					self.start += 100
					self.end += 100
			case "Buried Treasure":
				results = []
				while results == []:
					results = self.search_BT_seeds(self.java_gw, self.start, self.end)
					self.start += 100
					self.end += 100
			case "Ruined Portal":
				results = []
				while results == []:
					results = self.search_RP_seeds(self.java_gw, self.start, self.end)
					self.start += 100
					self.end += 100
			case _:
				results = []
		self.signal.results.emit(results)


	@Slot()
	def search_DT_seeds(self, entry, start = 0, end = 500):
		all_seeds = []
		print("Starting")
		for seed in range(start, end):
			t1 = time.time()
			valid_seeds = entry.DesertTempleChecker(seed)
			if len(valid_seeds) > 0:
				print(f"Seed {seed} {valid_seeds}")
				all_seeds.extend(valid_seeds)
			if time.time()-t1 > 0.25: print(round(time.time()-t1, 2))
		return all_seeds

	@Slot()
	def search_SW_seeds(self, entry, start = 0, end = 1000):
		all_seeds = []
		print("Starting")
		for seed in range(start, end):
			t1 = time.time()
			valid_seeds = entry.ShipwreckChecker(seed)
			if len(valid_seeds) > 0:
				print(f"Seed {seed} {valid_seeds}")
				all_seeds.extend(valid_seeds)
			if time.time()-t1 > 0.25: print(round(time.time()-t1, 2))
		return all_seeds

	@Slot()
	def search_BT_seeds(self, entry, start = 0, end = 1000):
		all_seeds = []
		print("Starting")
		for seed in range(start, end):
			t1 = time.time()
			valid_seeds = entry.BuriedTreasureChecker(seed)
			if len(valid_seeds) > 0:
				print(f"Seed {seed} {valid_seeds}")
				all_seeds.extend(valid_seeds)
			if time.time()-t1 > 0.25: print(round(time.time()-t1, 2))
		return all_seeds

	@Slot()
	def search_RP_seeds(self, entry, start = 0, end = 1000):
		all_seeds = []
		print("Starting")
		for seed in range(start, end):
			t1 = time.time()
			valid_seeds = entry.RuinedPortalChecker(seed)
			if len(valid_seeds) > 0:
				print(f"Seed {seed} {valid_seeds}")
				all_seeds.extend(valid_seeds)
			if time.time()-t1 > 0.25: print(round(time.time()-t1, 2))
		return all_seeds

	@Slot()
	def search_VIL_seeds(self, entry, start = 0, end = 1000):
		all_seeds = []
		print("Starting")
		for seed in range(start, end):
			t1 = time.time()
			valid_seeds = entry.VillageChecker(seed)
			if len(valid_seeds) > 0:
				print(f"Seed {seed} {valid_seeds}")
				all_seeds.extend(valid_seeds)
			if time.time()-t1 > 0.25: print(round(time.time()-t1, 2))
		return all_seeds