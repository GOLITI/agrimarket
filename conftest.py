# Fichier de configuration pytest pour tous les tests Django

import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    """Configuration de la base de données de test."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': True,
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Donne accès à la DB pour tous les tests."""
    pass
