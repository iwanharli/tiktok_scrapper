import json 
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright 
from rich import print

keyword				    = "jokowi"
url 				    = "https://www.tiktok.com/search/video?q="+keyword

path_cookies    	    = "cookies.json"
path_contents		    = "result/contents_list.json"
path_contents_URL  	    = "result/contents_url_list.json"

current_scroll_attempt 	= 0
max_scroll_attempt 		= 10

response_count 			= 0 
response_get			= 6  #if 10 => 10*12 = 120 content

items_contents  	    = []
items_contents_URL 	    = []

with sync_playwright() as p:

	def explore_response(ress):
		global response_count

		if ("search/item/full/?aid=1988" in ress.url):
			json_data = ress.json()
			response_count += 1

			total_data = 0
			if 'item_list' in json_data:
				print("<<", ress.status, ress.url, "\n")
				
				total_data += json_data['cursor']
				for item in json_data['item_list']:

					items = {"video_id"              : item["id"]}

					items_contents.append(items)
					count = len(json_data['item_list'])

				print('>> GET \t\t=', count,'CONTENT')
			print('>> TOTAL \t=', total_data,'CONTENT')
			print("--------------------------------------------------------------------------------------")

	start_time 	= time.perf_counter() #GET TIME PROCESSING
	browser 	= p.chromium.launch(headless=False) 
	context		= browser.new_context()
	page    	= context.new_page()
	page.set_viewport_size({"width":1200, "height":1080})
	
	with open(path_cookies, 'r') as file:
		cookies_data = json.load(file)
	context.add_cookies(cookies_data)

	with open(path_contents, 'w') as file:
		file.write('')

	with open(path_contents_URL, 'w') as file:
		file.write('')

	
	page.on("response", explore_response) 
	
	page.goto(url, wait_until="networkidle", timeout=90000) 

	#SCROLL THE PAGE--------------------------------------------------------
	while True:

		previous_height = page.evaluate("document.body.scrollHeight")
		page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
		timeout = random.uniform(0.5, 2)    # Random timeout between 0.5 to 2 seconds
		page.wait_for_timeout(int(timeout * 1000))  # Convert to milliseconds
        # sleeptime = random.uniform(3, 7)
    

		new_height = page.evaluate("document.body.scrollHeight")
		if new_height == previous_height or response_count >= response_get:
			break

	count = len(items_contents)
	print()
	print("TOTAL CONTENT\t=",count)

	end_time = time.perf_counter()
	time_pc = end_time - start_time

	time_taken = time_pc/60
	print(f"TIME TAKEN \t= {time_taken:.2f} minutes")

	page.context.close() 
	browser.close()