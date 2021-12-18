import json
from time import ctime
from typing import Literal
from numpy.core.fromnumeric import size 
import requests
from PIL import Image,ImageDraw,ImageFont
import enum
import os
import numpy as np
from requests.api import patch
from datetime import *
import statistics


coreDataPath = "coreDatabase/"
databasePath = "databaseImages/"
paintedDatabasePath = "paintedDatabaseImages/"
externalDatabasePath =  "externalDatabaseImages/"
tempDatabasePath = "tempDatabaseImages/"
fontDatabase = "fontDatabase/"

class colorCategory (enum.Enum):
    COMMON = (128, 128, 128,255)
    UNCOMMON = (0, 255, 0,255)
    UNIQUE = (0, 153, 255,255)
    RARE = (255, 0, 255,255)
    EPIC = (255, 153, 0,255)
    LEGENDARY = (255, 0, 0,255)
    TEXT = (245,204,39,255)
    TEXTSTROKE = (0,0,0,255)

def GetMomoPhotoIDValue(requiredKey): 
    
    with open('{path}data.txt'.format(path = coreDataPath)) as f:
        data = f.readlines()
        dataCleared = [element.replace('[','') for element in data]
        data2Cleared = [element.replace(']','') for element in dataCleared]
        data3Cleared = [element.replace('\n','') for element in data2Cleared]
        data4Cleared = [element.replace(',','') for element in data3Cleared]
        data5Cleared = [element.replace(',','') for element in data4Cleared]
        data6Cleared = [element.replace('"','') for element in data5Cleared]
        data7Cleared = list(filter(len, data6Cleared))

    data_set = {}
    for i in data7Cleared:
        miniData = i.split('img')
        values = miniData[1]
        values = values.split('.')
        key = values[0].replace('/','')
        value =values[1]
        data_set[key] = value
    
    return  data_set[str(requiredKey)]

def DownloadDatabaseImages():
    from MOBOX import GetMomoPhotoLink
    with open("{path}data.txt".format(path = coreDataPath)) as f:
        data = f.readlines()
        dataCleared = [element.replace('[','') for element in data]
        data2Cleared = [element.replace(']','') for element in dataCleared]
        data3Cleared = [element.replace('\n','') for element in data2Cleared]
        data4Cleared = [element.replace(',','') for element in data3Cleared]
        data5Cleared = [element.replace(',','') for element in data4Cleared]
        data6Cleared = [element.replace('"','') for element in data5Cleared]
        data7Cleared = list(filter(len, data6Cleared))

        for i in data7Cleared:
            tempMOMOID = i.split("/")[-1].split(".")[0]
            tempPHOTOID = i.split("/")[-1].split(".")[1]
            tempPHOTOURL = GetMomoPhotoLink(tempMOMOID,tempPHOTOID)       
            with open('{path}{momoID}-{photoID}.png'.format(momoID = tempMOMOID,photoID = tempPHOTOID,path = databasePath), 'wb') as handle:
                imageResponse = requests.get(tempPHOTOURL, stream=True)
                if not imageResponse.ok:
                    print("NO IMAGE")
                for block in imageResponse.iter_content(512):
                    if not block:
                        break
                    handle.write(block)
        
def PaintDatabaseImages():
    from MOBOX import GetMomoRarity
    for f in os.listdir(databasePath):
        tempmomoID = f.split("-")[0]
        tempPhotoID = f.split("-")[1].split(".")[0]
        tempRarity = GetMomoRarity(tempmomoID)
       

        coreImage = Image.open('{path}{image}'.format(path = databasePath, image = f)).convert("RGBA")
        hashrateImage = Image.open('{path}hashrateCutted.png'.format(path = externalDatabasePath)).convert("RGBA")
        hashrateResizedImage = hashrateImage.resize((45,45))

        finalPaintedImage = Image.new('RGBA',(512,512),colorCategory[tempRarity].value)
        finalPaintedImage.paste(coreImage,(0,0),coreImage)
        finalPaintedImage.paste(hashrateResizedImage,(10,10),hashrateResizedImage)

        smallFont = ImageFont.truetype("{path}impact.ttf".format(path = fontDatabase),20)
        draw = ImageDraw.Draw(finalPaintedImage)

        #marka
        draw.text(((512/2-160),(512/2 +240)),"@MOMOCATCHERBOT",colorCategory.TEXT.value, stroke_width=2,stroke_fill=colorCategory.TEXTSTROKE.value,font =smallFont,anchor="mm")
        finalPaintedImage.save("{path}{mergedImage}.png".format(path =paintedDatabasePath, mergedImage = tempmomoID + "-" + tempPhotoID),"PNG")

def PaintImageTexts(hashrate,price,momoID,momoPhotoID):

    bigFont = ImageFont.truetype("{path}impact.ttf".format(path = fontDatabase),60)
    mediumFont = ImageFont.truetype("{path}impact.ttf".format(path = fontDatabase),30)


    paintedImage = Image.open('{path}{image}.png'.format(path = paintedDatabasePath, image = str(momoID) + "-" + str(momoPhotoID))).convert("RGBA")

    draw = ImageDraw.Draw(paintedImage)

    #busd
    draw.text(((512/2),(512/2 + 190)),"{price} BUSD".format(price = price),colorCategory.TEXT.value, stroke_width=3,stroke_fill=colorCategory.TEXTSTROKE.value,font =bigFont,anchor="mm")

    #hashrate
    draw.text(((512/2 -175),(512/2 -225 )),"{hashrate}".format(hashrate = hashrate),colorCategory.TEXT.value, stroke_width=2,stroke_fill=colorCategory.TEXTSTROKE.value,font =mediumFont,anchor="mm")
    
    paintedImage.save("{path}{tempImage}.png".format(path = tempDatabasePath, tempImage = str(momoID) + "-" + str(momoPhotoID)),"PNG")

