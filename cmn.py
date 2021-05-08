# -*- coding: UTF-8 -*-
import functools
import hashlib
import inspect
import logging
import math
import os
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

from typing import TypeVar, Callable

RT = TypeVar('RT')


# noinspection PyUnusedLocal
def log_dec(
        func: Callable[..., RT], *args: object, **kwargs: object  # pylint: disable=W0613
) -> Callable[..., RT]:
    # logger = logging.getLogger(func.__module__)
    logger = BotLogger.get_instance()

    # noinspection PyShadowingNames
    @functools.wraps(func)
    def decorator(*args: object, **kwargs: object) -> RT:  # pylint: disable=W0613
        logger.debug('Entering: %s', func.__name__)
        result = func(*args, **kwargs)
        logger.debug(result)
        logger.debug('Exiting: %s', func.__name__)
        return result

    return decorator


class Utils:
    BOT_D_REPEAT_PLS = 'Пожалуйста, введите корректное значение'

    @staticmethod
    def dt_timestamp(dt):
        return time.mktime(dt.timetuple())

    @staticmethod
    def datetime_from_unix_time(unix_time):
        return datetime.fromtimestamp(float(unix_time / 1000))

    @staticmethod
    def datetime_to_unix_time(dt):
        return int(Utils.dt_timestamp(dt) * 1000)

    @staticmethod
    def get_default_list_display(self, list_prev=None, list_last=None):
        list_display = []
        if list_prev:
            list_display.extend(list_prev)
        for field in self._meta.fields:
            list_display.append(field.name)
        if list_last:
            list_display.extend(list_last)
        return tuple(list_display)

    @staticmethod
    def str_to_int(string, default=None):
        value = default
        try:
            value = int(string)
        except TypeError:
            pass
        except ValueError:
            pass
        return value

    @staticmethod
    def int_str_to_bool(string, default=False):
        value = default
        if string is not None:
            int_str = Utils.str_to_int(string.strip())
            if string and int_str is not None:
                value = bool(int_str)

        return value

    @staticmethod
    def get_environ_int(np, default=None):
        # type: (str, int) -> int
        s = os.environ.get(np)
        if s is None:
            res = default
        else:
            res = Utils.str_to_int(s)
            if res is None:
                res = default
        return res

    @staticmethod
    def get_environ_bool(np, default=None):
        # type: (str, bool) -> bool
        res = default
        s = os.environ.get(np)
        if s:
            s = s.lower()
            if s == 'true':
                res = True
            elif s == 'false':
                res = False
        return res

    @staticmethod
    def get_md5_hash_str(str_):
        # type: (str) -> str
        return hashlib.md5(str(str_).encode('utf-8')).hexdigest()

    @staticmethod
    def put_into_text_storage(text_storage, text, max_length):
        # type: ([], str, int) -> []

        max_length = int(max_length)
        if len(text_storage) == 0:
            text_storage.append('')
        ci = len(text_storage) - 1
        if len(text_storage[ci] + text) <= max_length:
            text = text_storage[ci] + text
            text_storage[ci] = text
        else:
            s_m = []
            p_c = math.ceil(len(text) / max_length)
            for i in range(p_c):
                s_m.append(text[max_length * i:max_length * (i + 1)])
            if not text_storage[ci]:
                text_storage.pop(ci)
            text_storage.extend(s_m)

        return text_storage

    @staticmethod
    def get_calling_function_filename(called_function, pass_cnt=1):
        sts = inspect.stack(0)
        i = 0
        for st in sts:
            i += 1
            if st.function == called_function:
                break
        i = i + (pass_cnt - 1)
        calling_function_filename = None
        if i > 0:
            try:
                calling_function_filename = sts[i].filename
            except IndexError:
                pass
        return calling_function_filename


class ExtList(list):
    def __init__(self, no_double=False):
        self.no_double = no_double
        super(ExtList, self).__init__()

    def append(self, obj):
        if not self.no_double or not (obj in self):
            super(ExtList, self).append(obj)

    def get(self, index):
        try:
            return self[index]
        except IndexError:
            pass


class BotLogger(logging.Logger):
    __instance = None

    def __new__(cls, **kwargs):
        instance = None
        if not cls.__instance:
            instance = logging.getLogger(os.environ.get('TTG_BOT_LOGGING_NAME')) or logging.getLogger(os.environ.get('TT_BOT_LOGGING_NAME')) or 'TtgBot'
            formatter = logging.Formatter('%(asctime)s - %(name)s[%(threadName)s-%(thread)d] - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s')

            log_file_max_bytes = Utils.get_environ_int('TTG_BOT_LOGGING_FILE_MAX_BYTES') or Utils.get_environ_int('TT_BOT_LOGGING_FILE_MAX_BYTES') or 10485760
            log_file_backup_count = Utils.get_environ_int('TTG_BOT_LOGGING_FILE_BACKUP_COUNT') or Utils.get_environ_int('TT_BOT_LOGGING_FILE_BACKUP_COUNT') or 10
            fh = RotatingFileHandler("bots_TtgBot.log", mode='a', maxBytes=log_file_max_bytes, backupCount=log_file_backup_count, encoding='UTF-8')
            fh.setFormatter(formatter)
            instance.addHandler(fh)

            sh = logging.StreamHandler(stream=sys.stdout)
            sh.setFormatter(formatter)
            instance.addHandler(sh)

            cls.trace_requests = Utils.get_environ_bool('TTG_BOT_TRACE_REQUESTS') or Utils.get_environ_bool('TT_BOT_TRACE_REQUESTS') or False
            cls.logging_level = os.environ.get('TTG_BOT_LOGGING_LEVEL') or os.environ.get('TT_BOT_LOGGING_LEVEL') or 'INFO'
            # noinspection PyProtectedMember,PyUnresolvedReferences
            cls.logging_level = logging._nameToLevel.get(cls.logging_level)
            if cls.logging_level is None:
                instance.setLevel(logging.DEBUG if cls.trace_requests else logging.INFO)
            else:
                instance.setLevel(cls.logging_level)
            instance.trace_requests = cls.trace_requests
        return instance

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = BotLogger()
        return cls.__instance
