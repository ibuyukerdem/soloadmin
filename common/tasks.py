from celery import shared_task
from common.models import LogEntry
from common.utils.hash_chain_verifier import verify_chain
from django.contrib.sites.models import Site

@shared_task
def verify_all_sites():
    """
    Tüm sitelerde hash zincirini kontrol eden Celery görevi.
    """
    sites = Site.objects.all()
    for site in sites:
        is_valid, corrupted_log = verify_chain(site)
        if not is_valid:
            print(f"Zincir bozulmuş! Problemli kayıt: {corrupted_log}")
        else:
            print(f"Site '{site.domain}' için zincir sağlam.")
