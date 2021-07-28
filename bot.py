import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from game import quiz
from pprint import pprint
import asyncio
import datetime
import csv
#from sheets import insertAnswers,createPlayers,createHeader

load_dotenv()
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$',intents=intents)
bot.remove_command('help')

curQuiz = None
onGame = False
seconds = 60

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def hello(ctx):
    await ctx.author.send("Hi! " + str(ctx.author.mention))

@bot.command()
async def start(ctx,num=None):
    global curQuiz,onGame

    if num == None:
        await ctx.send("Please mention total number of questions")
        return

    if onGame == True:
        await ctx.send("A quiz is already going on " + str(ctx.author.mention))
        return
    
    curQuiz=quiz(ctx.author,int(num))
    onGame=True
    #createHeader(int(num))
    await ctx.send("A new quiz is being started by " + str(ctx.author.mention))

    embed = discord.Embed(
        colour = discord.Colour.orange(),
        title = "Host Controls",
        description = "Command Prefix is $"
    )

    embed.add_field(name="next",value="Used to move to next question.",inline=False)
    embed.add_field(name="open <seconds>",value="Used to open for specifed seconds. Default 60s (If <seconds> is not specified)",inline=False)
    embed.add_field(name="close",value="Closes pounce for the question",inline=False)
    embed.add_field(name="preview <qnum>",value="preview a question. Default is next Question",inline=False)
    embed.add_field(name="quit",value="close the quiz",inline=False)
    embed.add_field(name="IMPORTANT : uploadQ",value="Upload the questions docx file in the specified format and in comments type $uploadQ\nOnce a file is uploaded it cant be changed.\n FORMAT - \n<QUESTION>\n<BLANK_LINE>\n<QUESTION>\n",inline=False)


    await ctx.author.send(embed=embed)
    await ctx.send("Join the quiz using $join")

@bot.command()
async def join(ctx):
    if await checkGame(ctx) == False : return

    global curQuiz
    if str(ctx.author) not in curQuiz.players.keys():
        curQuiz.join(str(ctx.author))
        #createPlayers(curQuiz.players)
        await ctx.author.send("You'll be pouncing here. To pounce use $pounce <answer>")
    else:
        await ctx.channel.send(str(ctx.author.mention) + "has already joined")

@bot.command()
async def pounce(ctx,*,args=None):
    
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.message.delete()
        await ctx.send(str(ctx.author.mention) + " Please pounce in DM, not in the channel")
        return

    if await checkGame(ctx) == False : return  
    
    global curQuiz

    if curQuiz.pounceOpen==False:
        await ctx.send("Pounce is Closed / Not Open Yet")
        return

    curQuiz.pounce(str(ctx.author),str(args))
    await ctx.author.send("Your pounce for Question " + str(curQuiz.curQuestion) + " was recorded")

@bot.command()
@commands.dm_only()
async def repeat(ctx):
    if curQuiz.pounceOpen==False:
        await ctx.send("Pounce is Closed / Not Open Yet")
        return
        
    qnum = curQuiz.curQuestion
    embed = discord.Embed(
        colour = discord.Colour.orange(),
        title = "Question " + str(qnum), 
        description = curQuiz.questions[qnum]
    )
    await ctx.send(embed=embed)

@bot.command()
async def next(ctx):
    if await checkHost(ctx) == False : return
    if await checkGame(ctx) == False : return

    if not curQuiz.questions :
        await ctx.author.send("You didnt add any questions")
        return
    
    if curQuiz.curQuestion == curQuiz.totalQuestions - 1:
        await ctx.channel.send("That was the last Question!")
        await quit(ctx)
    else:
        #if curQuiz.curQuestion != -1:
            #insertAnswers(curQuiz.curQuestion,curQuiz.responses)
        curQuiz.nextQuestion()
        await sendQ(ctx,curQuiz.curQuestion)

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        colour = discord.Colour.orange(),
        title = "Help",
        description = "Command Prefix is $"
    )
    
    embed.add_field(name="hello",value="Say Hi!",inline=False)
    embed.add_field(name="start <value>",value="Starts a quiz with <value> questions.",inline=False)
    embed.add_field(name="join",value="Join an ongoing quiz.",inline=False)
    embed.add_field(name="pounce <answer>",value="Used for answering in DM.",inline=False)
    embed.add_field(name="repeat",value="Reapeats the current question.(Only in DM)",inline=False)
    

    await ctx.send(embed=embed)

