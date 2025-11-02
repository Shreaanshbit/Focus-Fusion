class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task, difficulty, duration):
        self.tasks.append({
            "task": task,
            "difficulty": difficulty,
            "duration": duration
        })

    def get_tasks(self):
        return self.tasks

    def clear_tasks(self):
        self.tasks = []
