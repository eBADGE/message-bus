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

import logging
import pika
import threading
import time
logger = logging.getLogger(__name__)

print "%s logger.getEffectiveLevel():%s" % (__name__, logger.getEffectiveLevel())

from ebadge_msg.common import from_json
import heh_level
import market_level

try:
    from ebadge_heh import *
except:
    logger.error("import ebadge_heh failed")

logger.error("ERROR")
logger.warning("WARNING")
logger.info("INFO")
logger.debug("DEBUG")


class Connector_Settings(object):
    def __init__(self, server_ip, heh_name,
                 location="heh",
                 # #location can be heh or vpp (this settings set correct queue names for publishing and consuming)
                 use_exchange=False, owner=None):

        self.server_ip = server_ip
        self.queue_args = dict()
        self.queue_args["x-ha-policy"] = "all"  # use mirrored queue if possible
        self.queue_args["x-message-ttl"] = 900000

        self.rmq_name = heh_name
        self.use_exchange = use_exchange
        self.location = location
        self.owner = owner

        if self.location == "heh":
            logger.debug("LOCATION HEH")
            self.rmq_name_up = "private-%s-up" % self.rmq_name
            self.rmq_name_down = "private-%s-down" % self.rmq_name
            self.exchange_name_up = "%s-to-%s" % (self.rmq_name, self.owner)
            self.exchange_name_down = "%s-to-%s" % (self.owner, self.rmq_name)
        else:
            logger.debug("LOCATION VPP")
            self.rmq_name_up = "private-%s-down" % self.rmq_name
            self.rmq_name_down = "private-%s-up" % self.rmq_name
            self.exchange_name_up = "%s-to-%s" % (self.owner, self.rmq_name)
            self.exchange_name_down = "%s-to-%s" % (self.rmq_name, self.owner)

        self.queue_durable = True
        self.username = "guest"
        self.password = "guest"
        self.port = 5672
        self.virtualhost = '/'
        self._conn = None
        self.timeout = 3600
        self.heartbeat = 10
        self.retry_delay = 5
        self.use_ssl = False
        self.certfile = None
        self.keyfile = None



