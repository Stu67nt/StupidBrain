import math
import sys
from PySide6.QtGui import QIcon
from calc_math import *
from gui import *
from PySide6 import QtWidgets
from PySide6.QtCore import QThreadPool, Slot, QObject, Signal

class CalcSignals(QObject):
	results = Signal(list, list)

class Calc(QtCore.QRunnable):
	def __init__(self, g_set):
		super().__init__()
		self.signals = CalcSignals()
		self.g_set = g_set

	def validate_measurement(self, sr1, sr2):
		for r in sr1:
			if r in sr2:
				return True
		return False


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
				if [x, y, z, yaw, pitch] not in self.all_commands_data:
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
						t1 = time.time()
						self.g_set = find_probablilty((x, z, yaw), self.g_set, STRD_DEV)
						results = extract_best(self.g_set)
						print(results)
						self.signals.results.emit(results, self.all_commands_data[-1])

if __name__ == "__main__":
	g_set = precompute_g_set()
	app = QtWidgets.QApplication()
	widget = MainWindow(g_set)
	widget.setFixedSize(350, 270)
	widget.setWindowOpacity(0.95)
	widget.setWindowTitle("StupidBrain Calc")
	widget.setWindowIcon(QIcon("icon.png"))
	widget.show()

	sys.exit(app.exec())