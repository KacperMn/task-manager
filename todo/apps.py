from django.apps import AppConfig

class TodoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'todo'

    def ready(self):
        import todo.signals  # Import the signals module
        from todo.tasks import schedule_activate_scheduled_tasks
        schedule_activate_scheduled_tasks()

