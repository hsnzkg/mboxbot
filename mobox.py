from json.encoder import py_encode_basestring
from logging import NullHandler
from typing import final
from PIL.Image import RASTERIZE
from numpy import False_

import threading, queue
import requests
import json
import enum
import os

from time import sleep
from datetime import *
from requests.models import Response

import asyncio
import telegram

from telegram import message
from telegram import bot
from telegram import chat
from telegram import parsemode
from telegram import update
from telegram.constants import PARSEMODE_HTML, PARSEMODE_MARKDOWN, PARSEMODE_MARKDOWN_V2

import statistics

from telegram import ParseMode
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from telegram.ext import Defaults




#region ENUMS

class category (enum.Enum):
    ALL = "0"
    WIND = "1"
    EARTH = "2"
    WATER = "3"
    CREATURES = "4"
    HUMANS = "5"

class sort(enum.Enum):
   LTACC = "-time"
   LTDECC = "time"
   PACC = "price"
   PDEC = "-price"
   QUAACC = "hashrate"
   QUADEC = "-hashrate"

class pType (enum.Enum):
    DEFAULT = ''

class vType (enum.Enum):
    ALL = "0"
    COMMON = "1"
    UNCOMMON = "2"
    UNIQUE = "3"
    RARE = "4"
    EPIC = "5"
    LEGENDARY = "6"

class ago (enum.Enum):
    ONE = 1
    SEVEN = 7
    ALL = "ALL"

#endregion ENUMS

#region MOMOMARKET
currentvType = vType.UNIQUE
currentCategory = category.ALL
currentSort = sort.LTACC
currentPType = pType.DEFAULT
currentChain = 'BNB'
currentPage = 1
currentLimit = 15
momoMarketLR = []
momoMarketCTR = 5
momoMarketCSTR = 5
#endregion MOMOMARKET

#region TELEGRAM
channelID = "-1001746717168"
botID = "5074248859:AAHIOiI4-CnpoCX4Qb0XTqD6qbkY8x-go_Q"
#endregion TELEGRAM

#region URLS
momoMarketURL = 'https://www.mobox.io/home/#/iframe/momo?path=market&tab=0'
momoMarketAPI = 'https://nftapi.mobox.io/auction/search/{chain}?page={page}&limit={limit}&category={category}&vType={vType}&sort={sort}&pType={pType}'
momoMarketPAPI = 'https://www.mobox.io/momo/img/{key}.{value}.png'
transactionAPI = 'https://nftapi.mobox.io/auction/logs?&page={page}&limit={limit}'

#endregion URLS

#region TEXT MESSAGES
        
SETPOSITIVETEXT = "⏳ I WILL SEND YOU A MESSAGE WHEN\nANY *{rarity}* price  *{operator}* *BUSD{price}*\n"
WELCOMETEXT = "👋WELCOME👋 *{username}*\nOUR ADMINS WILL TAKE YOUR *REGISTER* PROCESS AND YOU WILL BE NOTIFIED *SOON*...\n*YOUR ID*: *{id}*"
MOMOPRICETEXT = "🔥*NEW MOMO LISTED*🔥\nPRICE: *{price} BUSD*\nHASHRATE: *{hashrate}*\nLEVEL: *{level}*\nRARITY: *{rarity}*\nDATE: *{date}*"

MOMOPRICEHISTORYTEXT = "⌛*PRICE HISTORY*⌛\n\n *YESTERDAY*\n🟢*MIN*: *{dailymin}* *BUSD* \n🔴*MAX*: *{dailymax}* *BUSD* \n🟡*AVG*: *{dailyavg}* *BUSD* \n🔵*MED*: *{dailymed}* *BUSD* \n\n *LAST WEEK*\n🟢*MIN*: *{weeklymin}* *BUSD*\n🔴*MAX*: *{weeklymax}* *BUSD*\n🟡*AVG*: *{weeklyavg}* *BUSD* \n🔵*MED*: *{weeklymed}* *BUSD*"

