#!/usr/bin/python
# -*- coding: utf-8 -*- 
"""
Copyright (c) 2013-2014, XLAB D.O.O.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:

    - Redistributions of source code must retain the above copyright notice, this list of conditions and the following
    disclaimer.
    - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
     following disclaimer in the documentation and/or other materials provided with the distribution.
    - Neither the name of the XLAB D.O.O. nor the names of its contributors may be used to endorse or promote products
     derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE,EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s  %(lineno)d:%(filename)-15s %(threadName)-15s %(funcName)-25s\t %(levelname)-8s %(message)s',
    "%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


logging.getLogger("ebadge_msg").setLevel(logging.DEBUG)
logging.getLogger("ebadge_msg").addHandler(ch)
logging.getLogger("pika").addHandler(ch)

import sys
import Queue
import threading
import logging
import time
from ebadge_msg.comm import AbstractConsumer, Connector_Settings, Connector_async
from ebadge_msg.heh_level import Report


workQueue = Queue.Queue(10)
queueLock = threading.Lock()
queue_name = sys.argv[2]


class Consumer(AbstractConsumer):
    def on_get_report(self, request, method=""):

        logger.info("Got: " + request.msg)
        mes = [0.12, 0.17, 0.33, 0]
        values = dict()
        for sig in request.signals:
            values[sig] = mes

        report = Report(
            request.from_, request.to,
            request.resolution,
            values)
        try:
            queueLock.acquire()
            try:
                workQueue.put_nowait(report)
                queueLock.release()
            except Exception as err:
                logger.error("Queue err:" + str(err))

        except Exception as err:
            logger.error("error sending: " + str(err))


conn_settings = Connector_Settings(sys.argv[1], sys.argv[2], location="heh",owner="xlab")
conn_settings.virtualhost = "/"
conn_settings.port=5671
conn_settings.use_ssl = True
conn_settings.use_exchange=True
conn_settings.certfile = sys.argv[3]
conn_settings.keyfile = sys.argv[4]
conn_settings.use_exchange=True

thread = {}
thread["sender"] = Connector_async.connector(conn_settings, workqueue=workQueue, queueLock=queueLock)
thread["consumer"] = Connector_async.connector(conn_settings, listener=Consumer())
## start all threads
for t in thread.values():
    t.daemon = True
    t.start()
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    for t in thread.values():
        try:
            t.stop()
            t.join()
        except Exception as err:
            logger.error("Error Stopping:" + str(err))
    raise SystemExit