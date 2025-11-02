import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt

class ProductivityTracker:
    def __init__(self, filename="productivity_log.csv"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Focus Time (min)", "Distracted Time (min)"])

    def log_productivity(self, focus_minutes, distracted_minutes):
        date_str = datetime.now().strftime("%Y-%m-%d")
        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date_str, focus_minutes, distracted_minutes])

    def load_data(self):
        sessions = []
        with open(self.filename, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                sessions.append({
                    "date": row["Date"],
                    "focus": int(row["Focus Time (min)"]),
                    "distracted": int(row["Distracted Time (min)"])
                })
        return sessions

    def plot_productivity(self):
        data = self.load_data()
        if not data:
            return

        dates = [row["date"] for row in data]
        focus_times = [row["focus"] for row in data]
        distracted_times = [row["distracted"] for row in data]

        x = range(len(dates))

        plt.figure(figsize=(8, 4))
        plt.bar(x, focus_times, width=0.4, label="Focus", align="center", color='green')
        plt.bar(x, distracted_times, width=0.4, bottom=focus_times, label="Distracted", align="center", color='red')
        plt.xticks(x, dates, rotation=45)
        plt.xlabel("Date")
        plt.ylabel("Minutes")
        plt.title("Productivity Over Time")
        plt.legend()
        plt.tight_layout()
        plt.show()
