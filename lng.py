# -*- coding: UTF-8 -*-

import gettext
import os

from ttgb_cmn.cmn import Utils

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

use_django = True

LANG = None


def set_use_django(val):
    global use_django
    use_django = val


def get_lang():
    if use_django:
        # noinspection PyUnresolvedReferences
        from django.utils import translation
        return translation
    else:
        if LANG:
            return LANG
        else:
            calling_function_filename = Utils.get_calling_function_filename(get_lang.__name__, 2)
            if calling_function_filename:
                return gettext.translation('django', os.path.join(os.path.dirname(os.path.abspath(calling_function_filename)), 'locale'), languages=['ru'])
            return gettext.translation('django', os.path.join(BASE_DIR, 'locale'), languages=['ru'])


def get_text(msg_id):
    return get_lang().gettext(msg_id)


def translation_activate(language):
    if use_django:
        get_lang().activate(language)
    else:
        global LANG
        if language:
            calling_function_filename = Utils.get_calling_function_filename(translation_activate.__name__)
            if calling_function_filename:
                LANG = gettext.translation('django', os.path.join(os.path.dirname(os.path.abspath(calling_function_filename)), 'locale'), languages=[language])
            else:
                LANG = gettext.translation('django', os.path.join(BASE_DIR, 'locale'), languages=[language])
