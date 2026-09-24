import json
import os
import requests

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


VERIFY_TOKEN = "dormer_whatsapp_2026"


@csrf_exempt
def webhook(request):

    # Meta webhook verification
    if request.method == "GET":
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if token == VERIFY_TOKEN:
            return HttpResponse(challenge)

        return HttpResponse("Invalid verify token", status=403)

    # Incoming WhatsApp messages
    if request.method == "POST":

        try:
            data = json.loads(request.body)

            print("WhatsApp:", data)

            # Check whether this is actually a message
            entry = data.get("entry", [])

            if not entry:
                return JsonResponse({"status": "received"})

            changes = entry[0].get("changes", [])

            if not changes:
                return JsonResponse({"status": "received"})

            value = changes[0].get("value", {})

            messages = value.get("messages", [])

            if not messages:
                return JsonResponse({"status": "received"})

            message = messages[0]

            customer_number = message.get("from")

            # Only handle text messages for now
            if message.get("type") != "text":
                send_whatsapp_message(
                    customer_number,
                    "Please send us a text message so we can help you."
                )
                return JsonResponse({"status": "received"})

            text = message.get("text", {}).get("body", "")
            text = text.strip().lower()

            print("Customer:", customer_number)
            print("Message:", text)

            # Main menu
            if text in ["hi", "hello", "hey", "start", "menu"]:
                send_whatsapp_message(
                    customer_number,
                    welcome_message()
                )

            # Rooms
            elif text in ["1", "rooms", "room", "beds", "bed"]:
                send_whatsapp_message(
                    customer_number,
                    rooms_message()
                )

            # Availability
            elif text in ["2", "availability", "available", "booking", "book"]:
                send_whatsapp_message(
                    customer_number,
                    availability_message()
                )

            # Facilities
            elif text in ["3", "facilities", "facility", "amenities"]:
                send_whatsapp_message(
                    customer_number,
                    facilities_message()
                )

            # Location
            elif text in ["4", "location", "address", "directions", "map"]:
                send_whatsapp_message(
                    customer_number,
                    location_message()
                )

            # Contact staff
            elif text in ["5", "contact", "staff", "manager", "help"]:
                send_whatsapp_message(
                    customer_number,
                    contact_message()
                )

            # Unknown message
            else:
                send_whatsapp_message(
                    customer_number,
                    unknown_message()
                )

            return JsonResponse({"status": "received"})

        except Exception as e:

            print("Webhook error:", str(e))

            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=200
            )

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405
    )


# ---------------------------------------
# MESSAGE CONTENT
# ---------------------------------------

def welcome_message():

    return """👋 Welcome to Dormer Stay!

How can we help you?

1️⃣ Rooms & Beds
2️⃣ Availability
3️⃣ Facilities
4️⃣ Location
5️⃣ Contact Staff

Reply with a number or type your question."""


def rooms_message():

    return """🛏️ Rooms & Beds

We offer comfortable accommodation at Dormer Stay.

For room/bunk availability and current options, please reply:

2️⃣ Availability

Or contact our staff for assistance."""


def availability_message():

    return """📅 Availability

Please send us:

• Check-in date
• Check-out date
• Number of guests

Example:

Check-in: 25 September
Check-out: 28 September
Guests: 2

Our staff can then help you with availability."""


def facilities_message():

    return """🏨 Facilities

Dormer Stay provides comfortable accommodation and common facilities for guests.

For complete information about our current facilities, please contact our staff.

5️⃣ Contact Staff"""


def location_message():

    return """📍 Location

Dormer Stay is located in Calicut, Kerala.

We can send you the exact location and directions.

Please contact our staff:

5️⃣ Contact Staff"""


def contact_message():

    return """👨‍💼 Contact Staff

Our staff will assist you with your enquiry.

Please send your question here and our team can help you."""


def unknown_message():

    return """Sorry, I didn't understand that. 🙂

Please choose an option:

1️⃣ Rooms & Beds
2️⃣ Availability
3️⃣ Facilities
4️⃣ Location
5️⃣ Contact Staff

You can also type "Hi" to see the menu."""


# ---------------------------------------
# SEND WHATSAPP MESSAGE
# ---------------------------------------

def send_whatsapp_message(to, message):

    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN")

    url = (
        f"https://graph.facebook.com/v26.0/"
        f"{phone_number_id}/messages"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
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
        json=payload,
        timeout=20
    )

    print(
        "WhatsApp response:",
        response.status_code,
        response.text
    )