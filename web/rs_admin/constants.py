# -*- coding: utf-8 -*-

import os

MONGODB_URL = os.environ.get("RSADMIN_MONGODB_URL", "mongodb://localhost/radicalspam")

SESSION_LANG_KEY = "current_lang"
SESSION_TIMEZONE_KEY = "current_tz"
SESSION_THEME_KEY = "current_theme"

COL_SESSION = "session_web"

