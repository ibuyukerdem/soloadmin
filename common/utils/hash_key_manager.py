import hashlib
import os

from datetime import datetime


class HashKeyManager:
    @staticmethod
    def get_key_for_timestamp(timestamp):
        """
        Belirli bir zaman damgası için hash anahtarını döndürür.
        """
        # None kontrolü, geçerli zaman kullanılır
        if timestamp is None:
            timestamp = datetime.now()

        # Zaman damgasını Unix zamanına dönüştür
        if isinstance(timestamp, datetime):
            timestamp = timestamp.timestamp()

        # .env dosyasından periyot uzunluğunu al (varsayılan 15 dakika)
        hash_period = int(os.getenv("HASH_PERIOD_SECONDS", 900))  # 15 dakika = 900 saniye

        # İlgili periyodu hesapla
        period = int(timestamp // hash_period)

        # Sabit tuz ile hash anahtarını oluştur
        salt = "STATIC_SALT_FOR_HASH_KEY"
        key_input = f"{salt}:{period}"
        return hashlib.sha256(key_input.encode('utf-8')).hexdigest()
