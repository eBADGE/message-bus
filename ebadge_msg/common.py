"""
Copyright (c) 2013, XLAB D.O.O.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    - Neither the name of the XLAB D.O.O. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from ebadge_msg import *

logger = logging.getLogger("ebadge")
import json
import time
import datetime
import re
import uuid

#rabbitmq stuff	
class _EbadgeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            #all eBADGE times must have time-zone defined

            return obj.isoformat() + 'Z'
        elif isinstance(obj, object):
            #some fields may require preprocessing
            fields = _preprocess_fields(obj.__dict__.items())
            return dict(fields)
        else:
            return super(_EbadgeEncoder, self).default(obj)


def _preprocess_fields(fields):
    #remove field name prefixes
    #(for fields whose names are reserved words in python)
    fields = map(lambda (key, value): (re.sub('_$', '', key), value), fields)
    return fields


#json hook that converts dictionaries to real eBADGE objects
def _as_ebadge_msg(dct):
    if 'msg' in dct:
        for msg_class in _get_subclasses_transitive(EbadgeMsg):
            if msg_class._get_msg_type() == dct['msg']:
                return msg_class._from_dict(dct)
    return dct


def _get_subclasses_transitive(class_):
    subclasses = []
    for subclass in class_.__subclasses__():
        subclasses.append(subclass)
        subclasses = subclasses + _get_subclasses_transitive(subclass)
    return subclasses


#base class for all eBADGE messages
class EbadgeMsg(object):
    def __init__(self):
        self.msg = self._get_msg_type()

    def to_json(self):
        json_str = json.dumps(self, cls=_EbadgeEncoder)
        #test-disable prints and assert for production!
        #logger.info('1: ' + json_str)
        #logger.info('2: ' + json.dumps(from_json(json_str), cls=_EbadgeEncoder))
        #assert (json_str == json.dumps(from_json(json_str), cls=_EbadgeEncoder))
        return json_str

    @staticmethod
    def _get_msg_type():
        return None


#further base class for all eBADGE messages that require immediate
#generic response (eg OK/not-OK) and thus need a message ID
class EbadgeSyncMsg(EbadgeMsg):
    def __init__(self):
        super(EbadgeSyncMsg, self).__init__()
        self.msg_id = makeuuid()

    def _set_id_from_dict(self, dct):
        self.msg_id = dct['msg_id']


####general-purpose functions

#create random UUID
def makeuuid():
    return uuid.uuid4().urn.replace('urn:uuid:', '')

#parse JSON into eBADGE object
def from_json(json_str):
    return json.loads(json_str, object_hook=_as_ebadge_msg)


def time_now(_format="unix", microsec=False):
    if _format == "unix":
        if microsec:
            return (time.time())
        else:
            return (int(time.time()))


def from_unixtime(value):
    return datetime.datetime.fromtimestamp(int(value))


def to_unixtime(value):
    """
    TODO: convert value to correct format
    """
    if isinstance(value,str) or isinstance(value,unicode):
        try:
            return int(time.mktime(datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").timetuple()))
        except Exception as err:
            try:
                return int(time.mktime(datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple()))
            except:
                logger.error("to_unixtime: %s" % err)
                return 0

    if isinstance(value,datetime.datetime):
        return int(time.mktime(value.timetuple()))


