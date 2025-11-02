import datetime

class SummaryLogger:
    def __init__(self):
        self.logs = []

    def log_session(self, task, duration, focused_time, distracted_time):
        self.logs.append({
            "task": task,
            "duration": duration,
            "focused": focused_time,
            "distracted": distracted_time,
            "timestamp": datetime.datetime.now()
        })

    def get_logs(self):
        return self.logs