STARTTEXT = "*👋Welcome MOMO Catcher👋*\nThis bot can useful for catching *CHEAP MOMO's* in MOMO market before *EVERYONE*🔥\n\nYou can find bot *command usages* in */help*"
SPACETEXT = "\n\n"

STOPPROCESSTEXT = "⚠️STOPPING ALL */SET* PROCESS..."
STARTPROCESSTEXT = "⚠️STARTING ALL */SET* PROCESS..."
CLEARPROCESSTEXT = "⚠️CLEARING ALL */SET* PROCESS..."

REGISTERNEGATIVETEXT = "⚠️PLEASE PROVIDE A VALID */REGISTER* USAGE: \n FOR EXAMPLES PLEASE USE */help*"
REGISTERSECONDNEGATIVETEXT = "YOU ARE *ALREADY* REGISTERED !"

HELPTEXT = "For */set* required MOMO price range usage: */set* \n\n📗*OPERATOR EXAMPLES*📕\n\n*RARITY* : *COMMON | UNCOMMON | UNIQUE | RARE | EPIC | LEGENDARY*\n\n*OPERATOR* : * > <*\n\n*AMOUNT BUSD* : *100.2*\n\n *Example Set Usage* : */set |RARITY| |OPERATOR| |AMOUNTBUSD|*"
SETNEGATIVETEXT = "⚠️PLEASE *REGISTER* FIRST !\nFOR EXAMPLES PLEASE USE */help*"
SETSECONDNEGATIVETEXT = "⚠️YOUR MEMBERSHIP IS *EXPIRED* OR *NOT ACTIVATED*!\n PLEASE CONTACT ANY ADMIN VIA OUR GROUP : *https://t.me/MOMOCATCHER*"
SETTHIRDNEGATIVETEXT = "⚠️PLEASE PROVIDE A VALID */SET* USAGE: \n FOR EXAMPLES PLEASE USE */help*"
SETFOURTHNEGATIVETEXT = "⚠️YOU ALREADY SETTED THIS *SET* !*/SET* USAGE: \n FOR EXAMPLES PLEASE USE */help*"

UNKOWNTEXT = "⚠️You typed wrong *COMMAND* for help please use -> */help*"

#endregion TEXTMESSAGES

headers = {
    "accept":"application/json, text/plain, */*",
    "accept-encoding":"gzip, deflate, br",
    "connection":"keep-alive",
    'Content-Security-Policy': 'upgrade-insecure-requests',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'authority': 'bsc-dataseed2.binance.org',
    'scheme': 'https',
    'referrer': 'https://www.mobox.io/',
    'sec-ch-ua-platform': 'Windows',
    'referer':'https://www.mobox.io'
    }


def GetMomoPhotoID(MOMOID):
    from DBMANAGER import GetMomoPhotoIDValue
    return GetMomoPhotoIDValue(MOMOID)

def GetMomoPhotoLink(ID,PHOTOID):
    return momoMarketPAPI.format(key = str(ID), value = str(PHOTOID))

def GetMomoName(momoJson):
    #TODO
    return

def GetLastMomos(chain,page,limit,category,vType,sort):
    requestURL = momoMarketAPI.format(chain = chain, page = page , limit = limit,category = category,vType = vType,sort = sort, pType = currentPType)
    response = requests.get(requestURL,headers=headers)
    json_data = json.loads(response.content)
    for momojson in json_data["list"]:
        for key in momojson.keys():
            if(type(momojson[key]) == list):
                momojson[key] = tuple(momojson[key])
    return json_data["list"]

def GetMomoID(momoJson):
    if(momoJson):
        if(momoJson["prototype"]): 
            return momoJson["prototype"]
    else:   
        return "NO  DATA"

def GetMomoDate(momoJson):
    return datetime.fromtimestamp(momoJson["uptime"])
    
def GetMomoPrice(momoJson):
    if(momoJson):
        if("startPrice" in momoJson):
            return round(momoJson["startPrice"]/1000000000,2)
        elif("endPrice" in momoJson): 
            return round(momoJson["endPrice"]/1000000000,2)
        elif("bidPrice" in momoJson): 
            return round(momoJson["bidPrice"]/1000000000,2)
        else:
            return round(momoJson["nowPrice"]/1000000000,2)
    else:
        return("NO  DATA")

