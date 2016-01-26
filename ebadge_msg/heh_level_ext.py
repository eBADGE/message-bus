import json
import logging

logger = logging.getLogger(__name__)

from common import *


class ExtSiXlabSetDeviceCapabilities(EbadgeMsg):
    def __init__(
            self, phydevice, device, relay, classes, type_, device_name, signals):
        super(ExtSiXlabSetDeviceCapabilities, self).__init__()

        self.phydevice = phydevice
        self.device = device
        self.relay = relay
        self.classes = classes
        self.type_ = type_
        self.device_name = device_name
        self.signals = signals

    @staticmethod
    def _get_msg_type():
        return 'ext_si_xlab_set_device_capabilities'

    @staticmethod
    def _from_dict(dct):
        return ExtSiXlabSetDeviceCapabilities(
            dct['phydevice'], dct['device'], dct['relay'], dct['classes'],
            dct['type'], dct['device_name'], dct['signals'])


class ExtSiXlabLedSignal(EbadgeMsg):
    def __init__(self, duration):
        super(ExtSiXlabLedSignal, self).__init__()
        self.duration = duration

    @staticmethod
    def _get_msg_type():
        return 'ext_si_xlab_led_signal'

    @staticmethod
    def _from_dict(dct):
        return ExtSiXlabLedSignal(dct['duration'])
