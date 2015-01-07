# -*- coding: utf-8 -*-


'''
Author: Ax3 (Nazar Kravtsov)
http://vk.com/ax3effect
http://github.com/ax3effect/
'''

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import core as _imaging
import vk
import time, threading
import requests
import json
import traceback
import urllib.request

# Settings
group_id = "-64682296" # enter group id here, see https://vk.com/dev/utils.resolveScreenName
album_id = "208971769" # album id, can be found in the URL after userid_
user_id = "277044695" # userid, https://vk.com/dev/utils.resolveScreenName
watermark_text = "sample text" # text
checkInterval = 60 # in seconds, wall checking interval

# Config
from datetime import datetime
from random import randint
from configobj import ConfigObj
config = ConfigObj("settings.ini")
vk_access_token = config['vk_token']

# Watermark function
def watermarkit():
    # black magic here
    txt = watermark_text
    # Open the original image
    main = Image.open("image_downloaded.jpg")
 
    # Create a new image for the watermark with an alpha layer (RGBA)
    #  the same size as the original image
    watermark = Image.new("RGBA", main.size)
    # Get an ImageDraw object so we can draw on the image
    waterdraw = ImageDraw.ImageDraw(watermark, "RGBA")

    fontsize = 1  # starting font size

    # portion of image width you want text width to be
    img_fraction = 0.70

    font = ImageFont.truetype("arial.ttf", fontsize)
    while font.getsize(txt)[0] < img_fraction*main.size[0]:
    # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype("arial.ttf", fontsize)


 
    # Get the watermark image as grayscale and fade the image
    fontsizeblack = fontsize + 1
    # fontblack = ImageFont.truetype("arial.ttf", fontsizeblack)
    # waterdraw.text((8, 8), txt, (60,20,20), font=fontblack)
    # Place the text at (10, 10) in the upper left corner. Text will be white.
    waterdraw.text((10, 10), txt, font=font)
    watermask = watermark.convert("L").point(lambda x: min(x, 100))
    # Apply this mask to the watermark image, using the alpha filter to 
    #  make it transparent
    watermark.putalpha(watermask)
 
    # Paste the watermark (with alpha layer) onto the original image and save it
    main.paste(watermark, None, watermark)
    main.save("image_watermarked.jpg", "JPEG")
 

# Save image
def saveimage(imgurl):
    image_name = 'image_downloaded.jpg'
    urllib.request.urlretrieve(imgurl, image_name)


def postWatermark():
    wallInfo = vkapi.wall.get(owner_id = group_id, count = 1, offset = 1) # get wall info
    #print wallInfo
    # ----- parse wall get info -----
    photoinfo1 = wallInfo["items"][0]
    try:
        posttext = photoinfo1["text"]
        print(posttext)
    except Exception:
        posttext = ""
        pass
    postId = photoinfo1["id"] # post ID
    photoinfo2 = photoinfo1["attachments"][0]
    photoinfo3 = photoinfo2["photo"]
    photoinfo4 = photoinfo3["photo_604"] # photo ID
    saveimage(photoinfo4) # save it as test2.jpg
    watermarkit() # watermark

    configRead = ConfigObj("wall.ini")
    wallcheck = configRead['wallid']
    print(str(wallcheck) + "---" + str(postId))
    configWrite = ConfigObj()
    configWrite.filename = "wall.ini"
    if int(wallcheck) != int(postId):
        print("Change found!")
        configWrite['wallid'] = postId
        configWrite.write()
        upload(postId, posttext)
    else:
        pass
        #print("Change NOT found!")


    # ----- Upload photo to VK Album -----
def upload(postId, posttext):


    photo_serverid = vkapi.photos.getUploadServer(album_id = album_id)
    photo_serverid_url = photo_serverid["upload_url"]
    r = requests.post(photo_serverid_url, files={'file1': open('image_watermarked.jpg', 'rb')})
    photos_save = r.json()
    photo_save_result = vkapi.photos.save(album_id = album_id, server = photos_save["server"], photos_list = photos_save["photos_list"], hash = photos_save["hash"])
    readyphotoid = photo_save_result[0]["id"]
    photoPublicID = "photo" + str(user_id) + "_" + str(readyphotoid)

    # ----- edit -----
    vkapi.wall.edit(owner_id = group_id, post_id = postId, attachments = photoPublicID, message = posttext)
    #print("done")


# ----- Main -------
vkapi = vk.API(access_token=vk_access_token)
print("Watermark Bot Launched -- vk.com/ax3effect")

while True:
    try:
        postWatermark()
    except Exception:
        #for debug
        traceback.print_exc()
        time.sleep(checkInterval)
        pass
    time.sleep(checkInterval)