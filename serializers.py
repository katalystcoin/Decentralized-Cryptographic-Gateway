import json

import base58
from abc import ABC, abstractmethod

from database import PLATFORM_WAVES, PLATFORM_ETHEREUM


class AbstractTx(ABC, json.JSONDecoder):
    """
    Абстрактный класс для десериализации транзакций.
    """
    tx_id = None
    sender = None
    amount = None

    # def __init__(self, *args, **kwargs):
    #     json.JSONDecoder.__init__(self, object_hook=self.hook, *args, **kwargs)
    #     # super(json.JSONDecoder, self).__init__(self, object_hook=self.hook, *args, **kwargs)

    @abstractmethod
    def hook(self, obj):
        pass

    @abstractmethod
    def is_valid(self):
        """
        Является ли транзакция пригодной, т.е. нужного типа и содержит правильный адрес получателя.
        :rtype: bool
        """
        pass

    @property
    @abstractmethod
    def platform(self):
        pass

    @property
    @abstractmethod
    def receiver(self):
        pass

    def __repr__(self):
        return "%r(%r, %r, %r)" % (self.__class__.__name__, self.tx_id, self.sender, self.amount)


class WavesTx(AbstractTx):
    """
    Waves транзакция.
    """

    _type = None
    _attachment = None

    @property
    def receiver(self):
        return self._attachment

    @property
    def platform(self):
        return PLATFORM_WAVES

    def hook(self, obj):
        self._type = obj['type']
        self._attachment = base58.b58decode(obj['attachment'])

        self.tx_id = obj['id']
        self.sender = obj['sender']
        self.amount = float(obj['amount'])

        # print(obj)

        return self

    def is_valid(self):
        return self._type == 4 and self._attachment


class EthereumTx(AbstractTx):
    """
    Ethereum транзакция.
    """

    @property
    def receiver(self):
        pass

    def is_valid(self):
        pass

    def hook(self, obj):
        pass

    @property
    def platform(self):
        return PLATFORM_ETHEREUM


# waves
j = """
[[ {
  "type" : 4,
  "id" : "6Zh4J5fU6g4jCx4SK6rqyHRiQuQCQi535KLtXaduaMBk",
  "sender" : "3MqtveWsgTE6jHzed32g8pp2YL7dkL8JvS3",
  "senderPublicKey" : "2WNJPxu5jARFGdh4vLVkZzU3GK5e5LHCBEZJYAsGjcg6",
  "fee" : 100000,
  "timestamp" : 1521568677040,
  "signature" : "4SVSrXtFVhZwmZnMkQTUpLevGmpnevXbBrkLNPqq4Y5KEjcyktZAqUq1rpnA25bmDpi3t3RSDy3j14sehppyAccX",
  "recipient" : "3MqtveWsgTE6jHzed32g8pp2YL7dkL8JvS3",
  "assetId" : null,
  "amount" : 100000000,
  "feeAsset" : null,
  "attachment" : "3Mwu6q9cjCa1pV5D254Hy",
  "height" : 301596
}, {
  "type" : 4,
  "id" : "hAW4bBCT5aA3PBpmpAqxEKYmYFb6DFdpDKQ9rbze5WP",
  "sender" : "3MqtveWsgTE6jHzed32g8pp2YL7dkL8JvS3",
  "senderPublicKey" : "2WNJPxu5jARFGdh4vLVkZzU3GK5e5LHCBEZJYAsGjcg6",
  "fee" : 100000,
  "timestamp" : 1521568080155,
  "signature" : "xfgvugnkVsniAV7dDRNrFBeXuFXmyQnzAMFz1FnpS6DDwAsW8UAJBTiyimafRLiUmn7wHCd41HdKsjtonSGdvKQ",
  "recipient" : "3MqtveWsgTE6jHzed32g8pp2YL7dkL8JvS3",
  "assetId" : null,
  "amount" : 100000000,
  "feeAsset" : null,
  "attachment" : "3Mwu6q9cjCa1pV5D254Hy",
  "height" : 301588
}, {
  "type" : 4,
  "id" : "GwXn5FdWK7S5zzzze5n3gmvh9zbFPMunFVvZFZPPNMHp",
  "sender" : "3NBVqYXrapgJP9atQccdBPAgJPwHDKkh6A8",
  "senderPublicKey" : "CRxqEuxhdZBEHX42MU4FfyJxuHmbDBTaHMhM3Uki7pLw",
  "fee" : 100000,
  "timestamp" : 1521564164430,
  "signature" : "5GANiiVUmrHPoGutFynhtw9ogWgDXxDzRpP1tWrGpscYbeX8vZbeie8n5vXGwVhL85rmyk9sDVhqWLC8UwygrfTv",
  "recipient" : "3MqtveWsgTE6jHzed32g8pp2YL7dkL8JvS3",
  "assetId" : null,
  "amount" : 1000000000,
  "feeAsset" : null,
  "attachment" : "",
  "height" : 301526
}]]

"""

class TTx:
    def __init__(self, tx_id):
        self.tx_id = tx_id

    def __repr__(self):
        return self.tx_id

# txs = json.loads(j, cls=WavesTx)

def obj_creator(d):

    # d = json.loads(d)

    return TTx(d['id'])

txs = json.loads(j, object_hook=obj_creator)

# print(txs)
for tx in txs:
    print(tx)
