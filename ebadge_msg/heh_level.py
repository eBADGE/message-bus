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

import json
import logging

logger = logging.getLogger(__name__)

from common import *


class GetReport(EbadgeMsg):
    def __init__(self, from_, to, resolution, signals=list(), heh_id=None):
        super(GetReport, self).__init__()
        self.from_ = from_
        self.to = to
        self.resolution = resolution
        self.signals = signals
        self.heh_id = heh_id

    @staticmethod
    def _get_msg_type():
        return 'get_report'

    @staticmethod
    def _from_dict(dct):
        return GetReport(
            dct['from'], dct['to'],
            dct['resolution'], dct.get('signals'),
            dct.get('heh_id'))


class GetPeriodicReport(EbadgeMsg):
    def __init__(self, interval, first_from, resolution, signals=list(), heh_id=None, request_id=None):
        super(GetPeriodicReport, self).__init__()
        self.interval = interval
        self.first_from = first_from
        self.resolution = resolution
        self.signals = signals
        self.heh_id = heh_id
        self.request_id = request_id

    @staticmethod
    def _get_msg_type():
        return 'get_periodic_report'

    @staticmethod
    def _from_dict(dct):
        return GetPeriodicReport(
            dct['interval'], dct['first_from'],
            dct['resolution'], dct.get('signals'),
            dct.get('heh_id'), dct.get('request_id'))


class Report(EbadgeMsg):
    def __init__(self, from_, to, resolution, values, heh_id=None):
        super(Report, self).__init__()
        self.from_ = from_
        self.to = to
        self.resolution = resolution

        self.values = values
        self.heh_id = heh_id

    @staticmethod
    def _get_msg_type():
        return 'report'

    @staticmethod
    def _from_dict(dct):
        return Report(
            dct['from'], dct['to'], dct['resolution'],
            dct['values'],
            dct.get('heh_id'))


class GetEnergyEvents(EbadgeMsg):
    def __init__(self, from_, to, severity):
        super(GetEnergyEvents, self).__init__()
        self.from_ = from_
        self.to = to
        self.severity = severity

    @staticmethod
    def _get_msg_type():
        return 'get_energy_events'

    @staticmethod
    def _from_dict(dct):
        return GetEnergyEvents(dct['from'], dct['to'], dct['severity'])


class GetEnergyEventsRealtime(EbadgeMsg):
    def __init__(self, severity):
        super(GetEnergyEventsRealtime, self).__init__()
        self.severity = severity

    @staticmethod
    def _get_msg_type():
        return 'get_energy_events_realtime'

    @staticmethod
    def _from_dict(dct):
        return GetEnergyEventsRealtime(dct['severity'])


class EnergyEvents(EbadgeMsg):
    def __init__(self, events):
        super(EnergyEvents, self).__init__()
        self.events = events

    @staticmethod
    def _get_msg_type():
        return 'energy_events'

    @staticmethod
    def _from_dict(dct):
        return EnergyEvents(dct['events'])


class EnergyEvents_Event(object):
    def __init__(self, severity, type_, start_time, end_time):
        self.severity = severity
        self.type_ = type_
        self.start_time = start_time
        self.end_time = end_time


class Activate(EbadgeMsg):
    def __init__(self, from_, to, quantity, device=None, heh_id=None):
        super(Activate, self).__init__()
        self.id_ = makeuuid()
        self.modification_count = 0
        self.from_ = from_
        self.to = to
        self.quantity = quantity
        self.device = device
        self.heh_id = heh_id

    def modify(self, from_=None, to=None, quantity=None, device=None):
        if from_ is not None:
            self.from_ = from_
        if to is not None:
            self.to = to
        if quantity is not None:
            self.quantity = quantity
        if device is not None:
            self.device = device
        self.modification_count += 1

    @staticmethod
    def _get_msg_type():
        return 'activate'

    @staticmethod
    def _from_dict(dct):
        obj = Activate(
            dct['from'], dct['to'],
            dct['quantity'],
            dct.get('device'),
            dct.get('heh_id'), )
        obj.id_ = dct['id']
        obj.modification_count = dct['modification_count']
        return obj


