import json
import os
import requests

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


VERIFY_TOKEN = "dormer_whatsapp_2026"


@csrf_exempt
def webhook(request):

    if request.method == "GET":
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if token == VERIFY_TOKEN:
            return HttpResponse(challenge)

        return HttpResponse("Invalid verify token", status=403)

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            print("WhatsApp:", data)

            message = data["entry"][0]["changes"][0]["value"]["messages"][0]

            customer_number = message["from"]

            send_whatsapp_message(
                customer_number,
                "👋 Welcome to Dormer Stay!\n\nHow can we help you?"
            )

        except Exception as e:
            print("Webhook error:", e)

        return JsonResponse({"status": "received"})

    return JsonResponse({"error": "Method not allowed"}, status=405)


def send_whatsapp_message(to, message):

    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN")

    url = f"https://graph.facebook.com/v26.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print("WhatsApp response:", response.status_code, response.text)