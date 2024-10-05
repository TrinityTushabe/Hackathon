# health_advice/views.py

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .ussd_handler import USSDHandler

@csrf_exempt
def ussd_callback(request):
    if request.method == 'POST':
        session_id = request.POST.get('sessionId', None)
        phone_number = request.POST.get('phoneNumber', None)
        text = request.POST.get('text', '')

        ussd_handler = USSDHandler()
        response = ussd_handler.handle_request(session_id, phone_number, text)

        return HttpResponse(response, content_type='text/plain')

    return HttpResponse('Method not allowed', status=405)