class AcceptActivation(EbadgeMsg):
    def __init__(self, id_, modification_count):
        super(AcceptActivation, self).__init__()
        self.id_ = id_
        self.modification_count = modification_count

    @staticmethod
    def from_activate(activate):
        return AcceptActivation(activate.id_, activate.modification_count)

    @staticmethod
    def _get_msg_type():
        return 'accept_activation'

    @staticmethod
    def _from_dict(dct):
        return AcceptActivation(dct['id'], dct['modification_count'])


class RejectActivation(EbadgeMsg):
    def __init__(self, id_, modification_count):
        super(RejectActivation, self).__init__()
        self.id_ = id_
        self.modification_count = modification_count

    @staticmethod
    def from_activate(activate):
        return RejectActivation(activate.id_, activate.modification_count)

    @staticmethod
    def _get_msg_type():
        return 'reject_activation'

    @staticmethod
    def _from_dict(dct):
        return RejectActivation(dct['id'], dct['modification_count'])


class ModifyActivation(EbadgeMsg):
    def __init__(
            self, activate,
            from_=None, to=None,
            quantity=None, device=None):
        super(ModifyActivation, self).__init__()
        self.id_ = activate.id_
        self.heh_id = activate.heh_id
        self.modification_count = activate.modification_count
        self.from_ = activate.from_
        self.to = activate.to
        self.quantity = activate.quantity
        self.device = activate.device
        if from_ is not None:
            self.from_ = from_
        if to is not None:
            self.to = to
        if quantity is not None:
            self.quantity = quantity
        if device is not None:
            self.device = device

    @staticmethod
    def _get_msg_type():
        return 'modify_activation'

    @staticmethod
    def _from_dict(dct):
        aux_act = Activate._from_dict(dct)
        return ModifyActivation(aux_act)


class GetActivationCapacity(EbadgeMsg):
    def __init__(self, device=None, heh_id=None):
        super(GetActivationCapacity, self).__init__()
        self.device = device
        self.heh_id = heh_id

    @staticmethod
    def _get_msg_type():
        return 'get_activation_capacity'

    @staticmethod
    def _from_dict(dct):
        return GetActivationCapacity(dct.get('device'), dct.get('heh_id'))


class ActivationCapacity(EbadgeMsg):
    def __init__(self, device, pos_capacity, neg_capacity, heh_id=None):
        super(ActivationCapacity, self).__init__()
        self.device = device
        self.pos_capacity = pos_capacity
        self.neg_capacity = neg_capacity
        self.heh_id = heh_id

    @staticmethod
    def _get_msg_type():
        return 'activation_capacity'

    @staticmethod
    def _from_dict(dct):
        return ActivationCapacity(
            dct.get('device'),
            dct.get('pos_capacity', 0),
            dct.get('neg_capacity', 0),
            dct.get('heh_id'))


class ContingencyActivate(EbadgeMsg):
    def __init__(self, from_, to, max_quantity, heh_id=None):
        super(ContingencyActivate, self).__init__()
        self.id_ = makeuuid()
        self.from_ = from_
        self.to = to
        self.max_quantity = max_quantity
        self.heh_id = heh_id

    @staticmethod
    def _get_msg_type():
        return 'contingency_activate'

    @staticmethod
    def _from_dict(dct):
        obj = ContingencyActivate(
            dct['from'], dct['to'],
            dct.get('max_quantity', float("inf")),
            dct.get('heh_id'), )
        obj.id_ = dct['id']
        return obj


class ContingencyEnd(EbadgeMsg):
    def __init__(self, id_, end, heh_id=None):
        super(ContingencyEnd, self).__init__()
        self.id_ = id_
        self.end = end
        self.heh_id = heh_id

    @staticmethod
    def _get_msg_type():
        return 'contingency_end'

    @staticmethod
    def _from_dict(dct):
        return ContingencyEnd(dct['id'], dct['end'], dct.get('heh_id'))


class LoadPrice(EbadgeMsg):
    def __init__(self, from_, to, price):
        super(LoadPrice, self).__init__()
        self.from_ = from_
        self.to = to
        self.price = price

    @staticmethod
    def _get_msg_type():
        return 'load_price'

    @staticmethod
    def _from_dict(dct):
        return LoadPrice(dct['from'], dct['to'], dct['price'])


