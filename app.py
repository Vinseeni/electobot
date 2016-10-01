import os
import sys
import json
import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":
        for messaging_event  in data["entry"][0]["messaging"]:
                log(messaging_event)
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]
                    if message_text == "trump":
                        send_message(sender_id, "trump sucks yo ")
                        send_message(sender_id, "http://www.nytimes.com/2016/10/02/magazine/how-donald-trump-set-off-a-civil-war-within-the-right-wing-media.html")
                        break
                    elif message_text == "hillary":
                        send_message(sender_id, "hillary not too bad ")
                        send_message(sender_id, "http://www.latimes.com/nation/politics/trailguide/la-na-live-updates-trailguide-hillary-clinton-pounces-on-donald-1475266902-htmlstory.html")
                        break
                    elif message_text == "undecided":
                        send_message(sender_id, "then trust me and vote hillary")
                        send_message(sender_id, "http://www.latimes.com/nation/politics/trailguide/la-na-live-updates-trailguide-hillary-clinton-pounces-on-donald-1475266902-htmlstory.html")
                        break
                    else:
                        send_message(sender_id, "Wassup! Ready for election news? trump, hillary or undecided?")
                        break          
        

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
            break

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)



def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