class Connector_blocking():
    def __init__(self, Settings, listener=None):
        self.Settings = Settings
        self.listener = listener
        self._conn = None
        self.no_ack = False
        self.queue_name = None
        if self.Settings.use_ssl:
                self.parameters = pika.ConnectionParameters(self.Settings.server_ip, self.Settings.port,
                                                            self.Settings.virtualhost,
                                                            pika.credentials.ExternalCredentials(),
                                                            socket_timeout=self.Settings.timeout,
                                                            heartbeat_interval=self.Settings.heartbeat,
                                                            connection_attempts=3600 * 24,
                                                            retry_delay=self.Settings.retry_delay,
                                                            ssl=True,
                                                            ssl_options={'certfile': self.Settings.certfile,
                                                                         'keyfile': self.Settings.keyfile})
        else:
            self.parameters = pika.ConnectionParameters(self.Settings.server_ip, self.Settings.port,
                                                        self.Settings.virtualhost,
                                                        pika.PlainCredentials(self.Settings.username,
                                                                              self.Settings.password),
                                                        socket_timeout=self.Settings.timeout,
                                                        heartbeat_interval=self.Settings.heartbeat,
                                                        connection_attempts=3600 * 24,
                                                        retry_delay=self.Settings.retry_delay)

    def connect(self):
        retry = 0
        while True:
            retry += 1
            logger.warning("No connection. Connecting ... (queue:%s server_ip:%s) (retry %s)" % (
                self.queue_name, self.Settings.server_ip, retry))
            try:
                self._conn = pika.BlockingConnection(parameters=self.parameters)
            except Exception as err:
                logger.error("Error connecting. Sleeping 1sec before retry. ERR:" + str(err))
                time.sleep(1)
            else:
                try:
                    self._channel = self._conn.channel()
                    self._channel.confirm_delivery()

                    self.queue_declare()
                    logger.info("Connection established")
                    break
                except Exception as err:
                    logger.error("Error channel: " + str(err))
                    time.sleep(1)

            if self._conn is None:
                retry += 1
            else:
                pass

    def queue_declare(self, ):
        try:
            self._channel.queue_declare(queue=self.queue_name, durable=self.Settings.queue_durable,
                                        arguments=self.Settings.queue_args)
        except Exception as err:
            logger.error("queue declare: " + str(err))
            self.connect()

    def basic_publish(self, ebadge_msg):
        if self._conn is None:
            self.queue_name = self.Settings.rmq_name_up
            self.connect()


        send = False

        try:
            send = self._channel.basic_publish(exchange='', routing_key=self.queue_name, body=ebadge_msg.to_json(),
                                               properties=pika.BasicProperties(delivery_mode=2))
            # signal.alarm(0)
            return send

        except Exception, msg:
            logger.error("Sending timed out!")
            self.connect()
            return False

    def start_consuming(self, listener):
        if self._conn is None:
            self.queue_name = self.Settings.rmq_name_down
            self.connect()
        self.listener = listener
        listener.set_connector(self)
        self.is_consumer = True
        while True:
            try:
                self.queue_declare()
                self.consumer = self._channel.basic_consume(listener.callback, queue=self.queue_name,
                                                            no_ack=self.no_ack)
            except Exception as err:
                logger.error("basic_consume ERR:" + str(err))
                self.connect()

            try:
                logger.info("start_consuming OK ")
                self._channel.start_consuming()
            except Exception as err:
                logger.error("start_consuming %s" % err)
                self.connect()


    def recover_msg(self, ):
        logger.debug("Basic recover")
        try:
            timeout = self._conn.add_timeout(10, self.on_timeout)
            self._channel.basic_recover(requeue=True)
            self._conn.remove_timeout(timeout)
        except Exception as err:
            logger.error("recover failed:" + str(err))
            self.connect()

    def ack(self, method):
        logger.debug("no_ack:" + str(self.no_ack))
        if self.no_ack is False:
            logger.debug("sending ack (%s)" % method.delivery_tag)
            self._channel.basic_ack(delivery_tag=method.delivery_tag)

    def nack(self, method):
        if self.no_ack is False:
            logger.debug("sending NO ack (%s)" % method.delivery_tag)
            self._channel.basic_nack(delivery_tag=method.delivery_tag)

