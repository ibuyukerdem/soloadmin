from django.contrib.sites.models import Site

class SiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        try:
            site = Site.objects.get(domain=host)
            request.site = site
            request.module = site.module.module if hasattr(site, 'module') else None
        except Site.DoesNotExist:
            request.site = None
            request.module = None
        return self.get_response(request)
