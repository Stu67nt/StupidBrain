import math
import sys
from calc_math import *
from gui import *
from seedsearch import *
from strd_dev_calc import *
from PySide6.QtGui import QIcon
from PySide6 import QtWidgets
from PySide6.QtCore import Slot, QObject, Signal, Qt

# Classes for sending outputs to GUI thread
class CalcSignals(QObject):
	results = Signal(list, list, bool)

class LogSignals(QObject):
	output = Signal(str)

class Calc(QtCore.QRunnable):
	def __init__(self, g_set: list):
		super().__init__()
		# for sending outputs to GUI thread
		self.signals = CalcSignals()
		self.logger = LogSignals()
		self.g_set = g_set
		self.locked_angle = False
		self.results = None
		self.changing_dev = False

	def ring_overlap(self, sr1: list[int], sr2: list[int]) -> bool:
		"""
		Checking if 2 rings overlap
		:param sr1: candidate ring
		:param sr2: comparison ring
		:return: bool deciding if they overlap
		"""
		for r in sr1:
			if r in sr2:
				return True
		return False

	def lock_angle_calcs(self, command: str) -> list[QTableWidgetItem]:
		"""
		Computes output when we are not adjusting chances.
		:param command: copied f3+c msg
		:return: List of
		"""
		# Test commands
		# /execute in minecraft:overworld run tp @s 1920.48 75.00 -1259.10 139.88 -31.30
		# /execute in minecraft:the_nether run tp @s 77.78 50.00 311.31 74.90 6.46
		parts = command.split(" ")
		parts[2] = parts[2].split(":")
		dimension, x, z, yaw = parts[2][1], float(parts[6]), float(parts[8]), float(parts[9])
		display_lock = []

		for i, pos in enumerate(self.results):
			if dimension == "the_nether":
				x1, z1 = nether_coords(pos[0], pos[1])
			else:
				x1, z1 = pos[0], pos[1]
			distance = math.sqrt(pow(x - x1, 2) + pow(z - z1, 2))
			curr_trav_angle = math.degrees(math.atan2(-(x1 - x), (z1 - z)))
			trav_face_diff = standarise_degrees(yaw) - standarise_degrees(curr_trav_angle)
			trav_face_diff = (trav_face_diff + 180) % 360 - 180
			angle_shift = f" <= {abs(round(trav_face_diff, 1))}" if trav_face_diff >= 0 else f" => {abs(round(trav_face_diff, 1))}"
			display_lock.append([QTableWidgetItem(str((pos[0], pos[1]))), QTableWidgetItem(str(round(pos[4] * 100, 2))),
					 QTableWidgetItem(str(round(distance))), QTableWidgetItem(str(nether_coords(pos[0], pos[1]))),
					 QTableWidgetItem(f"{round(curr_trav_angle, 1)}  ({angle_shift})")])
		return display_lock


	@Slot()
	def run(self):
		ring = 0
		self.all_commands_data = []
		while True:
			try:
				keyboard.wait("f3+c")
			except:
				pass
			time.sleep(0.05)
			command1 = read_clipboard()
			print(self.changing_dev)
			if command1 != "invalid":
				x, y, z, yaw, pitch = command1
				if not self.locked_angle and not self.changing_dev and [x, y, z, yaw, pitch] not in self.all_commands_data:
					if len(self.all_commands_data) > 0:
						pos = self.all_commands_data[0]

						sr1 = surrounding_rings(math.sqrt(pow(pos[0], 2) + pow(pos[2], 2)))
						sr2 = surrounding_rings(math.sqrt(pow(x, 2) + pow(z, 2)))

						if self.ring_overlap(sr1, sr2):
							gradient1 = get_gradient(pos[3])
							gradient2 = get_gradient(yaw)

							constant1 = get_constant(pos[0], pos[2], gradient1)
							constant2 = get_constant(x, z, gradient2)

							c_x, c_z = intersect_lines(gradient1, gradient2, constant1, constant2)
							ring = validate_result(c_x, c_z)
						else:
							self.logger.output.emit("Invalid measurement")
							ring = -1
					if ring != -1:
						strd_dev = get_strd_dev()
						self.all_commands_data.append([x, y, z, yaw, pitch])
						self.g_set = find_probablilty((x, z, yaw), self.g_set, strd_dev)
						self.results = extract_best(self.g_set)
						self.signals.results.emit(self.results, self.all_commands_data[-1], True)
				elif self.locked_angle and self.results is not None and not self.changing_dev:
					lock_results = self.lock_angle_calcs(read_clipboard(auto_filter=False))
					self.signals.results.emit(lock_results, self.all_commands_data[-1], False)
			else:
				self.logger.output.emit("Invalid paste")

if __name__ == "__main__":
	g_set = precompute_g_set()

	app = QtWidgets.QApplication()
	widget = MainWindow(g_set)
	#widget.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
	widget.show()

	sys.exit(app.exec())