class GenerationPrice(EbadgeMsg):
    def __init__(self, from_, to, price, device):
        super(GenerationPrice, self).__init__()
        self.from_ = from_
        self.to = to
        self.price = price
        self.device = device

    @staticmethod
    def _get_msg_type():
        return 'generation_price'

    @staticmethod
    def _from_dict(dct):
        return GenerationPrice(
            dct['from'], dct['to'], dct['price'], dct['device'])


class GetAllPrices(EbadgeMsg):
    def __init__(self):
        super(GetAllPrices, self).__init__()

    @staticmethod
    def _get_msg_type():
        return 'get_all_prices'

    @staticmethod
    def _from_dict(dct):
        return GetAllPrices()


class GetStatusReport(EbadgeMsg):
    def __init__(self, from_, to, severity_threshold):
        super(GetStatusReport, self).__init__()
        self.from_ = from_
        self.to = to
        self.severity_threshold = severity_threshold

    @staticmethod
    def _get_msg_type():
        return 'get_status_report'

    @staticmethod
    def _from_dict(dct):
        return GetStatusReport(
            dct['from'], dct['to'], dct['severity_threshold'])


class StatusReport(EbadgeMsg):
    def __init__(self, status, clock, events):
        super(StatusReport, self).__init__()
        self.status = status
        self.clock = clock
        self.events = events

    @staticmethod
    def _get_msg_type():
        return 'status_report'

    @staticmethod
    def _from_dict(dct):
        return StatusReport(dct['status'], dct['clock'], dct['events'])


class StatusReport_Event(EbadgeMsg):
    def __init__(self, time, severity, type_):
        self.time = time
        self.severity = severity
        self.type_ = type_


class SetClock(EbadgeMsg):
    def __init__(self, offset):
        super(SetClock, self).__init__()
        self.offset = offset

    @staticmethod
    def _get_msg_type():
        return 'set_clock'

    @staticmethod
    def _from_dict(dct):
        return SetClock(dct['offset'])


class SetSmartMode(EbadgeMsg):
    def __init__(self, mode, reset):
        super(SetSmartMode, self).__init__()
        self.mode = mode
        self.reset = reset

    @staticmethod
    def _get_msg_type():
        return 'set_smart_mode'

    @staticmethod
    def _from_dict(dct):
        return SetSmartMode(dct['mode'], dct['reset'])


class GetCapabilities(EbadgeMsg):
    def __init__(self, device):
        super(GetCapabilities, self).__init__()
        self.device = device

    @staticmethod
    def _get_msg_type():
        return 'get_capabilities'

    @staticmethod
    def _from_dict(dct):
        return GetCapabilities(dct.get('device'))


class Capabilities(EbadgeMsg):
    def __init__(self, device_name, device_version, devices, device_sn=None, device_ip=None, device_mac=None):
        super(Capabilities, self).__init__()
        self.device_name = device_name
        self.device_version = device_version
        self.device_sn = device_sn
        self.device_ip = device_ip
        self.device_mac = device_mac
        self.devices = devices

    @staticmethod
    def _get_msg_type():
        return 'capabilities'

    @staticmethod
    def _from_dict(dct):
        return Capabilities(
            dct['device_name'], dct['device_version'], dct['devices'], dct.get('device_sn'), dct.get('device_ip'),
            dct.get('device_mac'))


class DeviceCapabilities(EbadgeMsg):
    def __init__(
            self, device, classes, type_, device_name, version,
            signals,
            can_predict_profile, can_predict_curtailment_capacity):
        super(DeviceCapabilities, self).__init__()
        self.device = device
        self.classes = classes
        self.type_ = type_
        self.device_name = device_name
        self.version = version
        self.signals = signals
        self.can_predict_profile = can_predict_profile
        self.can_predict_curtailment_capacity = can_predict_curtailment_capacity

    @staticmethod
    def _get_msg_type():
        return 'device_capabilities'

    @staticmethod
    def _from_dict(dct):
        return DeviceCapabilities(
            dct['device'], dct['classes'], dct['type'],
            dct['device_name'], dct['version'],
            dct['signals'],
            dct['can_predict_profile'],
            dct['can_predict_curtailment_capacity'])

        


