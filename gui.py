import os
import subprocess
import sys
import random
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QPlainTextEdit
from calc_math import nether_coords
from main import Calc
from seedsearch import *
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

		self.lock_button = QPushButton("Lock")
		self.lock_button.clicked.connect(self.lock)

		self.log_view = QPlainTextEdit(self)
		self.log_view.setReadOnly(True)
		self.log_view.setMaximumHeight(30)

		self.seed_window = None
		self.seed_window_button = QPushButton("Seed Filter")
		self.seed_window_button.clicked.connect(self.open_seed_searcher)

		self.g_set_orig = deepcopy(g_set)
		self.g_set_main = g_set


		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.addWidget(self.table)
		self.layout.addWidget(self.reset_button)
		self.layout.addWidget(self.lock_button)
		self.layout.addWidget(self.log_view)
		self.layout.addWidget(self.seed_window_button)

		self.thread = Calc(self.g_set_main)
		self.thread.signals.results.connect(self.display_best)
		self.thread.logger.output.connect(self.write)
		self.threadpool = QtCore.QThreadPool()
		self.threadpool.start(self.thread)


	@QtCore.Slot(list)
	def display_best(self, results, player_pos, need_fixing):
		self.table.clearContents()
		for i, (x, z, distance, angle, chance) in enumerate(results):
			if need_fixing:
				distance = math.sqrt(pow((x - player_pos[0]),2) + pow((z - player_pos[2]), 2))
				angle = math.degrees(math.atan2(-(x - player_pos[0]), (z - player_pos[2])))
				items = [QTableWidgetItem(str((x, z))), QTableWidgetItem(str(round(chance * 100, 2))),
						QTableWidgetItem(str(round(distance))), QTableWidgetItem(str(nether_coords(x, z))),
						 QTableWidgetItem(str(round(angle, 1)))]
			else:
				items = results[i]

			for j in range(0, len(items)):
				self.table.setItem(i, j, items[j])
		self.table.resizeColumnsToContents()

	@QtCore.Slot()
	def reset(self):
		self.table.clearContents()
		self.table.resizeColumnsToContents()
		self.thread.g_set = deepcopy(self.g_set_orig)
		self.thread.all_commands_data = []

	@QtCore.Slot()
	def lock(self):
		if self.thread.locked_angle:
			print("unlocked")
			self.lock_button.setText("Lock")
			self.thread.locked_angle = False
		elif not self.thread.locked_angle:
			print("locked")
			self.lock_button.setText("Unlock")
			self.thread.locked_angle = True

	def write(self, text):
		self.log_view.appendPlainText(text.strip())

	@QtCore.Slot()
	def open_seed_searcher(self):
		if self.seed_window is None:
			self.seed_window = SeedSearcher()
			self.seed_window.resize(400, 300)

		self.seed_window.show()
		self.seed_window.activateWindow()

	def closeEvent(self, event):
		event.accept()

class SeedSearcher(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()

		self.seed_filt = None
		self.threadpool = QThreadPool()

		self.process = subprocess.Popen(["java", "-jar", "seedsearching-1.0-SNAPSHOT-all.jar"])
		self.java_gw = JavaGateway()
		self.entry = self.java_gw.entry_point

		self.label = QtWidgets.QLabel(self, text="Select what kind of seed you would like to filter for:")

		self.rb_vil = QtWidgets.QRadioButton(self, text = "Village")
		self.rb_vil.toggled.connect(self.update)

		self.rb_sw = QtWidgets.QRadioButton(self, text = "Shipwreck")
		self.rb_sw.toggled.connect(self.update)

		self.rb_dt = QtWidgets.QRadioButton(self, text = "Desert Temple")
		self.rb_dt.toggled.connect(self.update)

		self.rb_rp = QtWidgets.QRadioButton(self, text = "Ruined Portal")
		self.rb_rp.toggled.connect(self.update)

		self.rb_bt = QtWidgets.QRadioButton(self, text = "Buried Treasure")
		self.rb_bt.toggled.connect(self.update)

		self.submit_button = QPushButton("Submit")
		self.submit_button.clicked.connect(self.submit)

		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.rb_vil)
		self.layout.addWidget(self.rb_sw)
		self.layout.addWidget(self.rb_dt)
		self.layout.addWidget(self.rb_rp)
		self.layout.addWidget(self.rb_bt)
		self.layout.addWidget(self.submit_button)

	def closeEvent(self, event):
		self.java_gw.shutdown()
		self.process.terminate()
		event.accept()

	def update(self, event):
		self.rb = self.sender()
		if self.rb.isChecked():
			self.seed_filt = self.rb.text()
			print(self.seed_filt)

	def submit(self):
		thread = SeedSearch(self.seed_filt, self.entry)
		thread.signal.results.connect(self.gui_connect)
		self.threadpool.start(thread)

	def gui_connect(self, results):
		print(results)
