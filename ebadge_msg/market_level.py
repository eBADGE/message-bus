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
import logging
logger = logging.getLogger("ebadge")
from common import *
class BalancingReserveBid(EbadgeSyncMsg):
	def __init__(
			self, product, quantity, divisible,
			reserve_price, energy_price):
		super(BalancingReserveBid, self).__init__()
		self.bid_id = makeuuid()
		self.product = product
		self.quantity = quantity
		self.divisible = divisible
		self.reserve_price = reserve_price
		self.energy_price = energy_price

	@staticmethod
	def _get_msg_type():
		return 'balancing_reserve_bid'

	@staticmethod
	def _from_dict(dct):
		obj = BalancingReserveBid(
					dct['product'], dct['quantity'], dct['divisible'],
					dct['reserve_price'], dct['energy_price'])
		obj._set_id_from_dict(dct)
		obj.bid_id = dct['bid_id']
		return obj


class Product(object):
	def __init__(self, positive, start, end):
		self.positive = positive
		self.start = start
		self.end = end


class Response(EbadgeMsg):
	def __init__(self, msg_id, response_code, response_subcode, response_desc):
		super(Response, self).__init__()
		self.msg_id = msg_id
		self.response_code = response_code
		self.response_subcode = response_subcode
		self.response_desc = response_desc

	@staticmethod
	def ack(syncMsg):
		return Response(syncMsg.msg_id, 200, 0, "OK")

	@staticmethod
	def _get_msg_type():
		return 'response'

	@staticmethod
	def _from_dict(dct):
		return Response(
					dct['msg_id'], dct['response_code'],
					dct['response_subcode'], dct['response_desc'])


class BidAccepted(EbadgeSyncMsg):
	def __init__(self, bid_id, quantity):
		super(BidAccepted, self).__init__()
		self.bid_id = bid_id
		self.quantity = quantity

	@staticmethod
	def _get_msg_type():
		return 'bid_accepted'

	@staticmethod
	def _from_dict(dct):
		obj = BidAccepted(dct['bid_id'], dct['quantity'])
		obj._set_id_from_dict(dct)
		obj.msg_id = dct['msg_id']
		return obj


class MarketCleared(EbadgeMsg):
	def __init__(self, product):
		super(MarketCleared, self).__init__()
		self.product = product

	@staticmethod
	def _get_msg_type():
		return 'market_cleared'

	@staticmethod
	def _from_dict(dct):
		return MarketCleared(dct['product'])
		

class BalancingEnergyBid(EbadgeSyncMsg):
	def __init__(self, product, quantity, divisible, energy_price):
		super(BalancingEnergyBid, self).__init__()
		self.bid_id = makeuuid()
		self.product = product
		self.quantity = quantity
		self.divisible = divisible
		self.energy_price = energy_price

	@staticmethod
	def _get_msg_type():
		return 'balancing_energy_bid'

	@staticmethod
	def _from_dict(dct):
		obj = BalancingEnergyBid(
					dct['product'], dct['quantity'], dct['divisible'],
					dct['energy_price'])
		obj._set_id_from_dict(dct)
		obj.bid_id = dct['bid_id']
		return obj


class ActivateBid(EbadgeSyncMsg):
	def __init__(self, bid_id, quantity, from_, to):
		super(ActivateBid, self).__init__()
		self.bid_id = bid_id
		self.quantity = quantity
		self.from_ = from_
		self.to = to

	@staticmethod
	def _get_msg_type():
		return 'activate_bid'

	@staticmethod
	def _from_dict(dct):
		obj = ActivateBid(
					dct['bid_id'], dct['quantity'],
					dct['from'], dct['to'])
		obj._set_id_from_dict(dct)
		return obj


class RequestBalancing(EbadgeSyncMsg):
	def __init__(self, quantity, from_, to):
		super(RequestBalancing, self).__init__()
		self.quantity = quantity
		self.from_ = from_
		self.to = to
		
	@staticmethod
	def _get_msg_type():
		return 'request_balancing'

	@staticmethod
	def _from_dict(dct):
		obj = RequestBalancing(dct['quantity'], dct['from'], dct['to'])
		obj._set_id_from_dict(dct)
		return obj


class BalancingActivated(EbadgeMsg):
	def __init__(self, quantity, from_, to, originating_tso, bid_id):
		super(BalancingActivated, self).__init__()
		self.quantity = quantity
		self.from_ = from_
		self.to = to
		self.originating_tso = originating_tso
		self.bid_id = bid_id

	@staticmethod
	def _get_msg_type():
		return 'balancing_activated'

	@staticmethod
	def _from_dict(dct):
		return BalancingActivated(
					dct['quantity'], dct['from'], dct['to'],
					dct['originating_tso'], dct['bid_id'])
		

class BalancingUnachievable(EbadgeSyncMsg):
	def __init__(self, request_id):
		super(BalancingUnachievable, self).__init__()
		self.request_id = request_id

	@staticmethod
	def _get_msg_type():
		return 'balancing_unachievable'
	
	@staticmethod
	def _from_dict(dct):
		obj = BalancingUnachievable(dct['request_id'])
		obj._set_id_from_dict(dct)
		return obj

