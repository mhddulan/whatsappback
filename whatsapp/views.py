from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


VERIFY_TOKEN = "dormer_whatsapp_2026"


@csrf_exempt
def webhook(request):
    if request.method == "GET":
        verify_token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if verify_token == VERIFY_TOKEN:
            return HttpResponse(challenge)

        return HttpResponse("Invalid verify token", status=403)

    if request.method == "POST":
        data = json.loads(request.body)

        print("WhatsApp Webhook:", data)

        return JsonResponse({"status": "received"})

    return JsonResponse({"error": "Method not allowed"}, status=405)