def GetMomoHashRate(momoJson):
    if(momoJson):
        if("lvHashrate" in momoJson):
            return momoJson["lvHashrate"]
        elif("hashrate" in momoJson): 
            return momoJson["hashrate"]
    else:
        return("NO  DATA")

def GetMomoRarity(momoID):
    tempMOMOID = momoID
    tempFirstIDLetter = str(tempMOMOID)[0]
    return  str(vType(tempFirstIDLetter).name)

def GetMomoLevel(momoJson):
    if(momoJson):
        if("level" in momoJson):
            return momoJson["level"]
    else:
        return("NO  DATA")

def GetMomoAllSpecs(momoJson):
    if(momoJson):
        specs = {}
        specs["momoID"] = GetMomoID(momoJson)
        specs["photoID"] = GetMomoPhotoID(GetMomoID(momoJson))
        specs["price"] = GetMomoPrice(momoJson)
        specs["level"] = GetMomoLevel(momoJson)
        specs["hashrate"] = GetMomoHashRate(momoJson)
        specs["photoLink"] = GetMomoPhotoLink(GetMomoID(momoJson),GetMomoPhotoID(GetMomoID(momoJson)))
        specs["rarity"] = GetMomoRarity(GetMomoID(momoJson))
        specs["date"] = GetMomoDate(momoJson)
        return specs
    else:
        return("NO  DATA")

def GetPriceHistoryText(momoID):
    tempDailyTransactionHistory = GetTransactionHistory(momoID,1)
    tempWeeklyTransactionHistory = GetTransactionHistory(momoID,7)


    return MOMOPRICEHISTORYTEXT.format(
        dailymin = tempDailyTransactionHistory["min"],
        dailymax = tempDailyTransactionHistory["max"],
        dailyavg = tempDailyTransactionHistory["avg"],
        dailymed = tempDailyTransactionHistory["med"],
        weeklymin = tempWeeklyTransactionHistory["min"],
        weeklymax = tempWeeklyTransactionHistory["max"],
        weeklyavg = tempWeeklyTransactionHistory["avg"],
        weeklymed = tempWeeklyTransactionHistory["med"])

def GetPriceText(momoJson):
    return MOMOPRICETEXT.format(date = momoJson["date"], price = momoJson["price"],hashrate = momoJson["hashrate"], level = momoJson["level"], rarity = momoJson["rarity"])
     
def startCommand(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=STARTTEXT,parse_mode = PARSEMODE_MARKDOWN)

def helpCommand(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=HELPTEXT,parse_mode = PARSEMODE_MARKDOWN)

def stopBotCommand(update,context):
    from DBMANAGER import StopUserSets
    response = STOPPROCESSTEXT
    context.bot.send_message(chat_id=update.effective_chat.id, text=response,parse_mode = PARSEMODE_MARKDOWN)
    StopUserSets(update.effective_chat.id)

def startBotCommand(update,context):
    from DBMANAGER import StartUserSets
    response = STARTPROCESSTEXT
    context.bot.send_message(chat_id=update.effective_chat.id, text=response,parse_mode = PARSEMODE_MARKDOWN)
    StartUserSets(update.effective_chat.id)

def registerCommand(update,context):
    from DBMANAGER import CheckUserDatabase,SaveUser
    
    if(len(context.args) > 0 and len(context.args ) < 2):
        if(CheckUserDatabase(update.effective_chat.id)):
            response = REGISTERSECONDNEGATIVETEXT
        else:
            SaveUser(update.effective_chat.id,str(context.args[0]))
            response = WELCOMETEXT.format(username = str(context.args[0]),id= str(update.effective_chat.id))       
    else:
        response = REGISTERNEGATIVETEXT
    context.bot.send_message(chat_id=update.effective_chat.id, text=response,parse_mode = PARSEMODE_MARKDOWN)

