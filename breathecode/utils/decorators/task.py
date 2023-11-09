from datetime import datetime, timedelta
from decimal import Decimal
import importlib
import inspect
import logging
from typing import Any, Callable
from breathecode.utils.exceptions import ProgrammingError
import celery
from django.db import transaction
from django.utils import timezone
import copy

__all__ = ['task', 'AbortTask', 'RetryTask', 'RETRIES_LIMIT', 'TaskPriority']

logger = logging.getLogger(__name__)
RETRIES_LIMIT = 10
RETRY_AFTER = timedelta(seconds=5)

from enum import Enum


# keeps this sorted by priority
# unused: ACTIVITY, TWO_FACTOR_AUTH
class TaskPriority(Enum):
    BACKGROUND = 0  # anything without importance
    NOTIFICATION = 1  # non realtime notifications
    MONITORING = 2  # monitoring tasks
    ACTIVITY = 2  # user activity
    BILL = 2  # postpaid billing
    CACHE = 3  # cache
    MARKETING = 4  # marketing purposes
    OAUTH_CREDENTIALS = 5  # oauth tasks
    DEFAULT = 5  # default priority
    TASK_MANAGER = 6  # task manager
    ACADEMY = 7  # anything that the academy can see
    CERTIFICATE = 8  # issuance of certificates
    STUDENT = 9  # anything that the student can see
    TWO_FACTOR_AUTH = 9  # 2fa
    REALTIME = 9  # schedule as soon as possible
    WEB_SERVICE_PAYMENT = 10  # payment in the web
    FIXER = 10  # fixes


class AbortTask(Exception):
    """Abort task due to it doesn't meet the requirements, it will not be reattemped."""
    pass


class RetryTask(Exception):
    """Retry task due to it doesn't meet the requirements for a syncronization issue like a not found, it will be reattemped."""
    pass


def parse_payload(payload: dict):
    if not isinstance(payload, dict):
        return payload

    for key in payload.keys():
        # TypeError("string indices must be integers, not 'str'")
        if isinstance(payload[key], datetime):
            payload[key] = payload[key].isoformat().replace('+00:00', 'Z')

        elif isinstance(payload[key], Decimal):
            payload[key] = str(payload[key])

        elif isinstance(payload[key], list) or isinstance(payload[key], tuple) or isinstance(
                payload[key], set):
            l = []
            for item in payload[key]:
                l.append(parse_payload(item))

            payload[key] = l

        elif isinstance(payload[key], dict):
            payload[key] = parse_payload(payload[key])

    return payload


