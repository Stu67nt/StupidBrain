import sys
import random
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QPlainTextEdit
from calc_math import nether_coords
from main import Calc
from copy import deepcopy
import math


class MainWindow(QtWidgets.QWidget):
	def __init__(self, g_set):
		super().__init__()

		self.table = QtWidgets.QTableWidget(columnCount=5, rowCount=5)
		self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
		self.table.setHorizontalHeaderLabels(["Location", "%", "Dist", "Nether", "Angle"])
		self.table.resizeColumnsToContents()

		self.reset_button = QPushButton("Reset")
		self.reset_button.clicked.connect(self.reset)

		self.log_view = QPlainTextEdit(self)
		self.log_view.setReadOnly(True)
		self.log_view.setMaximumHeight(30)

		self.g_set_orig = deepcopy(g_set)
		self.g_set_main = g_set


		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.addWidget(self.table)
		self.layout.addWidget(self.reset_button)
		self.layout.addWidget(self.log_view)

		self.thread = Calc(self.g_set_main)
		self.thread.signals.results.connect(self.display_best)
		self.threadpool = QtCore.QThreadPool()
		self.threadpool.start(self.thread)


	@QtCore.Slot(list)
	def display_best(self, results, player_pos):
		self.table.clearContents()
		for i, (x, z, distance, angle, chance) in enumerate(results):
			distance = math.sqrt(pow((x - player_pos[0]),2) + pow((z - player_pos[2]), 2))
			angle = math.degrees(math.atan2(-(x - player_pos[0]), (z - player_pos[2])))
			items = [QTableWidgetItem(str((x, z))), QTableWidgetItem(str(round(chance * 100, 2))),
					QTableWidgetItem(str(round(distance))), QTableWidgetItem(str(nether_coords(x, z))),
					 QTableWidgetItem(str(round(angle, 1)))]

			for j in range(0, len(items)):
				self.table.setItem(i, j, items[j])
		self.table.resizeColumnsToContents()

	@QtCore.Slot()
	def reset(self):
		self.table.clearContents()
		self.thread.g_set = deepcopy(self.g_set_orig)
		self.thread.all_commands_data = []

	def write(self, text):
		self.log_view.appendPlainText(text.strip())