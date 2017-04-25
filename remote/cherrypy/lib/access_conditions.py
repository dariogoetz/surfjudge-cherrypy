# -*- coding: utf-8 -*-
"""
    Copyright (c) Dario Götz and Jörg Christian Reiher.
    All rights reserved.
"""
import cherrypy

from keys import *

def require(*conditions):
    '''
    A decorator that appends conditions to the "auth.require"
    field of the request's config variable.


    Plays together with the UserAuthenticationTool which checks
    for "auth.require" and then checks the provided conditions.
    '''
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        f._cp_config.setdefault('auth.require', []).extend(conditions)
        return f
    return decorate



def has_all_roles(*roles):
    def check():
        is_okay = True
        for role in roles:
            if role not in cherrypy.request.user_info.get(KEY_ROLES, []):
                is_okay = False
                break
        return is_okay
    return check

def has_one_role(*roles):
    def check():
        is_okay = False
        for role in roles:
            if role in cherrypy.request.user_info.get(KEY_ROLES, []):
                is_okay = True
                break
        return is_okay
    return check

def is_admin():
    def check():
        return KEY_ROLE_ADMIN in cherrypy.request.user_info.get(KEY_ROLES, [])
    return check