class Connector_async():
    class connector(threading.Thread):
        def __init__(self, Settings, listener=None, workqueue=None, queueLock=None,
                     callback_on_connection_closed=None,
                     callback_on_connection_open=None,
                     callback_on_data_sending=None):
            threading.Thread.__init__(self)

            self.Settings = Settings
            self.workqueue = workqueue
            self.queueLock = queueLock
            self.listener = listener

            self._consumer_tag = None
            self._connection = None
            self._channel = None
            self._deliveries = []
            self._closing = False

            self._stop = threading.Event()
            self.ioloop_timeout = None

            self.rmq_name = None
            self.exchange_name = None

            self.msg2send = None
            self.delete_queue = False

            self.callback_on_connection_closed = callback_on_connection_closed
            self.callback_on_data_sending = callback_on_data_sending
            self.callback_on_connection_open = callback_on_connection_open

            if self.Settings.use_ssl:
                self.parameters = pika.ConnectionParameters(self.Settings.server_ip, self.Settings.port,
                                                            self.Settings.virtualhost,
                                                            pika.credentials.ExternalCredentials(),
                                                            socket_timeout=self.Settings.timeout,
                                                            heartbeat_interval=self.Settings.heartbeat,
                                                            connection_attempts=3600 * 24,
                                                            retry_delay=self.Settings.retry_delay,
                                                            ssl=True,
                                                            ssl_options={'certfile': self.Settings.certfile,
                                                                         'keyfile': self.Settings.keyfile})
            else:
                self.parameters = pika.ConnectionParameters(self.Settings.server_ip, self.Settings.port,
                                                            self.Settings.virtualhost,
                                                            pika.PlainCredentials(self.Settings.username,
                                                                                  self.Settings.password),
                                                            socket_timeout=self.Settings.timeout,
                                                            heartbeat_interval=self.Settings.heartbeat,
                                                            connection_attempts=3600 * 24,
                                                            retry_delay=self.Settings.retry_delay)
            self.setConsumer()

        def setConsumer(self):
            if self.listener:
                self._is_consumer = True
                self.rmq_name = self.Settings.rmq_name_down
                self.exchange_name=self.Settings.exchange_name_down
            else:
                self._is_consumer = False
                self.rmq_name = self.Settings.rmq_name_up
                self.exchange_name=self.Settings.exchange_name_up


        def connect(self):
            try:
                self.callback_on_connection_closed()
            except:
                pass
            logger.info('Connecting to %s %s' % (self.Settings.server_ip, self.rmq_name))
            return pika.SelectConnection(self.parameters, self.on_connection_open,
                                         on_open_error_callback=self.on_connect_error)

        def on_connect_error(self):
            logger.error("connecting error")

        def close_connection(self):
            logger.warning('Closing connection')
            self._closing = True
            self._connection.close()

        def add_on_connection_close_callback(self):

            logger.debug('Adding connection close callback')
            self._connection.add_on_close_callback(self.on_connection_closed)

        def on_connection_closed(self, connection, reply_code, reply_text):
            try:
                self.callback_on_connection_closed()
            except:
                pass

            self._channel = None

            if self._closing:
                self._connection.ioloop.stop()
            else:
                logger.warning('Connection closed, reopening in 5 seconds: (%s) %s', reply_code, reply_text)
                self._connection.add_timeout(5, self.reconnect)  # reconnecting in 5 seconds
                # self.reconnect()

        def on_connection_open(self, unused_connection):

            logger.debug('Connection opened')
            self.add_on_connection_close_callback()
            self.open_channel()

        def reconnect(self):
            # This is the old connection IOLoop instance, stop its ioloop
            self._connection.ioloop.stop()

            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()
            # self.run()

        def add_on_channel_close_callback(self):

            logger.debug('Adding channel close callback')
            self._channel.add_on_close_callback(self.on_channel_closed)

        def restore_msg(self):
            if self.msg2send:
                logger.info("msg not send, putting it back to queue")
                try:
                    self.queueLock.acquire()
                    try:
                        self.workqueue.put(self.msg2send, True, 1)
                    except Exception as err:
                        log_exception(err, "error adding to queue")
                    self.queueLock.release()
                    self.msg2send = None

                except Exception as err:
                    log_exception(err, "error sending")

        def on_channel_closed(self, channel, reply_code, reply_text):
            try:
                self.callback_on_connection_closed()
            except:
                pass
            self.restore_msg()
            logger.warning('Channel was closed: (%s) %s', reply_code, reply_text)
            if reply_code == 406:  # # PRECONDITION_FAILED
                logger.info("Removing queue")
                self.delete_queue = True

            if self._closing:
                logger.info("Closing connection")
                self._connection.close()
            else:
                self.reconnect()


        def on_channel_open(self, channel):

            logger.debug('Channel opened')
            try:
                self.callback_on_connection_open()
            except:
                pass

            self._channel = channel
            self.add_on_channel_close_callback()
            self._channel.confirm_delivery()

            if self.Settings.use_exchange:
                self.setup_exchage()
            else:
                self.setup_queue()

        def setup_exchage(self):
            logger.info("Declaring exchange:%s" % self.exchange_name)
            self._channel.exchange_declare(self.on_exchange_declare_ok,
                                           exchange=self.exchange_name,
                                           exchange_type='topic')


        def on_exchange_declare_ok(self, method_frame):
            logger.info("Exchange declared OK")
            self.setup_queue()
            #self.start_worker()

        def on_delete_queue_ok(self, method_frame):
            self.setup_queue()

        def setup_queue(self,):
            if self.delete_queue:
                self._channel.queue_delete(None, self.rmq_name)
                self.delete_queue = False

            if self._is_consumer:
                self._channel.queue_declare(self.on_queue_declareok, self.rmq_name,
                                            durable=self.Settings.queue_durable, arguments=self.Settings.queue_args)
            else:
                self.start_worker()

        def on_queue_bindok(self, method_frame):
            self.start_worker()

        def on_queue_declareok(self, method_frame):

            if self.Settings.use_exchange:
                self._channel.queue_bind(self.on_queue_bindok, exchange=self.exchange_name,
                                         queue=self.rmq_name,
                                         routing_key="*.*")
            else:
                self.start_worker()


        def on_delivery_confirmation(self, method_frame):
            try:
                self.callback_on_data_sending()
            except:
                pass
            confirmation_type = method_frame.method.NAME.split('.')[1].lower()
            logger.debug('Msg delivered (%s) for delivery tag: %i', confirmation_type, method_frame.method.delivery_tag)
            # logger.info('%s delivered' % self.msg2send.msg)
            self.msg2send = None
            try:
                self.workqueue.task_done()
            except:
                pass
            self._connection.remove_timeout(self.ioloop_timeout)

            # self.ioloop_timeout = self._connection.add_timeout(0.1, self.schedule_next_message)
            self.schedule_next_message()

        def close_channel(self):

            logger.debug('Closing the channel')
            if self._channel:
                self._channel.close()

        def open_channel(self):

            logger.debug('Creating a new channel')
            self._connection.channel(on_open_callback=self.on_channel_open)

        def run(self):
            while self._closing is not True:
                self._connection = self.connect()

                self._connection.ioloop.start()

        def stop(self):

            logger.info('Stopping')
            self._closing = True
            self.close_channel()
            self.close_connection()
            # self._connection.ioloop.start()
            logger.info('Stopped')

        def start_worker(self):
            if self._is_consumer:
                self.start_consuming()
            else:
                self.start_publishing()

        # publisher part
        def enable_delivery_confirmations(self):
            self._channel.confirm_delivery(self.on_delivery_confirmation)

        def publish_message(self):
            if self._closing:
                return
            if self.msg2send:
                properties = pika.BasicProperties(content_type='application/json')

                if self.Settings.use_exchange:
                    routing_key = "%s.%s" % (self.msg2send.msg, self.Settings.rmq_name)
                    logger.info('Sending to exchange %s routing_key:%s msg: %s' % (
                        self.exchange_name, routing_key, self.msg2send.to_json()))

                    self._channel.basic_publish(exchange=self.exchange_name, routing_key=routing_key,
                                                body=self.msg2send.to_json(),
                                                properties=properties, mandatory=True)
                else:
                    self.setup_queue(True)
                    logger.info('Sending to queue %s msg: %s' % (self.rmq_name, self.msg2send.to_json()))
                    self._channel.basic_publish("", self.rmq_name, self.msg2send.to_json(), properties, mandatory=True)
                    self.msg2send=None

        def schedule_next_message(self):

            try:
                self._connection.remove_timeout(self.ioloop_timeout)
            except:
                pass
            if self._closing:
                return
            if self.msg2send is None:
                if not self.workqueue.empty():
                    logger.debug("schedule_next_message")
                    self.msg2send = self.workqueue.get()
            self.publish_message()

            self.ioloop_timeout = self._connection.add_timeout(0.2, self.schedule_next_message)


        def start_publishing(self):
            logger.debug('Issuing consumer related RPC commands 1')

            self.enable_delivery_confirmations()
            self.schedule_next_message()


        # consumer part
        def add_on_cancel_callback(self):

            logger.debug('Adding consumer cancellation callback')
            self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

        def on_consumer_cancelled(self, method_frame):

            logger.warning('Consumer was cancelled remotely, shutting down: %r',
                           method_frame)
            if self._channel:
                self._channel.close()

        def acknowledge_message(self, delivery_tag):

            logger.debug('Acknowledging message %s', delivery_tag)
            self._channel.basic_ack(delivery_tag)

        def on_message(self, unused_channel, basic_deliver, properties, body):

            self.listener.set_connector(self)
            logger.debug('Received message # %s from %s: %s', basic_deliver.delivery_tag, properties.app_id, body)
            self.acknowledge_message(basic_deliver.delivery_tag)

            try:
                self.listener.callback(unused_channel, basic_deliver, properties, body)
            except Exception as err:
                log_exception(err, "on_message error")

        def on_cancelok(self, unused_frame):

            logger.debug('RabbitMQ acknowledged the cancellation of the consumer')
            self.close_channel()

        def consumer_stop(self):

            if self._channel:
                logger.debug('Sending a Basic.Cancel RPC command to RabbitMQ')
                self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

        def start_consuming(self):
            logger.debug('Issuing consumer related RPC commands')
            self.add_on_cancel_callback()
            self._consumer_tag = self._channel.basic_consume(self.on_message, self.rmq_name)


