from .hash_key_manager import HashKeyManager
from ..models import LogEntry

def verify_chain(site):
    """
    Verilen siteye ait hash zincirinin bütünlüğünü kontrol et.
    """
    logs = LogEntry.objects.filter(site=site).order_by('timestamp')
    previous_hash = None

    for log in logs:
        # Hash girdisini yeniden oluştur
        hash_key = HashKeyManager.get_key_for_timestamp(log.timestamp)
        hash_input = {
            "site": log.site.id,
            "user": log.user,
            "ip_address": log.ip_address,
            "browser": log.browser,
            "operating_system": log.operating_system,
            "model_name": log.model_name,
            "operation": log.operation,
            "previous_hashed_data": log.previous_hashed_data,
            "original_data": log.original_data,
            "timestamp": str(log.timestamp),
            "current_key": hash_key,
        }
        calculated_hash = LogEntry.hash_data(hash_input)

        # Mevcut hash ile eşleşmiyorsa zincir bozulmuştur
        if log.hashed_data != calculated_hash:
            return False, log

        previous_hash = log.hashed_data

    return True, None
