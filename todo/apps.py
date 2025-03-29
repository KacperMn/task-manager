from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class TodoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'todo'

    def ready(self):
        # Import here to avoid early database access
        from django.core.management import call_command
        import django
        if not django.conf.settings.configured:
            return
            
        # Use post_migrate signal to set up scheduled tasks
        from django.db.models.signals import post_migrate
        
        def setup_scheduler(sender, **kwargs):
            # This will run after migrations are complete
            from todo.utils import setup_scheduled_tasks
            setup_scheduled_tasks()
            
        post_migrate.connect(setup_scheduler, sender=self)
