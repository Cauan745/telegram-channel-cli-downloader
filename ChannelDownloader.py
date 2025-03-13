import time
import sys
import os

from pathlib import Path

from telethon import events, utils
from telethon.sync import TelegramClient
from telethon.tl import types
from telethon.tl.types import PeerUser, PeerChat, PeerChannel

from FastTelethon import download_file, upload_file


api_id: int = 23551167 #int(input("Type the API_ID: ")) 
api_hash: str = "0cc102a7881744ac65a7631524dea6f1" #input("Type the API_HASH: ")
#token = input() #"7790387146:AAHJkD6Ad4yVHInpPH3E-O8iqD0ZdinmQn8"

client = TelegramClient("anon", api_id, api_hash)

client.start(phone=5569993558523)#int(input("Type your phone number: ")))

#"
# "

class Timer:
    def __init__(self, time_between=2):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False


def clear_console():
    # Clear console based on the operating system
    if os.name == 'nt':
        os.system('cls')  # For Windows
    else:
        os.system('clear')  # For Unix/Linux/Mac


async def downloadFile(path,targetChannel,fileToDownload,fileName):
    timer = Timer()

    async def progress_bar(current, total):
        if timer.can_send():
            print("\r{}: {}%".format(fileName, int(current * 100 / total)),end="", flush=True)

    if fileToDownload:
        print("")
        with open(path/fileName, "wb") as out:
            # Creating a backup of stderr
            old_stderr = sys.stderr

            # Creating a new stderr to stop "Server closed the connection" messages
            sys.stderr = open(os.devnull, "w")
            
            try:
                await download_file(client, fileToDownload, out, progress_callback=progress_bar)
                print("\r{}: {}%".format(fileName, 100))
                sys.stderr = old_stderr
            except:
                sys.stderr = old_stderr
                print("\nError downloading file: " + fileName)


async def isFileAlreadyDownloaded(path):
    if(Path(path).is_file()):
        return True
    else:
        return False

async def downloadFiles(path,targetChannel):
    async for message in client.iter_messages(targetChannel,reverse=True):
        fileName = ""
        document = None

        if(message.video):
            fileName = message.media.document.attributes[1].file_name
            document = message.media.document

        elif(message.document):
            fileName = message.document.attributes[0].file_name
            document = message.document

        else:
            continue
        
        if(await isFileAlreadyDownloaded(path/fileName)):
            print("File already downloaded: " + fileName)
            continue
        
        await downloadFile(path,targetChannel,document,fileName)


async def checkDownloadedFiles(path,targetChannel):
    async for message in client.iter_messages(targetChannel,reverse=True):
        fileName = ""
        
        if(message.video or message.photo):
            fileName = message.media.document.attributes[1].file_name

        elif(message.document):
            fileName = message.document.attributes[0].file_name

        else:
            continue

        if(await isFileAlreadyDownloaded(path/fileName)):
            print("Downloaded - " + fileName)
        else:
            print("Missing - " + fileName)

            

async def main():

    userDownloadsFolderPath = Path.home() / 'Downloads'

    option = 999

    while(option != 0):

        clear_console()

        print(f"Choose one of the options")
        print("1 - Download all files from channel")
        print("2 - Verify all downloaded files from channel")
        print("0 - Close the program")
        option = int(input())

        if(option == 0):
            break

        targetChannelId = int(input("Type the channel id: "))
        targetChannel = await client.get_entity(PeerChannel(targetChannelId))
        channelTitle = targetChannel.title
        
        path = userDownloadsFolderPath / channelTitle
        channelFolderExists = os.path.exists(path)
        
        clear_console()
        print("Looking into channel: " + channelTitle)

        if(option == 1):
            if not channelFolderExists:
                os.mkdir(path)
            await downloadFiles(path,targetChannel)
            input("Download finished, press enter to continue ")

        elif(option == 2):
            if not channelFolderExists:
                print("No files downloaded")
            else:
                await checkDownloadedFiles(path,targetChannel)
            input("Press enter to continue ")
    
    await client.disconnect()

import asyncio

loop = asyncio.get_event_loop()
result = loop.run_until_complete(main())

loop.close()
