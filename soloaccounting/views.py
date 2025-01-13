from django.http import HttpResponseServerError

def trigger_error(request):
    raise Exception("Bu bir test hatasıdır.")