class AbstractConsumer(object):
    def set_connector(self, connector):
        self.connector = connector

    def callback(self, channel, method, properties, body):
        ebadge_msg = from_json(body)
        if ebadge_msg == None:
            logger.error("ERROR: cannot decode: " + body)
        try:
            ebadge_msg.msg
        except:
            logger.error("ERROR: msg doesnt exists")
            return None

        if ebadge_msg.msg == heh_level.GetReport._get_msg_type():
            self.on_get_report(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.GetPeriodicReport._get_msg_type():
            self.on_get_periodic_report(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.Report._get_msg_type():
            self.on_report(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.GetEnergyEvents._get_msg_type():
            self.on_get_energy_events(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.GetEnergyEventsRealtime._get_msg_type():
            self.on_get_energy_events_realtime(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.EnergyEvents._get_msg_type():
            self.on_energy_events(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.Activate._get_msg_type():
            self.on_activate(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.AcceptActivation._get_msg_type():
            self.on_accept_activation(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.RejectActivation._get_msg_type():
            self.on_reject_activation(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.ModifyActivation._get_msg_type():
            self.on_modify_activation(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.ContingencyActivate._get_msg_type():
            self.on_contingency_activate(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.ContingencyEnd._get_msg_type():
            self.on_contingency_end(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.LoadPrice._get_msg_type():
            self.on_load_price(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.GenerationPrice._get_msg_type():
            self.on_generation_price(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.GetAllPrices._get_msg_type():
            self.on_get_all_prices(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.GetStatusReport._get_msg_type():
            self.on_get_status_report(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.StatusReport._get_msg_type():
            self.on_status_report(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.SetClock._get_msg_type():
            self.on_set_clock(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.SetSmartMode._get_msg_type():
            self.on_set_smart_mode(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.GetCapabilities._get_msg_type():
            self.on_get_capabilities(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.TotalCapabilities._get_msg_type():
            self.on_total_capabilities(ebadge_msg, method)

        elif ebadge_msg.msg == heh_level.DeviceCapabilities._get_msg_type():
            self.on_device_capabilities(ebadge_msg, method)

        elif ebadge_msg.msg == market_level.BalancingReserveBid._get_msg_type():
            self.on_balancing_reserve_bid(ebadge_msg, method)

        elif ebadge_msg.msg == market_level.Response._get_msg_type():
            self.on_response(ebadge_msg, method)

        elif ebadge_msg.msg == market_level.BidAccepted._get_msg_type():
            self.on_bid_accepted(ebadge_msg, method)

        elif ebadge_msg.msg == market_level.MarketCleared._get_msg_type():
            self.on_market_cleared(ebadge_msg, method)

        elif ebadge_msg.msg == market_level.BalancingEnergyBid._get_msg_type():
            self.on_balancing_energy_bid(ebadge_msg, method)

        elif ebadge_msg.msg == market_level.ActivateBid._get_msg_type():
            self.on_activate_bid(ebadge_msg, method)

        elif ebadge_msg.msg == market_level.RequestBalancing._get_msg_type():
            self.on_request_balancing(ebadge_msg, method)

        elif ebadge_msg.msg == market_level.BalancingActivated._get_msg_type():
            self.on_balancing_activated(ebadge_msg, method)

        elif ebadge_msg.msg == market_level.BalancingUnachievable._get_msg_type():
            self.on_balancing_unachievable(ebadge_msg, method)

        elif re.match('ext_(.+)', ebadge_msg.msg):
            self.on_ext_msg(ebadge_msg, method)
        else:
            logger.error("msg error: " + ebadge_msg.msg)

    # heh-level
    def on_get_report(self, ebadge_msg, method=""):
        logger.info("Received msg: on_get_load_report")
        pass

    def on_get_periodic_report(self, ebadge_msg, method=""):
        pass

    def on_report(self, ebadge_msg, method=""):
        pass

    def on_on_get_generation_report(self, ebadge_msg, method=""):
        pass

    def on_get_periodic_generation_report(self, ebadge_msg, method=""):
        pass

    def on_get_energy_events(self, ebadge_msg, method=""):
        pass

    def on_get_energy_events_realtime(self, ebadge_msg, method=""):
        pass

    def on_energy_events(self, ebadge_msg, method=""):
        pass

    def on_get_electricity_profile(self, ebadge_msg, method=""):
        pass

    def on_electricity_profile(self, ebadge_msg, method=""):
        pass

    def on_get_predicted_load_profile(self, ebadge_msg, method=""):
        pass

    def on_predicted_load_profile(self, ebadge_msg, method=""):
        pass

    def on_get_predicted_generation_profile(self, ebadge_msg, method=""):
        pass

    def on_predicted_generation_profile(self, ebadge_msg, method=""):
        pass

    def on_activate(self, ebadge_msg, method=""):
        pass

    def on_accept_activation(self, ebadge_msg, method=""):
        pass

    def on_reject_activation(self, ebadge_msg, method=""):
        pass

    def on_modify_activation(self, ebadge_msg, method=""):
        pass

    def on_contingency_activate(self, ebadge_msg, method=""):
        pass

    def on_contingency_end(self, ebadge_msg, method=""):
        pass

    def on_load_price(self, ebadge_msg, method=""):
        pass

    def on_generation_price(self, ebadge_msg, method=""):
        pass

    def on_get_all_prices(self, ebadge_msg, method=""):
        pass

    def on_get_status_report(self, ebadge_msg, method=""):
        pass

    def on_status_report(self, ebadge_msg, method=""):
        pass

    def on_set_clock(self, ebadge_msg, method=""):
        pass

    def on_set_smart_mode(self, ebadge_msg, method=""):
        pass

    def on_get_capabilities(self, ebadge_msg, method=""):
        pass

    def on_total_capabilities(self, ebadge_msg, method=""):
        pass

    def on_device_capabilities(self, ebadge_msg, method=""):
        pass

    # #market-level
    def on_balancing_reserve_bid(self, ebadge_msg, method=""):
        pass

    def on_response(self, ebadge_msg, method=""):
        pass

    def on_bid_accepted(self, ebadge_msg, method=""):
        pass

    def on_market_cleared(self, ebadge_msg, method=""):
        pass

    def on_balancing_energy_bid(self, ebadge_msg, method=""):
        pass

    def on_activate_bid(self, ebadge_msg, method=""):
        pass

    def on_request_balancing(self, ebadge_msg, method=""):
        pass

    def on_balancing_activated(self, ebadge_msg, method=""):
        pass

    def on_balancing_unachievable(self, ebadge_msg, method=""):
        pass

    # ## extension msg
    def on_ext_msg(self, ext_msg, ebadge_msg, method=""):
        pass
