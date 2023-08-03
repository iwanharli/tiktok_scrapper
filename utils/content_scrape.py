def explore_response(ress):
    global response_count

    if ("search/item/full/?aid=1988" in ress.url):
        data_object = ress.json()
        response_count += 1

        if 'item_list' in data_object:
            print("<<", ress.status, ress.url, "\n")
            # print(json.dumps(response.json()), "\n")
        
            for item in data_object['item_list']:
                
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
            print("--------------------------------------------------------------------------------------")