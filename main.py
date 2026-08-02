import math
import sys
from PySide6.QtGui import QIcon
from calc_math import *
from gui import *
from PySide6 import QtWidgets
from PySide6.QtCore import QThreadPool, Slot, QObject, Signal

class CalcSignals(QObject):
	results = Signal(list, list, bool)

class Calc(QtCore.QRunnable):
	def __init__(self, g_set):
		super().__init__()
		self.signals = CalcSignals()
		self.g_set = g_set
		self.locked_angle = False
		self.results = None

	def validate_measurement(self, sr1, sr2):
		for r in sr1:
			if r in sr2:
				return True
		return False

	def lock_angle_calcs(self, command):
		# /execute in minecraft:overworld run tp @s 1920.48 75.00 -1259.10 139.88 -31.30
		# /execute in minecraft:the_nether run tp @s 77.78 50.00 311.31 74.90 6.46
		parts = command.split(" ")
		parts[2] = parts[2].split(":")
		dimension, x, z, yaw = parts[2][1], float(parts[6]), float(parts[8]), float(parts[9])

		for i, pos in enumerate(self.results):
			if dimension == "the_nether":
				n_x, n_z = nether_coords(pos[0], pos[2])
				distance = math.sqrt(pow((x - n_x), 2) + pow((z - n_z), 2))
				curr_angle = math.degrees(math.atan2(-(x - n_x), (z - n_z)))
				self.results[i] = [QTableWidgetItem(str((pos[0], pos[1]))), QTableWidgetItem(str(round(pos[5] * 100, 2))),
						 QTableWidgetItem(str(round(distance))), QTableWidgetItem(str(nether_coords(pos[0], pos[1]))),
						 QTableWidgetItem(str(round(curr_angle, 1)))]
			else:
				distance = math.sqrt(pow((x - pos[0]), 2) + pow((z - pos[1]), 2))
				curr_angle = math.degrees(math.atan2(-(pos[0]-x), (pos[1]-z)))
				self.results[i] = [QTableWidgetItem(str((pos[0], pos[1]))), QTableWidgetItem(str(round(pos[4] * 100, 2))),
						 QTableWidgetItem(str(round(distance))), QTableWidgetItem(str(nether_coords(pos[0], pos[1]))),
						 QTableWidgetItem(str(round(curr_angle, 1)))]


	@Slot()
	def run(self):
		ring = 0
		self.all_commands_data = []
		while True:
			print("waiting one")
			keyboard.wait("f3+c")
			time.sleep(0.02)
			command1 = read_clipboard()

			if command1 != "invalid":
				x, y, z, yaw, pitch = command1
				if not self.locked_angle and [x, y, z, yaw, pitch] not in self.all_commands_data:
					if len(self.all_commands_data) > 0:
						pos = self.all_commands_data[0]

						sr1 = surrounding_rings(math.sqrt(pow(pos[0], 2) + pow(pos[2], 2)))
						sr2 = surrounding_rings(math.sqrt(pow(x, 2) + pow(z, 2)))

						if self.validate_measurement(sr1, sr2):
							gradient1 = get_gradient(pos[3])
							gradient2 = get_gradient(yaw)

							constant1 = get_constant(pos[0], pos[2], gradient1)
							constant2 = get_constant(x, z, gradient2)

							c_x, c_z = intersect_lines(gradient1, gradient2, constant1, constant2)
							ring = validate_result(c_x, c_z)
						else:
							ring = -1
					if ring != -1:
						self.all_commands_data.append([x, y, z, yaw, pitch])
						self.g_set = find_probablilty((x, z, yaw), self.g_set, STRD_DEV)
						self.results = extract_best(self.g_set)
						print(self.results)
						self.signals.results.emit(self.results, self.all_commands_data[-1], True)
				elif self.locked_angle and self.results is not None:
					print("lock")
					self.lock_angle_calcs(read_clipboard(auto_filter=False))
					self.signals.results.emit(self.results, self.all_commands_data[-1], False)

if __name__ == "__main__":
	g_set = precompute_g_set()
	app = QtWidgets.QApplication()
	widget = MainWindow(g_set)
	widget.setFixedSize(350, 370)
	widget.setWindowOpacity(0.95)
	widget.setWindowTitle("StupidBrain Calc")
	widget.setWindowIcon(QIcon("icon.png"))
	widget.show()

	sys.exit(app.exec())