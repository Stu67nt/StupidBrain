import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QTableWidgetItem
from calc_math import nether_coords
from main import Calc
from copy import deepcopy


class MainWindow(QtWidgets.QWidget):
	def __init__(self, g_set):
		super().__init__()
		self.table = QtWidgets.QTableWidget(columnCount=5, rowCount=5)
		self.table.setHorizontalHeaderLabels(["Location", "Chance", "Displacement", "Nether Location", "Angle"])
		self.g_set_orig = deepcopy(g_set)
		self.g_set_main = g_set


		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.addWidget(self.table)

		self.thread = Calc(self.g_set_main)
		self.thread.signals.results.connect(self.display_best)
		self.threadpool = QtCore.QThreadPool()
		self.threadpool.start(self.thread)


	@QtCore.Slot(list)
	def display_best(self, results):
		self.table.clearContents()
		for i, (x, z, distance, angle, chance) in enumerate(results):
			items = [QTableWidgetItem(str((x, z))), QTableWidgetItem(str(round(chance * 100, 2))),
					 QTableWidgetItem(str(nether_coords(x, z))), QTableWidgetItem(str(round(distance))),
					 QTableWidgetItem(str(round(angle, 2)))]

			for j in range(0, len(items)):
				self.table.setItem(i, j, items[j])