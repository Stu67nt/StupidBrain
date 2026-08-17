import os
import subprocess
import sys
import random
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QThreadPool, QTimer
from PySide6.QtGui import QIcon, QGuiApplication, Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QPlainTextEdit, QHeaderView, QVBoxLayout, \
	QLineEdit, QMenu
from calc_math import nether_coords, get_strd_dev
from main import Calc
from seedsearch import *
from strd_dev_calc import *
from copy import deepcopy
import math


class MainWindow(QtWidgets.QWidget):
	def __init__(self, g_set):
		super().__init__()

		self.setFixedSize(545, 335)
		self.setWindowOpacity(0.95)
		self.setWindowTitle("StupidBrain Calc")
		self.setWindowIcon(QIcon("assets/icon.png"))

		self.table = QtWidgets.QTableWidget(columnCount=5, rowCount=5)
		self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
		self.table.setHorizontalHeaderLabels(["Location", "%", "Dist", "Nether", "Angle"])
		self.table.setShowGrid(False)
		self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

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

		self.config_window = None
		self.config_window_button = QPushButton("Config Window")
		self.config_window_button.clicked.connect(self.open_config)

		self.context_menu = QMenu(self)
		self.on_top_toggle_menu = self.context_menu.addAction("Toggle Window on Top")

		self.on_top_toggle_menu.triggered.connect(self.on_top_toggle)

		self.g_set_orig = deepcopy(g_set)
		self.g_set_main = g_set

		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.addWidget(self.table)
		self.layout.addWidget(self.reset_button)
		self.layout.addWidget(self.lock_button)
		self.layout.addWidget(self.log_view)
		self.layout.addWidget(self.seed_window_button)
		self.layout.addWidget(self.config_window_button)

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

	@QtCore.Slot()
	def reset(self):
		self.table.clearContents()
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

		self.seed_window.setFixedSize(325, 250)
		self.seed_window.show()
		self.seed_window.activateWindow()

	def open_config(self):
		if self.config_window is None:
			self.config_window = StrdDevConfig(self.thread)
			self.config_window.destroyed.connect(self.config_window_closed)
		self.thread.changing_dev = True
		self.config_window.show()
		self.config_window.activateWindow()

	@Slot()
	def config_window_closed(self):
		self.config_window = None

	def closeEvent(self, event, /):
		os._exit(0)

	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())

	def on_top_toggle(self):
		print("balls")
		flags = self.windowFlags()
		if Qt.WindowType.WindowStaysOnTopHint in flags:
			self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
		else:
			self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
		self.show()

class SeedSearcher(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("StupidBrain Seed Finder")
		self.setWindowIcon(QIcon("assets/icon.png"))

		self.process = None
		self.entry = None
		self.java_gw = None
		self.seed_filt = None
		self.is_searching = False
		self.threadpool = QThreadPool()

		self.label = QtWidgets.QLabel(self, text="Select what kind of seed you would like to filter for:")
		self.label.resize(self.label.sizeHint())

		self.rb_vil = QtWidgets.QRadioButton(self, text = "Village")
		self.rb_vil.toggled.connect(self.update_filt)

		self.rb_sw = QtWidgets.QRadioButton(self, text = "Shipwreck")
		self.rb_sw.toggled.connect(self.update_filt)

		self.rb_dt = QtWidgets.QRadioButton(self, text = "Desert Temple")
		self.rb_dt.toggled.connect(self.update_filt)

		self.rb_rp = QtWidgets.QRadioButton(self, text = "Ruined Portal")
		self.rb_rp.toggled.connect(self.update_filt)

		self.rb_bt = QtWidgets.QRadioButton(self, text = "Buried Treasure")
		self.rb_bt.toggled.connect(self.update_filt)

		self.submit_button = QPushButton("Submit")
		self.submit_button.clicked.connect(self.submit)

		self.log_view = QPlainTextEdit(self)
		self.log_view.setReadOnly(True)
		self.log_view.setMaximumHeight(30)

		self.layout = QtWidgets.QVBoxLayout(self)
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.rb_vil)
		self.layout.addWidget(self.rb_sw)
		self.layout.addWidget(self.rb_dt)
		self.layout.addWidget(self.rb_rp)
		self.layout.addWidget(self.rb_bt)
		self.layout.addWidget(self.submit_button)
		self.layout.addWidget(self.log_view)

	def closeEvent(self, event):
		self.java_gw.shutdown()
		self.process.terminate()
		self.is_searching = False
		self.log_view.setPlainText("")
		event.accept()

	def update_filt(self, event):
		self.rb = self.sender()
		if self.rb.isChecked():
			self.seed_filt = self.rb.text()
			print(self.seed_filt)

	def submit(self):
		if not self.is_searching:
			self.is_searching = True
			self.log_view.setPlainText(f"Finding {self.seed_filt} seed. This can take a while.")
			self.process = subprocess.Popen(["java", "-jar", "seedsearching-1.0-SNAPSHOT-all.jar"])
			self.java_gw = JavaGateway()
			self.entry = self.java_gw.entry_point
			thread = SeedSearch(self.seed_filt, self.entry)
			thread.signal.results.connect(self.gui_connect)
			self.threadpool.start(thread)

	def gui_connect(self, results):
		self.is_searching = False
		self.java_gw.shutdown()
		self.process.terminate()
		self.log_view.setPlainText(str(results[random.randint(0, len(results)-1)]).strip())