@bot.command()
async def debug(ctx):
    if await checkHost(ctx) == False : return
    if await checkGame(ctx) == False : return

    global onGame,curQuiz
    print("Game State is : " + str(onGame))
    print("Quiz host is : " + str(curQuiz.host))
    print("Total Questions : " + str(curQuiz.totalQuestions))
    print("Current Question is : " + str(curQuiz.curQuestion))
    print('Number of Players : ' + str(curQuiz.playerNum))
    print('Is Pounce Open : ' + str(curQuiz.pounceOpen))
    pprint(curQuiz.players.items())
    pprint(curQuiz.responses)

@bot.command()
async def open(ctx, sec: int = 60):
    global curQuiz,seconds
    
    if await checkHost(ctx) == False : return
    if await checkGame(ctx) == False : return
    if curQuiz.curQuestion == -1 :
        await ctx.author.send("Display Question First!")
        return
    
    try:
        seconds = int(sec)
        if seconds > 150:
            await ctx.send("I dont think im allowed to do go above 150 seconds.")
            raise BaseException
        if seconds <= 0:
            await ctx.send("Thats not how time travel works" + str(ctx.author.mention))
            raise BaseException
        message = await ctx.send("Timer: {seconds}")
        curQuiz.pounceOpen=True
        await dm_players(ctx,"Pounce for Question " + str(curQuiz.curQuestion) + " is open")

        while True:
            seconds -= 1
            if seconds == 10:
                await dm_players(ctx,"10 seconds until pounce closes.")
            if seconds <= 0:
                curQuiz.pounceOpen=False
                await message.edit(content="Ended!")
                break
            await message.edit(content=f"Timer: {seconds}")
            await asyncio.sleep(1)
        await ctx.send("Pounce is Closed")
    except ValueError:
        await ctx.send("Must be a number!")

@bot.command()
async def close(ctx):
    global curQuiz,seconds

    if curQuiz.pounceOpen == False:
        return

    if await checkHost(ctx) == False : return
    if await checkGame(ctx) == False : return

    seconds=0
    curQuiz.pounceOpen=False

@bot.command()
@commands.dm_only()
async def preview(ctx,args=None):
    if await checkHost(ctx) == False : return
    if await checkGame(ctx) == False : return

    if args==None:
        await sendQ(ctx,curQuiz.curQuestion+1)
    else:
        await sendQ(ctx,int(args))

    
async def dm_players(ctx,args):
    guild = ctx.message.guild
    for name in curQuiz.players.keys():
        member = guild.get_member_named(str(name))
        await member.send(str(args))


@bot.command()
async def uploadQ(ctx,args):
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.message.delete()
        return

    if await checkHost(ctx) == False : return
    if await checkGame(ctx) == False : return

    global curQuiz

    if str(args) == "test":
        curQuiz.generateQues("sample2.docx")
        await ctx.send("sample used")
        return

    if curQuiz.questions :
        await ctx.send("Questions are already present.To change quit the quiz and start again")
    else:
        fname = 'question_' + datetime.datetime.now().strftime("%y%m%d_%H%M%S") + ".docx"
        await ctx.message.attachments[0].save(fname)
        curQuiz.generateQues(fname)
        await ctx.send("Questions uploaded")

async def sendQ(ctx,qnum: int):
    embed = discord.Embed(
        colour = discord.Colour.orange(),
        title = "Question " + str(qnum), 
        description = curQuiz.questions[qnum]
    )
    curQuesMessage = await ctx.send(embed=embed)
    await curQuesMessage.add_reaction('🇧')
    await curQuesMessage.add_reaction('🇭')


@bot.command()
async def quit(ctx):

    if await checkHost(ctx) == False : return
    if await checkGame(ctx) == False : return

    global onGame,curQuiz

    await createLog(curQuiz.responses)

    curQuiz = None
    onGame = False
    await ctx.channel.send("Quiz has been closed")

async def createLog(res):
    fname = 'log_' + datetime.datetime.now().strftime("%y%m%d_%H%M%S") + ".csv"

    with open(fname, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(res)

async def checkGame(ctx):
    if onGame == False:
        await ctx.channel.send("No Quiz is Currently going on")
        return False
    return True

async def checkHost(ctx):
    if str(ctx.author) != str(curQuiz.host):
        await ctx.send("I'm sorry, "+ str(ctx.author.mention) +". I'm afraid I can't do that.")
        return False
    return True

bot.run(os.getenv('KEY'))