class Task(object):

    def __init__(self, *args, **kwargs):
        self.is_transaction = kwargs.pop('transaction', False)
        self.fallback = kwargs.pop('fallback', None)
        self.reverse = kwargs.pop('reverse', None)
        self.bind = kwargs.get('bind', False)

        if self.fallback and not callable(self.fallback):
            raise ProgrammingError('Fallback must be a callable')

        if self.reverse and not callable(self.reverse):
            raise ProgrammingError('Reverse must be a callable')

        self.parent_decorator = celery.shared_task(*args, **kwargs)

    def get_fn_desc(self, function: Callable) -> tuple[str, str] or tuple[None, None]:
        if not function:
            return None, None

        module_name = inspect.getmodule(function).__name__
        function_name = function.__name__

        return module_name, function_name

    def reattemp_settings(self) -> dict[str, datetime]:
        """
        Return a dict with the settings to reattemp the task.
        """
        return {'eta': timezone.now() + RETRY_AFTER}

    def reattemp(self, task_module: str, task_name: str, attemps: int, args: tuple[Any], kwargs: dict[str,
                                                                                                      Any]):
        module = importlib.import_module(task_module)
        x = getattr(module, task_name, None)

        x.apply_async(args=args, kwargs={**kwargs, 'attemps': attemps}, **self.reattemp_settings())

    def __call__(self, function):
        from breathecode.commons.models import TaskManager

        self.function = function

        def wrapper(*args, **kwargs):
            task_module, task_name = self.get_fn_desc(function)
            reverse_module, reverse_name = self.get_fn_desc(self.reverse)
            arguments = parse_payload({
                'args': args[1:] if self.bind else args,
                'kwargs': kwargs,
            })

            page = kwargs.get('page', 0)
            total_pages = kwargs.get('total_pages', 1)
            attemps = kwargs.get('attemps', None)
            task_manager_id = kwargs.get('task_manager_id', None)
            last_run = timezone.now()

            x = None
            if task_manager_id:
                x = TaskManager.objects.filter(id=task_manager_id).first()

            created = False
            if x is None:
                created = True
                x = TaskManager.objects.create(task_module=task_module,
                                               task_name=task_name,
                                               attemps=1,
                                               reverse_module=reverse_module,
                                               reverse_name=reverse_name,
                                               arguments=arguments,
                                               status='PENDING',
                                               current_page=page + 1,
                                               total_pages=total_pages,
                                               last_run=last_run)

                kwargs['task_manager_id'] = x.id

            if not created:
                x.current_page = page + 1
                x.last_run = last_run

                if attemps:
                    x.attemps = attemps + 1

                x.save()

            if x.status in ['CANCELLED', 'REVERSED', 'PAUSED', 'ABORTED', 'DONE']:
                x.killed = True
                x.save()
                return

            if self.is_transaction == True:
                error = None
                with transaction.atomic():
                    sid = transaction.savepoint()
                    try:
                        x.status_message = ''
                        x.save()

                        res = function(*args, **kwargs)

                    except RetryTask as e:
                        x.status_message = str(e)[:255]

                        if x.attemps >= RETRIES_LIMIT:
                            logger.exception(str(e))
                            x.status = 'ERROR'
                            x.save()

                        else:
                            logger.warn(str(e))
                            x.save()

                            self.reattemp(x.task_module, x.task_name, x.attemps, arguments['args'],
                                          arguments['kwargs'])

                        # it don't raise anything to manage the reattems with the task manager
                        return

                    except AbortTask as e:
                        x.status = 'ABORTED'
                        x.status_message = str(e)[:255]
                        x.save()

                        logger.exception(str(e))

                        # avoid reattempts
                        return

                    except Exception as e:
                        transaction.savepoint_rollback(sid)

                        error = str(e)[:255]
                        exception = e

                        logger.exception(str(e))

                if error:
                    x.status = 'ERROR'
                    x.status_message = error
                    x.save()

                    # fallback
                    if self.fallback:
                        return self.fallback(*args, **kwargs, exception=exception)

                    # behavior by default
                    raise exception

            else:
                try:
                    res = function(*args, **kwargs)

                except RetryTask as e:
                    x.status_message = str(e)[:255]

                    if x.attemps >= RETRIES_LIMIT:
                        logger.exception(str(e))
                        x.status = 'ERROR'
                        x.save()

                    else:
                        logger.warn(str(e))
                        x.save()

                        self.reattemp(x.task_module, x.task_name, x.attemps, arguments['args'],
                                      arguments['kwargs'])

                    # it don't raise anything to manage the reattems with the task manager
                    return

                except AbortTask as e:
                    x.status = 'ABORTED'
                    x.status_message = str(e)[:255]
                    x.save()

                    logger.exception(str(e))

                    # avoid reattempts
                    return

                except Exception as e:
                    x.status = 'ERROR'
                    x.status_message = str(e)[:255]
                    x.save()

                    logger.exception(str(e))

                    # fallback
                    if self.fallback:
                        return self.fallback(*args, **kwargs, exception=e)

                    # behavior by default
                    raise e

            if x.total_pages == x.current_page:
                x.status = 'DONE'
                x.save()

            return res

        w = copy.deepcopy(wrapper)

        w.__name__ = function.__name__
        w.__module__ = function.__module__

        self.instance = self.parent_decorator(w)
        return self.instance


def task(*args, **kwargs):
    r"""Task wrapper that allows to use transactions, fallback and reverse functions.

    `Examples`
    ```py
    def my_reverse(*args, **kwargs):
        \"\"\"This is executed when someone reverse this task.\"\"\"

        pass


    def my_fallback(*args, **kwargs):
        \"\"\"This is executed when the task fails.\"\"\"

        pass


    @task(transaction=True, fallback=my_fallback, reverse=my_reverse)
    def my_task(*args, **kwargs):
        \"\"\"Your task, if it fails, transaction=True will made a rollback
        in the database, then fallback will be executed, if the task is
        canceled, cancel will be executed.
        \"\"\"

        pass
    """

    return Task(*args, **kwargs)