def StopUserSets(userID):
    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data["users"]:
            if(i["userID"] == userID):
                i["status"] = "off"
    with open('{path}users.json'.format(path = coreDataPath), 'w', encoding='utf-8') as f:
        json.dump(data, f)

def StartUserSets(userID):
    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data["users"]:
            if(i["userID"] == userID):
                i["status"] = "on"
    with open('{path}users.json'.format(path = coreDataPath), 'w', encoding='utf-8') as f:
        json.dump(data, f)

def CheckUserSubscription(userID):
    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data["users"]:
            if(i["userID"] == userID):
                tempRDate = i["rDate"]
                tempEDate = i["eDate"]
                if(tempEDate != ""):
                    tempYear = int(tempEDate.split("-")[0])
                    tempMonth = int(tempEDate.split("-")[1])
                    tempDay = int(tempEDate.split("-")[2])

                    if(datetime(date.today().year, date.today().month, date.today().day) >  datetime(tempYear, tempMonth, tempDay)):
                        return False
                    else:
                        return True

def CheckUserDatabase(userID):
    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data["users"]:
            if(i["userID"] == userID):
                return True
        return False

def SaveUser(userID,userName):
    tempUser = {}
    tempUser["userID"] = userID
    tempUser["userName"] = str(userName)
    tempUser["sets"] = []
    tempUser["rDate"] = date.today()
    tempUser["eDate"] = ""
    tempUser["status"] = "off"
    isValid = False
    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data["users"]:
            if(i["userID"] == userID):
                isValid = True
    if(isValid == False):          
        data["users"].append(tempUser)
        with open('{path}users.json'.format(path = coreDataPath), 'w', encoding='utf-8') as f:
            json.dump(data, f,default=str)

def ClearAllDatabase():
    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
    data["users"].clear()
    with open('{path}users.json'.format(path = coreDataPath), 'w', encoding='utf-8') as f:
        json.dump(data, f)

def ClearUserSets(userID):
    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data["users"]:
            if(i["userID"] == userID):
                i["sets"].clear()
    with open('{path}users.json'.format(path = coreDataPath), 'w', encoding='utf-8') as f:
        json.dump(data, f)

def CheckUserSets(userID,set):
    from MOBOX import DictCompare

    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data["users"]:
            if(i["userID"] == userID):
                isValid = False
                for x in i["sets"]:
                    if(DictCompare(x,set)):
                        isValid = True
                
    return isValid

def GetOnlineUsers():
    tempOnlineUsers = []
    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data["users"]:
            if(i["status"] == "on"):
                tempOnlineUsers.append(i)
    return tempOnlineUsers

def SaveUserSet(userID,set):
    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data["users"]:
            if(i["userID"] == userID):
                i["sets"].append(set)
                i["status"] = "on"
    with open('{path}users.json'.format(path = coreDataPath), 'w', encoding='utf-8') as f:
        json.dump(data, f)

def GetUserSets(userID):
    with open('{path}users.json'.format(path = coreDataPath), 'r', encoding='utf-8') as f:
        data = json.load(f)
        for i in data["users"]:
            if(i["userID"] == userID):
                return i["sets"]

def GetTransactionHistory(momoID,dateRange):
    from MOBOX import transactionAPI
    from MOBOX import ago
    from MOBOX import headers
    from MOBOX import GetMomoPrice
    isDone = False
    tempPage = 1
    tempTransactionHistory = {"max":"UNKOWN","avg":"UNKOWN","med":"UNKOWN","min":"UNKOWN"}
    tempMomoTransactionList = []
    tempMomoTransactionPriceList = []
    
    while(isDone != True):
        requestURL = transactionAPI.format(page = tempPage,limit = 500)
        response = requests.get(requestURL,headers=headers)
        json_data = json.loads(response.content)
        for momoJson in json_data["list"]:
            if(momoJson["prototype"] == momoID):
                if(datetime.fromtimestamp(momoJson["crtime"]) > datetime(datetime.today().year,datetime.today().month,datetime.today().day - dateRange)):
                    tempMomoTransactionPriceList.append(GetMomoPrice(momoJson))
                    tempMomoTransactionList.append(momoJson)
                else:
                    isDone = True
        tempPage += 1
    if(len(tempMomoTransactionPriceList) > 0):          
        tempTransactionHistory["max"] = round(max(tempMomoTransactionPriceList),2)
        tempTransactionHistory["min"] = round(min(tempMomoTransactionPriceList),2)
        tempTransactionHistory["med"] = round(statistics.median(tempMomoTransactionPriceList),2)
        tempTransactionHistory["avg"] = round(sum(tempMomoTransactionPriceList) / len(tempMomoTransactionList),2)

    return  tempTransactionHistory


