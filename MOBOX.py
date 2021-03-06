
import requests
import json
import enum
import os
import threading
from time import sleep
from datetime import *
from telegram.constants import  PARSEMODE_MARKDOWN
import statistics
from telegram.ext.updater import Updater
from telegram.ext.commandhandler import CommandHandler
from telegram.ext import RegexHandler,MessageHandler
from telegram.ext import Filters


#region TRANSACTION
transactionCTR = 3600
dailyTransactionList = []
weeklyTransactionList = []
#endregion TRANSACTION



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
momoMarketCTR = 1
momoMarketCSTR = 10
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

HELPTEXT = "*ALL COMMANDS*\n*/start* Welcome Command\n*/help* Help Command\n*/set* Create Rule Command\n*/startbot* Start Rules Command\n*/stopbot* Stop Rules Command\n*/clearbot* Clear All Rules Command\n*/register* Register Command"
HELPTEXT1 = "📗*SET OPERATORS*📕\n\n*RARITY* : *COMMON | UNCOMMON | UNIQUE | RARE | EPIC | LEGENDARY*\n\n*OPERATOR* : * > <*\n\n*AMOUNT BUSD* : *100.2*\n\n*Example Set Usage* : */set |RARITY| |OPERATOR| |AMOUNTBUSD|* \n\n"
HELPTEXT2 = "📗*REGISTER OPERATORS*📕\n\n*USERNAME* : *YOUR USERNAME* \n*Example Register Usage*:/register *YOUR_USERNAME*"
SETNEGATIVETEXT = "⚠️PLEASE *REGISTER* FIRST !\nFOR EXAMPLES PLEASE USE */help*"
SETPOSITIVETEXT = "⏳ I WILL SEND YOU A MESSAGE WHEN\nANY *{rarity}* price  *{operator}* *{price} BUSD*\n"
SETSECONDNEGATIVETEXT = "⚠️YOUR MEMBERSHIP IS *EXPIRED* OR *NOT ACTIVATED*!\n PLEASE CONTACT ANY ADMIN VIA OUR GROUP : *https://t.me/MOMOCATCHER*"
SETTHIRDNEGATIVETEXT = "⚠️PLEASE PROVIDE A VALID */SET* USAGE: \n FOR EXAMPLES PLEASE USE */help*"
SETFOURTHNEGATIVETEXT = "⚠️YOU ALREADY SETTED THIS *SET* !"

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
    context.bot.send_message(chat_id=update.effective_chat.id, text=HELPTEXT1,parse_mode = PARSEMODE_MARKDOWN)
    context.bot.send_message(chat_id=update.effective_chat.id, text=HELPTEXT2,parse_mode = PARSEMODE_MARKDOWN)

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




def DownloadDailyTransactionHistory():
    global dailyTransactionList

    print("Downloading Daily Transaction History...")
    tempMomosTransactionHistory = [] 
    tempPage = 1
    while (True):
        requestURL = transactionAPI.format(page = tempPage,limit = 5000)
        response = requests.get(requestURL,headers=headers)
        json_data = json.loads(response.content)
        tempMomosTransactionHistory.extend(json_data["list"])
        tempDate = datetime.today()  
        if(datetime.fromtimestamp(json_data["list"][-1]["crtime"]) <  datetime(tempDate.year,tempDate.month,tempDate.day - 1)):          
            break                       
        tempPage += 1
    dailyTransactionList = tempMomosTransactionHistory
    threading.Timer(transactionCTR,DownloadDailyTransactionHistory).start()



def DownloadWeeklyTransactionHistory():
    global weeklyTransactionList

    print("Downloading Daily Transaction History...")
    tempMomosTransactionHistory = [] 
    tempPage = 1
    while (True):
        requestURL = transactionAPI.format(page = tempPage,limit = 5000)
        response = requests.get(requestURL,headers=headers)
        json_data = json.loads(response.content)
        tempMomosTransactionHistory.extend(json_data["list"])
        tempDate = datetime.today()  
        if(datetime.fromtimestamp(json_data["list"][-1]["crtime"]) <  datetime(tempDate.year,tempDate.month,tempDate.day - 7)):          
            break                       
        tempPage += 1
    weeklyTransactionList = tempMomosTransactionHistory
    threading.Timer(transactionCTR,DownloadWeeklyTransactionHistory).start()


def GetTransactionHistory(momoID,dateRange):   
    tempTransactionHistory = {"max":"UNKOWN","avg":"UNKOWN","med":"UNKOWN","min":"UNKOWN"}
    sortStart = datetime.now()
    tempJSONDataList = dailyTransactionList if dateRange==1 else weeklyTransactionList
    if(len(tempJSONDataList) > 0):
        tempMomoTransactionPriceList = list(map(GetMomoPrice, list(filter(lambda x: GetMomoID(x) == momoID,tempJSONDataList))))   
        if(len(tempMomoTransactionPriceList) > 0):          
            tempTransactionHistory["max"] = round(max(tempMomoTransactionPriceList),2)
            tempTransactionHistory["min"] = round(min(tempMomoTransactionPriceList),2)
            tempTransactionHistory["med"] = round(GetListMed(tempMomoTransactionPriceList),2)
            tempTransactionHistory["avg"] = round(sum(tempMomoTransactionPriceList) / len(tempMomoTransactionPriceList),2)
    sortEnd = datetime.now()  
    print("sorttime",sortEnd - sortStart)
    return  tempTransactionHistory


def GetListMed(list):
    return statistics.median(list)

def unknownBotCommand(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=UNKOWNTEXT,parse_mode = PARSEMODE_MARKDOWN)

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
    dispatcher.add_handler(MessageHandler(Filters.text, unknownBotCommand))


    updater.start_polling()  


    t1 = threading.Timer(0,DownloadDailyTransactionHistory)
    t2 = threading.Timer(0,DownloadWeeklyTransactionHistory)
    t3 = threading.Timer(momoMarketCSTR,setCallback)

    t1.daemon = True
    t2.daemon = True
    t3.daemon = True


    t1.start()
    t2.start()
    t3.start()



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
    dispatcher.add_handler(MessageHandler(Filters.text, unknownBotCommand))
    
    PORT = int(os.environ.get('PORT', '8443'))
    updater.start_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=botID,
                        webhook_url="https://moboxbot.herokuapp.com/" + botID)
    
   

    t1 = threading.Timer(0,DownloadDailyTransactionHistory)
    t2 = threading.Timer(0,DownloadWeeklyTransactionHistory)
    t3 = threading.Timer(momoMarketCSTR,setCallback)
    t1.daemon = True
    t2.daemon = True
    t3.daemon = True


    t1.start()
    t2.start()
    t3.start()

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
    BotHerokuSession() 
