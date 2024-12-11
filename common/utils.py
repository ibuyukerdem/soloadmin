from django.core.paginator import Paginator
from rest_framework.response import Response

def paginate_or_default(queryset, serializer_class, request, default_limit=20):
    """
    Sayfalama mekanizmasını kullan veya varsayılan olarak belirli bir limit kadar kayıt döndür.

    Args:
        queryset (QuerySet): Filtrelenmiş sorgu seti.
        serializer_class (Serializer): DRF Serializer sınıfı.
        request (Request): HTTP isteği.
        default_limit (int): Sayfalama olmadığında dönecek kayıt sayısı.

    Returns:
        Response: Sayfalı veya varsayılan limitli bir yanıt.
    """
    # DRF'nin sayfalama mekanizmasını kullan
    view = request.parser_context['view']  # DRF view instance
    page = view.paginate_queryset(queryset)
    if page is not None:
        serializer = serializer_class(page, many=True)
        return view.get_paginated_response(serializer.data)

    # Eğer sayfalama devrede değilse varsayılan limit kadar döndür
    paginator = Paginator(queryset, default_limit)
    first_page = paginator.page(1)
    serializer = serializer_class(first_page.object_list, many=True)
    return Response(serializer.data)
