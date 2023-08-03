import json
import random 
import time
from datetime import datetime
from playwright.sync_api import sync_playwright 
from rich import print

keyword				= "jokowi"
url 				= "https://www.tiktok.com/search/video?q="+keyword

path_cookies    	= "cookies.json"
path_contents		= "result/contents_list.json"
path_contents_URL  	= "result/contents_url_list.json"

current_scroll_attempt 	= 0
max_scroll_attempt 		= 10

response_count 			= 0 
response_get			= 100  #if 10 => 10*12 = 120 content

end_of_page 			= ".tiktok-usx5e-DivNoMoreResultsContainer.eegew6e3"

items_contents  	= []
items_contents_URL 	= []

with sync_playwright() as p:

	def explore_response(ress):
		global response_count

		if ("search/general/preview/?aid=1988" in ress.url):
			data = ress.json()

			# Get user_input_query
			user_input_query = data["user_input_query"]
			
			result = []
			for item in data["sug_list"]:

				items = {
					"position"    : item["word_record"]["words_position"],
					"content"     : item["word_record"]["words_content"]
				}

				result.append(items)
				
			print (">> KEYWORD \t="		, user_input_query)
			print (">> SUGGESTION \t=", result)
			print("--------------------------------------------------------------------------------------")

		if ("search/item/full/?aid=1988" in ress.url):
			json_data = ress.json()
			response_count += 1

			total_data = 0
			if 'item_list' in json_data:
				print("<<", ress.status, ress.url, "\n")
				# print(json.dumps(response.json()), "\n")
				
				total_data += json_data['cursor']
				for item in json_data['item_list']:
					
					# CEK STIKER------------------
					try:
						sticker_array   = item["stickerOnItem"][0]["stickerText"]
						sticker_text    = ""
						for sticker in sticker_array:
							sticker_text += sticker +". "
					except KeyError: 
						sticker_text = "N/A"

					if "album" not in item["music"] or item["music"]["album"] is None:
						music_album = "N/A"
					else:
						music_album     = item["music"]["album"]

					items = {
							"video_id"              : item["id"],
							"video_desc"            : item['desc'],
							"video_sticker"         : sticker_text.replace('\n', ' '),
							"video_create_time"     : item["createTime"],
							"video_duration"        : item["video"]["duration"],
							"video_cover"           : item["video"]["cover"],
							"video_playCount"       : item["stats"]["playCount"],
							"video_diggCount"       : item["stats"]["diggCount"],
							"video_commentCount"    : item["stats"]["commentCount"],
							"video_shareCount"      : item["stats"]["shareCount"],
							"video_collectCount"    : item["stats"]["collectCount"],
							"author_id"             : item["author"]["id"],
							"author_username"       : item["author"]["uniqueId"],
							"author_name"           : item["author"]["nickname"],
							"author_biodata"        : item["author"]["signature"],
							"author_foto"           : item["author"]["avatarThumb"],
							"author_is_verified"    : item["author"]["verified"],
							"author_followingCount" : item["authorStats"]["followingCount"],
							"author_followerCount"  : item["authorStats"]["followerCount"],
							"author_heartCount"     : item["authorStats"]["heartCount"],
							"author_videoCount"     : item["authorStats"]["videoCount"],
							"author_diggCount"      : item["authorStats"]["diggCount"],
							"music_id"              : item["music"]["id"],
							"music_title"           : item["music"]["title"],
							"music_album"           : music_album,
							"music_authorName"      : item["music"]["authorName"],
							"music_coverThumb"      : item["music"]["coverThumb"]
					}

					url_key = f'https://www.tiktok.com/@{items["author_username"]}/video/{items["video_id"]}'

					key = {
						"url"	: url_key
					}

					items_contents.append(items)
					items_contents_URL.append(key)

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
	# page.on("response", lambda response: print("<<", response.status, response.url, "\n")) 
	# page.on("response", lambda response: explore_response(response)) 
	
	page.goto(url, wait_until="networkidle", timeout=90000) 

	#SCROLL THE PAGE--------------------------------------------------------
	while True:
		# element = page.query_selector('your-selector')
		# if element:
		# 	break # Element found, content stopped

		previous_height = page.evaluate("document.body.scrollHeight")
		page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
		page.wait_for_timeout(10000)
		
		sleep_time = random.uniform(1, 3)  # Random sleep between 1 to 5 seconds => more human-like behavior and avoid overwhelming the website's server with frequent requests
		time.sleep(sleep_time)
		# page.wait_for_load_state("networkidle")

		new_height = page.evaluate("document.body.scrollHeight") # save new scroll location
		if new_height == previous_height or response_count >= response_get:
			print("REACHED")
			break

		if page.locator(end_of_page).count() > 0:
			print("Reached the end of the content. Stopping scrolling.") # Check if the stop_selector exists on the page
			break

			# current_scroll_attempt += 1
			# if current_scroll_attempt > max_scroll_attempt:
			# 	break

	count = len(items_contents)
	print()
	print("TOTAL CONTENT\t=",count)

	with open(path_contents, "a") as outfile:
		json.dump(items_contents, outfile, indent=2)

	with open(path_contents_URL, "a") as outfile:
		json.dump(items_contents_URL, outfile, indent=2)

	end_time = time.perf_counter()
	time_pc = end_time - start_time

	time_taken = time_pc/60
	print(f"TIME TAKEN \t= {time_taken:.2f} minutes")

	page.context.close() 
	browser.close()