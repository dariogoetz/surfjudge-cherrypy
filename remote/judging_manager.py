# -*- coding: utf-8 -*-
"""
    Copyright (c) Dario Götz and Jörg Christian Reiher.
    All rights reserved.
"""
import threading
import datetime


from keys import *

from config import Config
_CONFIG = Config(__name__)



class JudgingManager(object):
    '''
    Provides the judging management responsible for keeping track of
    which judge requests to judge which heat
    '''

    def __init__(self):
        self._lock = threading.RLock()

        self.__judging_requests = {}


    def expire_judging_requests(self):
        with self._lock:
            for heat_id, reqs in self.__judging_requests.items():
                now = datetime.datetime.now()
                for judge_id, expire_date in reqs.items():
                    if expire_date < now:
                        del self.__judging_requests[heat_id][judge_id]
        return

    def register_judging_request(self, judge_id, heat_id, expire_s=None):
        if expire_s:
            expire_date = datetime.datetime.now() + datetime.timedelta(seconds=expire_s)
        else:
            expire_date = None
        with self._lock:
            self.__judging_requests.setdefault(heat_id, {})[judge_id] = expire_date
        return True


    def unregister_judging_request(self, judge_id, heat_id):
        with self._lock:
            try:
                del self.__judging_requests[heat_id][judge_id]
            except:
                print 'judging_manager: Cannot unregister judging request for Heat {} by {}'.format(heat_id, judge_id)
                return False
        return True


    def get_judging_requests(self, heat_id):
        self.expire_judging_requests()
        res = {}
        res.update(self.__judging_requests.get(heat_id, {}))
        return res
