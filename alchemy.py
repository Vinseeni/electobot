import requests
import json
import csv
import time
import atexit
# r = requests.get('https://gateway-a.watsonplatform.net/calls/data/GetNews?outputMode=json&start=now-30d&end=now&count=5&enriched.url.concepts.concept.text=ipad&renriched.url.concepts.concept.text=ipadeturn=enriched.url.url,enriched.url.title&apikey=519c0474356c6d4f16dfeffaae8a1e652aa03131')

# r = requests.get('https://gateway-a.watsonplatform.net/calls/data/GetNews?outputMode=json&start=now-1d&end=now&count=5&q.enriched.url.concepts.concept.text=[US^elections]&return=enriched.url.url,enriched.url.title&apikey=519c0474356c6d4f16dfeffaae8a1e652aa03131')


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=scrape,
    trigger=IntervalTrigger(seconds=30),
    id='printing_job',
    name='Print date and time every five seconds',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())






def scrape():
statusError =True
while statusError ==True:
	r = requests.get('https://access.alchemyapi.com/calls/data/GetNews?apikey=519c0474356c6d4f16dfeffaae8a1e652aa03131&start=1474761600&end=1475452799&outputMode=json&count=5&q.enriched.url.title=A[trump^elections]&return=enriched.url.url,enriched.url.title&dedup=1')
	parsed_json = json.loads(r.text)
	if parsed_json['status'] =='OK':
		statusError==False	
		# print parsed_json
		with open('articledata.csv','wb') as csvfile:
			datawriter = csv.writer(csvfile)
			for entry in parsed_json['result']['docs']:
				newsList = []
				cleanedTitle = entry['source']['enriched']['url']['cleanedTitle']
				newsList.append(cleanedTitle)
				articleURL= entry['source']['enriched']['url']['url']
				newsList.append(articleURL)
				datawriter.writerow(newsList)
			# print '\n'
		break;


	


		