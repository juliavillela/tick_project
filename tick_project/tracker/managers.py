from datetime import timedelta
from django.db.models import Manager
from django.core.exceptions import ValidationError

class SessionManager(Manager):
    def get_active_session(self, user):
        active_session = self.filter(
            task__project__user = user,
            end_time__isnull = True
        ).first()
        return active_session

    def end_current_session(self, user):
        active_session = self.get_active_session(user)
        if active_session:
            active_session.set_end_time()
            active_session.save()

    def create_new_session(self, user, task):
        if self.get_active_session(user):
            raise ValidationError
        session = self.model(task=task)
        session.set_start_time()
        session.save()
        return session
   
    def by_project_and_start_date_within(self, project, date, days):
        latest = date + timedelta(days=days)
        return self.filter(
            start_time__gte=date, 
            start_time__lte=latest, 
            task__project= project
            )
    
