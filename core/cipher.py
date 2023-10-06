from abc import ABC, abstractmethod
from Crypto.Cipher import AES, ChaCha20
from Crypto.Util import Counter


# 定义基础 Cipher 接口
class Cipher(ABC):

    @abstractmethod
    def encode(self, data: bytes) -> bytes:
        pass

    @abstractmethod
    def decode(self, data: bytes) -> bytes:
        pass


# 具体实现

class ChaCha20Cipher(Cipher):
    def __init__(self, key: bytes, nonce: bytes):
        self.key = key
        self.nonce = nonce

    def encode(self, data: bytes) -> bytes:
        cipher = ChaCha20.new(key=self.key, nonce=self.nonce)
        return cipher.encrypt(data)

    def decode(self, data: bytes) -> bytes:
        cipher = ChaCha20.new(key=self.key, nonce=self.nonce)
        return cipher.decrypt(data)


class AES256CFBCipher(Cipher):
    def __init__(self, key: bytes, iv: bytes):
        self.key = key
        self.iv = iv

    def encode(self, data: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CFB, iv=self.iv)
        return cipher.encrypt(data)

    def decode(self, data: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CFB, iv=self.iv)
        return cipher.decrypt(data)


class AES256CTRCipher(Cipher):
    def __init__(self, key: bytes, nonce: int):
        self.key = key
        self.nonce = nonce

    def _create_cipher(self):
        ctr = Counter.new(64, prefix=self.nonce.to_bytes(8, 'big'))
        return AES.new(self.key, AES.MODE_CTR, counter=ctr)

    def encode(self, data: bytes) -> bytes:
        cipher = self._create_cipher()
        return cipher.encrypt(data)

    def decode(self, data: bytes) -> bytes:
        cipher = self._create_cipher()
        return cipher.decrypt(data)


class AES256OFBCipher(Cipher):
    def __init__(self, key: bytes, iv: bytes):
        self.key = key
        self.iv = iv

    def _create_cipher(self):
        return AES.new(self.key, AES.MODE_OFB, iv=self.iv)

    def encode(self, data: bytes) -> bytes:
        cipher = self._create_cipher()
        return cipher.encrypt(data)

    def decode(self, data: bytes) -> bytes:
        cipher = self._create_cipher()
        return cipher.decrypt(data)


class CipherFactory:
    @staticmethod
    def create_cipher(cipher_type: str, *args, **kwargs) -> Cipher:
        if cipher_type == "ChaCha20":
            return ChaCha20Cipher(*args, **kwargs)
        elif cipher_type == "AES-256-CFB":
            return AES256CFBCipher(*args, **kwargs)
        elif cipher_type == "AES-256-CTR":
            return AES256CTRCipher(*args, **kwargs)
        elif cipher_type == "AES-256-OFB":
            return AES256OFBCipher(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported cipher type: {cipher_type}")

# cipher = CipherFactory.create_cipher("AES-256-CTR", key, iv_or_nonce)
