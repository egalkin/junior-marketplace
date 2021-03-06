from datetime import timedelta

from celery import Celery
from celery.schedules import crontab
from celery.signals import task_failure, worker_shutting_down
from celery.task import periodic_task

from marketplace.error_reports import send_report
# from marketplace.collect_statistics import collect_orders_stat, collect_users_count_stat


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_BACKEND_URL'],
        broker=app.config['CELERY_BROKER_URL'],
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def setup_periodic_tasks():
    return {
        'collect-stat-every-two-hours': {
            'task': 'collect_statistics.send_users_count_stat',
            'schedule': crontab(minute='0', hour='*/2')
        },
        'collect-stat-every-three-hours': {
            'task': 'collect_statistics.send_orders_stat',
            'schedule': crontab(minute='0', hour='*/3')
        },
        'update-static-sitemap-every-day': {
            'task': 'sitemap_tools.update_static_sitemap',
            'schedule': crontab(minute='0', hour='*/24')
        }
    }


@task_failure.connect
def task_failure_report_send(sender=None, exception=None, **kwargs):
    msg = f'Celery. Task {sender} fail with exception {exception}'
    send_report(msg, 'celery', reporter='celery', celery='task')


@worker_shutting_down.connect
def worker_shutdown_report_send(sig=None, exitcode=None, how=None, **kwargs):
    msg = f'Celery. Worker shutting down with exitcode {exitcode}, signal - {sig}'
    send_report(msg, 'celery', reporter='celery', celery='worker')
