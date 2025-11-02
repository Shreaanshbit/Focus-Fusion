import cv2
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLineEdit, QComboBox, QSpinBox, QTextEdit
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pomodoro import PomodoroTimer
from productivity_tracker import ProductivityTracker
from task_manager import TaskManager
from summary_logger import SummaryLogger
from face_tracker import is_user_distracted
from alarm import play_alarm_sound


class FocusFusionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FocusFusion - PyQt5")
        self.setGeometry(100, 100, 1000, 700)

        # Core components
        self.task_manager = TaskManager()
        self.summary_logger = SummaryLogger()
        self.productivity_tracker = ProductivityTracker()
        self.pomodoro_timer = PomodoroTimer(on_focus=self.on_focus, on_distract=self.on_distract)
        self.distraction_alarm_played = False

        # Tabs
        self.tabs = QTabWidget()
        self.task_tab = QWidget()
        self.stats_tab = QWidget()
        self.tabs.addTab(self.task_tab, "Tasks")
        self.tabs.addTab(self.stats_tab, "Statistics")

        # Setup tabs
        self.init_task_tab()
        self.init_stats_tab()
        self.setCentralWidget(self.tabs)

        # Webcam
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_webcam)
        self.timer.start(30)

    # ---------------- TASK TAB ---------------- #
    def init_task_tab(self):
        layout = QVBoxLayout()

        # Inputs
        self.task_input = QLineEdit()
        self.difficulty_input = QComboBox()
        self.difficulty_input.addItems(["Easy", "Medium", "Hard"])
        self.duration_input = QSpinBox()
        self.duration_input.setRange(5, 60)
        self.duration_input.setSuffix(" min")

        # Buttons
        add_task_btn = QPushButton("Add Task")
        add_task_btn.clicked.connect(self.add_task)

        self.task_list_display = QTextEdit()
        self.task_list_display.setReadOnly(True)

        self.status_label = QLabel("Status: Not Started")
        start_btn = QPushButton("Start Session")
        start_btn.clicked.connect(self.start_session)

        self.pause_btn = QPushButton("Pause Session")
        self.pause_btn.clicked.connect(self.pause_session)
        self.pause_btn.setEnabled(False)

        # Webcam Preview
        self.webcam_label = QLabel("Webcam Feed")
        self.webcam_label.setFixedSize(400, 300)

        # Add widgets
        layout.addWidget(QLabel("Task"))
        layout.addWidget(self.task_input)
        layout.addWidget(QLabel("Difficulty"))
        layout.addWidget(self.difficulty_input)
        layout.addWidget(QLabel("Custom Duration"))
        layout.addWidget(self.duration_input)
        layout.addWidget(add_task_btn)
        layout.addWidget(QLabel("Tasks"))
        layout.addWidget(self.task_list_display)
        layout.addWidget(self.status_label)
        layout.addWidget(start_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(QLabel("Live Face Tracking"))
        layout.addWidget(self.webcam_label)

        self.task_tab.setLayout(layout)

    # ---------------- STATS TAB ---------------- #
    def init_stats_tab(self):
        layout = QVBoxLayout()
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.stats_tab.setLayout(layout)
        self.plot_stats()

    def plot_stats(self):
        sessions = self.productivity_tracker.load_data()
        if not sessions:
            return
        times = [s["focus_time"] for s in sessions]
        dates = [s["date"] for s in sessions]
        self.ax.clear()
        self.ax.plot(dates, times, marker='o')
        self.ax.set_title("Focus Time Over Sessions")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Focus Time (mins)")
        self.figure.autofmt_xdate()
        self.canvas.draw()

    # ---------------- TASK ACTIONS ---------------- #
    def add_task(self):
        task = self.task_input.text()
        difficulty = self.difficulty_input.currentText()
        duration = self.duration_input.value()
        if task.strip():  # only add if not empty
            self.task_manager.add_task(task, difficulty, duration)
            self.refresh_task_list()
            self.task_input.clear()
            
    def start_session(self):
        task = self.task_input.text()
        difficulty = self.difficulty_input.currentText()
        duration = self.duration_input.value()
        self.pomodoro_timer.start(task, difficulty, duration)
        self.status_label.setText("Status: Session Started")
        self.pause_btn.setEnabled(True)

    def refresh_task_list(self):
        self.task_list_display.clear()
        for t in self.task_manager.get_tasks():
            self.task_list_display.append(
                f"{t['task']} - {t['difficulty']} - {t['duration']} mins"
            )
    def pause_session(self):
        self.pomodoro_timer.pause()
        self.status_label.setText("Status: Session Paused")

    # ---------------- DISTRACTION HANDLING ---------------- #
    def on_focus(self):
        self.status_label.setText("Status: Focused")
        self.distraction_alarm_played = False

    def on_distract(self):
        self.status_label.setText("Status: Paused due to distraction")
        if not self.distraction_alarm_played:
            play_alarm_sound()
            self.distraction_alarm_played = True

    # ---------------- WEBCAM ---------------- #
    def update_webcam(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Show webcam feed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.webcam_label.setPixmap(QPixmap.fromImage(qimg))

        # Distraction check
        is_distracted = is_user_distracted(frame)
        if is_distracted:
            self.pomodoro_timer.pause()
            self.on_distract()
        else:
            if not self.pomodoro_timer.running:
                self.pomodoro_timer.resume()
                self.on_focus()
