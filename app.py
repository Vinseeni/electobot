import os
import sys
import json
import requests
from flask import Flask, request

app = Flask(__name__)

newsList = []

def findArticles():
    statusError =True
    while statusError ==True:
        r = requests.get('https://access.alchemyapi.com/calls/data/GetNews?apikey=519c0474356c6d4f16dfeffaae8a1e652aa03131&start=1474761600&end=1475452799&outputMode=json&count=3&q.enriched.url.title=A[trump^elections]&return=enriched.url.url,enriched.url.title&dedup=1')
        parsed_json = json.loads(r.text)
        if parsed_json['status'] =='OK':
            statusError==False  
            # print parsed_json
            for entry in parsed_json['result']['docs']:
                cleanedTitle = entry['source']['enriched']['url']['cleanedTitle']
                newsList.append(cleanedTitle)
                articleURL= entry['source']['enriched']['url']['url']
                newsList.append(articleURL)
                # print '\n'
            break;



findArticles()
counter = 0

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
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]
                    # if "trump" in message_text.lower():
                    #     send_message(sender_id, "seriously, trump???")
                    #     send_message(sender_id, "http://www.nytimes.com/2016/10/02/magazine/how-donald-trump-set-off-a-civil-war-within-the-right-wing-media.html")
                    # elif "hillary" in message_text.lower():
                    #     send_message(sender_id, "Hillary isnt too bad to be honest ")
                    #     send_message(sender_id, "http://www.latimes.com/nation/politics/trailguide/la-na-live-updates-trailguide-hillary-clinton-pounces-on-donald-1475266902-htmlstory.html")
                    # elif "undecided" in message_text.lower():
                    #     send_message(sender_id, "Then trust me and vote hillary! Here's the latest news about hillary")
                    #     send_message(sender_id, "http://www.latimes.com/nation/politics/trailguide/la-na-live-updates-trailguide-hillary-clinton-pounces-on-donald-1475266902-htmlstory.html")
                    # else :
                    #     send_message(sender_id, "Wassup! I've got election news just for you! Who is your pick: Trump, Hillary or Undecided?")
                    if "more" in message_text.lower():
                        counter+=2
                        send_message(sender_id,"More News:" + newsList[counter])
                        send_message(sender_id,newsList[counter+1])


                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
            

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
