class NewDBRouter:
    """
    A router to control all database operations on models for the new database.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read models go to new_db.
        """
        if model._meta.app_label == 'new_app':
            return 'new_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write models go to new_db.
        """
        if model._meta.app_label == 'new_app':
            return 'new_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in new_db is involved.
        """
        if obj1._meta.app_label == 'new_app' or obj2._meta.app_label == 'new_app':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the new_app's models get created in the right database.
        """
        if app_label == 'new_app':
            return db == 'new_db'
        return None