def setCommand(update, context):
    from DBMANAGER import CheckUserDatabase,CheckUserSubscription,CheckUserSets,SaveUserSet

    if  len(context.args) > 2 and len(context.args) < 4:
        boolOne = has_value(vType,context.args[0].upper())
        boolTwo = (str(context.args[1])) == '<' or (str(context.args[1])) == '>'
        boolThree = is_float(context.args[2])

        if  is_allTrue((boolOne,boolTwo,boolThree)):
            if CheckUserDatabase(update.effective_chat.id) and CheckUserSubscription(update.effective_chat.id):
                tempUserID = update.effective_chat.id
                tempRare = context.args[0].upper()
                tempOperator = context.args[1]
                tempPrice = context.args[2]

                tempSet = {
                    "RARITY":tempRare,
                    "OPERATOR":tempOperator,
                    "PRICE":tempPrice
                }
                if(CheckUserSets(tempUserID,tempSet)):
                    response = SETFOURTHNEGATIVETEXT.format(rarity = tempRare,operator = tempOperator , price = tempPrice)
                else:
                    SaveUserSet(tempUserID,tempSet)
                    response = SETPOSITIVETEXT.format(rarity = tempRare,operator = tempOperator , price = tempPrice)
            else:
                if(CheckUserDatabase(update.effective_chat.id) == False):
                    response = SETNEGATIVETEXT
                else:
                    response = SETSECONDNEGATIVETEXT
        else:
            response = SETTHIRDNEGATIVETEXT 
               
    else:
        response = SETTHIRDNEGATIVETEXT
    context.bot.send_message(chat_id=update.effective_chat.id, text=response,parse_mode = PARSEMODE_MARKDOWN)

def has_value(cls, value):
    return value in cls._member_names_

def is_float(element: any) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False

def is_allTrue(tuple):
    for i in tuple:
        if(i == False):
            return False
    return True

def setCallback(): 
    from DBMANAGER import GetOnlineUsers
    global momoMarketLR 
    sendables = []

    if(len(GetOnlineUsers()) > 0):   
        response = GetLastMomos(currentChain,currentPage,currentLimit,currentCategory,currentvType,currentSort)
        if(len(response) > 0):

            if(len(momoMarketLR) == 0):
                momoMarketLR = response
                sendables = momoMarketLR
            else:
                for newJSON in (response):
                    isAddeable = True
                    for oldJSON in (momoMarketLR):
                        if(DictCompare(newJSON,oldJSON) == True):
                            isAddeable = False
                    if(isAddeable == True):
                        sendables.append(newJSON)
                momoMarketLR = response

    if(len(sendables) > 0):    
        from DBMANAGER import GetOnlineUsers,PaintImageTexts,tempDatabasePath,GetUserSets
        for x in sendables:
            send = False
            tempSpecs = GetMomoAllSpecs(x)
            tempCurrentRarity = tempSpecs["rarity"]
            tempCurrentPrice = tempSpecs["price"]


            for user in GetOnlineUsers():
                if(len(GetUserSets(user["userID"]))> 0):
                    for i in GetUserSets(user["userID"]):
                        if i["OPERATOR"] == '<' and tempCurrentRarity == i["RARITY"]:
                            if float(i["PRICE"]) >= float(tempCurrentPrice):
                                send = True
                        else:
                            if float(i["PRICE"]) <= float(tempCurrentPrice)  and tempCurrentRarity == i["RARITY"]:
                                send = True
                    if(send):
                        PaintImageTexts(tempSpecs["hashrate"],tempSpecs["price"],tempSpecs["momoID"],tempSpecs["photoID"])
                        updater.bot.sendPhoto(chat_id=user["userID"], photo = open('{path}{momoID}-{photoID}.png'.format(path = tempDatabasePath,momoID = tempSpecs["momoID"],photoID = tempSpecs["photoID"]), 'rb'),caption = "{}".format(GetPriceText(tempSpecs) + SPACETEXT + GetPriceHistoryText(tempSpecs["momoID"])),parse_mode = PARSEMODE_MARKDOWN)
                        os.remove("{path}{momoID}-{photoID}.png".format(path = tempDatabasePath, momoID = tempSpecs["momoID"],photoID = tempSpecs["photoID"]))
   
    threading.Timer(momoMarketCTR,setCallback).start()




