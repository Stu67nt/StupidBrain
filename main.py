from calc_math import *
from gui import *
from PySide6 import QtWidgets
from PySide6.QtCore import QThreadPool, Slot, QObject, Signal

class CalcSignals(QObject):
	results = Signal(list)

class Calc(QtCore.QRunnable):
	def __init__(self, g_set):
		super().__init__()
		self.signals = CalcSignals()
		self.g_set = g_set

	@Slot()
	def run(self):
		count = 0
		all_commands_data = []
		while True:
			print("waiting one")
			keyboard.wait("f3+c")
			time.sleep(0.02)
			command1 = read_clipboard()

			if command1 != "invalid":
				x1, y1, z1, yaw1, pitch1 = parse_result(command1)
				if [x1, y1, z1, yaw1, pitch1] not in all_commands_data:
					all_commands_data.append([x1, y1, z1, yaw1, pitch1])
					t1 = time.time()
					g_set = find_probablilty((x1, z1, yaw1), self.g_set, STRD_DEV)
					results = extract_best(g_set)
					print(results)
					# self.widget.display_best(results)
					self.signals.results.emit(results)

if __name__ == "__main__":
	g_set = precompute_g_set()
	app = QtWidgets.QApplication()
	widget = MainWindow(g_set)
	widget.show()

	sys.exit(app.exec())