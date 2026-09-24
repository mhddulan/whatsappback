import json
import os
import requests

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


VERIFY_TOKEN = "dormer_whatsapp_2026"

BOOKING_URL = "https://www.zotel.ai/hotels/dormer-stay-calicut-beach"


@csrf_exempt
def webhook(request):

    # Meta verification
    if request.method == "GET":
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if token == VERIFY_TOKEN:
            return HttpResponse(challenge)

        return HttpResponse("Invalid verify token", status=403)

    # Incoming messages
    if request.method == "POST":

        try:
            data = json.loads(request.body)

            print("WhatsApp:", data)

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

            # --------------------------------
            # TEXT MESSAGE
            # --------------------------------

            if message.get("type") == "text":

                text = (
                    message.get("text", {})
                    .get("body", "")
                    .strip()
                    .lower()
                )

                print("Customer:", customer_number)
                print("Message:", text)

                if text in ["hi", "hello", "hey", "start", "menu"]:
                    send_main_menu(customer_number)

                else:
                    send_unknown_message(customer_number)

            # --------------------------------
            # INTERACTIVE MENU RESPONSE
            # --------------------------------

            elif message.get("type") == "interactive":

                interactive = message.get("interactive", {})

                interaction_type = interactive.get("type")

                # List menu selection
                if interaction_type == "list_reply":

                    selected_id = (
                        interactive
                        .get("list_reply", {})
                        .get("id")
                    )

                    print("Selected:", selected_id)

                    handle_menu_selection(
                        customer_number,
                        selected_id
                    )

            return JsonResponse({"status": "received"})

        except Exception as e:

            print("Webhook error:", str(e))

            return JsonResponse(
                {
                    "status": "error",
                    "message": str(e)
                },
                status=200
            )

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405
    )


# =====================================================
# MAIN MENU
# =====================================================

def send_main_menu(to):

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
        "type": "interactive",
        "interactive": {
            "type": "list",

            "header": {
                "type": "text",
                "text": "Dormer Stay"
            },

            "body": {
                "text": (
                    "👋 Welcome to Dormer Stay!\n\n"
                    "Please choose an option below 👇"
                )
            },

            "footer": {
                "text": "Dormer Stay Calicut"
            },

            "action": {
                "button": "View Options",

                "sections": [
                    {
                        "title": "How can we help?",
                        "rows": [

                            {
                                "id": "rooms",
                                "title": "🛏️ Rooms & Beds",
                                "description": "View our accommodation options"
                            },

                            {
                                "id": "availability",
                                "title": "📅 Check Availability",
                                "description": "Check dates and availability"
                            },

                            {
                                "id": "booking",
                                "title": "🔗 Create Booking",
                                "description": "Book your stay online"
                            },

                            {
                                "id": "facilities",
                                "title": "🏨 Facilities",
                                "description": "View available facilities"
                            },

                            {
                                "id": "location",
                                "title": "📍 Location",
                                "description": "Find Dormer Stay"
                            },

                            {
                                "id": "contact",
                                "title": "👨‍💼 Contact Staff",
                                "description": "Talk to our staff"
                            }

                        ]
                    }
                ]
            }
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=20
    )

    print(
        "Menu response:",
        response.status_code,
        response.text
    )


# =====================================================
# MENU SELECTION HANDLER
# =====================================================

def handle_menu_selection(to, selected_id):

    if selected_id == "rooms":

        send_whatsapp_message(
            to,
            """🛏️ Rooms & Beds

We offer comfortable accommodation at Dormer Stay.

Our team can help you with available room and bed options.

📅 To check availability, choose Check Availability from the menu."""
        )

    elif selected_id == "availability":

        send_whatsapp_message(
            to,
            """📅 Check Availability

Please send us:

• Check-in date
• Check-out date
• Number of guests

Example:

Check-in: 25 September
Check-out: 28 September
Guests: 2

Our staff will help you with availability."""
        )

    elif selected_id == "booking":

        send_whatsapp_message(
            to,
            f"""🔗 Create Booking

You can complete your booking securely through our booking website.

👉 {BOOKING_URL}

Select your dates and complete your booking there.

Thank you for choosing Dormer Stay! ❤️"""
        )

    elif selected_id == "facilities":

        send_whatsapp_message(
            to,
            """🏨 Facilities

We are preparing our complete facilities list.

For more information, please contact our staff.

👨‍💼 Contact Staff"""
        )

    elif selected_id == "location":

        send_whatsapp_message(
            to,
            """📍 Dormer Stay Calicut

Our team can send you the exact location and directions.

Please contact our staff for assistance."""
        )

    elif selected_id == "contact":

        send_whatsapp_message(
            to,
            """👨‍💼 Contact Staff

Please send your question here.

Our staff will assist you as soon as possible."""
        )

    else:

        send_unknown_message(to)


# =====================================================
# UNKNOWN MESSAGE
# =====================================================

def send_unknown_message(to):

    send_whatsapp_message(
        to,
        """Sorry, I didn't understand that. 🙂

Please type "Hi" to see the Dormer Stay menu."""
    )


# =====================================================
# NORMAL TEXT MESSAGE
# =====================================================

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