class StrdDevConfig(QtWidgets.QWidget):
	def __init__(self, calc):
		super().__init__()

		self.strd_dev_label = None
		self.thread = None
		self.calc = calc
		self.threadpool = None
		self.tp_command = None
		self.strd_dev = 0.1
		self.coords = None
		self.measurements = []

		self.setWindowTitle("StupidBrain Config")
		self.setWindowIcon(QIcon("assets/icon.png"))
		self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
		self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

		self.label = QtWidgets.QLabel(self, text = "Paste in the stronghold tp command:")
		self.label.resize(self.label.sizeHint())

		self.stronghold_pos_box = QtWidgets.QLineEdit(self, placeholderText="/tp @s 1048 ~ 1480")

		self.submit_button = QPushButton("Submit")
		self.submit_button.clicked.connect(self.submit)

		self.layout = QVBoxLayout(self)
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.stronghold_pos_box)
		self.layout.addWidget(self.submit_button)

	def submit(self):
		self.coords = filter_command(self.stronghold_pos_box.text())
		self.measurements = []
		self.strd_dev = get_strd_dev()
		print(self.coords)
		if self.coords != [] and self.thread is None:
			self.stronghold_pos_box.setReadOnly(True)
			print("Detected")
			self.srtd_dev_hint_label = QtWidgets.QLabel(self, text = "The current standard deviation configured is: ")

			self.strd_dev_label = QtWidgets.QLabel(self, text=f"{round(self.strd_dev,4)}")
			self.strd_dev_label.resize(self.strd_dev_label.sizeHint())

			self.manual_set_hint_label = QtWidgets.QLabel(self, text="Enter your value in the text box if you already know it: ")

			self.manual_strd_dev_input = QtWidgets.QLineEdit(self, placeholderText="0.1")

			self.strd_dev_submit_button = QPushButton("Submit")
			self.strd_dev_submit_button.clicked.connect(self.save_strd_dev)

			self.layout.removeWidget(self.label)
			self.layout.removeWidget(self.stronghold_pos_box)
			self.layout.removeWidget(self.submit_button)
			self.label.deleteLater()
			self.stronghold_pos_box.deleteLater()
			self.submit_button.deleteLater()

			self.layout.addWidget(self.srtd_dev_hint_label)
			self.layout.addWidget(self.strd_dev_label)
			self.layout.addWidget(self.manual_set_hint_label)
			self.layout.addWidget(self.manual_strd_dev_input)
			self.layout.addWidget(self.strd_dev_submit_button)

			self.thread = StrdDevCalc(self.coords)
			self.thread.signals.results.connect(self.update_strd_dev)
			QtCore.QThreadPool.globalInstance().start(self.thread)

	def update_strd_dev(self, strd_dev, tp_command):
		clipboard = QGuiApplication.clipboard()
		clipboard.setText(tp_command)
		self.strd_dev_label.setText(f"{round(strd_dev,4)}")

	def save_strd_dev(self):
		try:
			strd_dev = float(self.manual_strd_dev_input.text())
		except ValueError:
			if self.strd_dev_label is not None:
				strd_dev = float(self.strd_dev_label.text())
			else:
				strd_dev = get_strd_dev()

		if strd_dev > 0:
			with open("config.txt", "w") as f:
				f.write(f"{strd_dev}")
				f.close()

			self.confirmation_popup = QtWidgets.QLabel(self, text="Saved!")
			self.layout.addWidget(self.confirmation_popup)
			QTimer.singleShot(2000, self.remove_popup)

	def remove_popup(self):
		self.layout.removeWidget(self.confirmation_popup)
		self.confirmation_popup.deleteLater()

	def closeEvent(self, event):
		if self.thread is not None:
			self.thread.is_running = False
		self.calc.changing_dev = False
		event.accept()