def GetTransactionHistory(momoID,dateRange):
    from MOBOX import transactionAPI
    from MOBOX import headers
    from MOBOX import GetMomoPrice
    from MOBOX import GetMomoID
    jsonQueue = queue.Queue()
    tempPage = 1
    tempTransactionHistory = {"max":"UNKOWN","avg":"UNKOWN","med":"UNKOWN","min":"UNKOWN"}
    tempMomosTransactionHistory = []    
    
    while (True):
        requestURL = transactionAPI.format(page = tempPage,limit = 1000)
        response = requests.get(requestURL,headers=headers)
        json_data = json.loads(response.content)
        tempMomosTransactionHistory.extend(json_data["list"])  
        if(datetime.fromtimestamp(json_data["list"][-1]["crtime"]) <  datetime(datetime.today().year,datetime.today().month,datetime.today().day - dateRange)):          
            break                       
        tempPage += 1

    tempMomoTransactionPriceList = list(map(GetMomoPrice, list(filter(lambda x: GetMomoID(x) == momoID, tempMomosTransactionHistory))))

    if(len(tempMomoTransactionPriceList) > 0):          
        tempTransactionHistory["max"] = round(max(tempMomoTransactionPriceList),2)
        tempTransactionHistory["min"] = round(min(tempMomoTransactionPriceList),2)
        tempTransactionHistory["med"] = round(GetListMed(tempMomoTransactionPriceList),2)
        tempTransactionHistory["avg"] = round(sum(tempMomoTransactionPriceList) / len(tempMomoTransactionPriceList),2)
    return  tempTransactionHistory


def GetListMed(list):
    return statistics.median(list)



def clearBotCommand(update,context):
    from DBMANAGER import ClearUserSets
    ClearUserSets(update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id, text=CLEARPROCESSTEXT,parse_mode = PARSEMODE_MARKDOWN)

def BotPCSession():
    global updater
    updater = Updater(botID,use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start',startCommand))
    dispatcher.add_handler(CommandHandler('help',helpCommand))
    dispatcher.add_handler(CommandHandler('register',registerCommand))
    dispatcher.add_handler(CommandHandler('set',setCommand))
    dispatcher.add_handler(CommandHandler('stopbot',stopBotCommand))
    dispatcher.add_handler(CommandHandler('startbot',startBotCommand))
    dispatcher.add_handler(CommandHandler('clearbot',clearBotCommand))


    updater.start_polling()  
    sleep(momoMarketCSTR)


    threading.Timer(momoMarketCTR,setCallback).start()
    updater.idle() 

def BotHerokuSession():
    global updater
    updater = Updater(botID,use_context=True)

   
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start',startCommand))
    dispatcher.add_handler(CommandHandler('help',helpCommand))
    dispatcher.add_handler(CommandHandler('register',registerCommand))
    dispatcher.add_handler(CommandHandler('set',setCommand))
    dispatcher.add_handler(CommandHandler('stopbot',stopBotCommand))
    dispatcher.add_handler(CommandHandler('startbot',startBotCommand))
    dispatcher.add_handler(CommandHandler('clearbot',clearBotCommand))
    
    PORT = int(os.environ.get('PORT', '8443'))
    updater.start_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=botID,
                        webhook_url="https://moboxbot.herokuapp.com/" + botID)
    
    sleep(momoMarketCSTR)
    threading.Timer(momoMarketCTR,setCallback).start()
    updater.idle()     

def DictCompare(d1, d2):
    d1_values = set(d1.values())
    d2_values = set(d2.values())


    sameValues = len(d1_values.intersection(d2_values))


    if(sameValues == len(d1_values) and sameValues == len(d2_values)):
        return True

    else:
        return False

if __name__ == '__main__':
    #from DBMANAGER import PaintDatabaseImages
    #PaintDatabaseImages()
    #DBMANAGER.DownloadDatabaseImages()  
    #BotPCSession() 
    s = datetime.now()
    print(GetPriceHistoryText(22001))   
    print( datetime.now() - s)