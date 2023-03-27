import discord
import asyncio
from discord.ext import commands
import time
import os
import json
import datetime
import random





intents = discord.Intents.all()
client = commands.Bot(command_prefix='$', intents=intents)

client.remove_command('help')

daily_cd = {}
weekly_cd = {}
monthly_cd = {}
yearly_cd = {}

@client.event
async def on_ready():
    activity = discord.Game(name="Vic Nik the Goat", type=3)
    await client.change_presence(status=discord.Status.idle, activity=activity)
    print('Bot is ready')






mainshop = [{"name":"Vbucks","price":100,"description":"Currency"},
            {"name":"Blue","price":500,"description":"Get a role with the color blue. After purchasing, use $use blue"},
            {"name":"Rolex","price":1000,"description":"Time"},
            {"name":"Tesla","price":10000,"description":"Modern Car"},
            {"name":"Lambo","price":99999,"description":"Sports Car"}]

@client.command(aliases=['bal'])
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title=f'{ctx.author.name} Balance',color = discord.Color(0xff0000))
    em.add_field(name="Wallet Balance", value=wallet_amt)
    em.add_field(name='Bank Balance',value=bank_amt)
    await ctx.send(embed= em)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = "**Still On Cooldown!**, Plese try again in {:.2f}s".format(error.retry_after)
        await ctx.send(msg)


@client.command()
@commands.cooldown(1,60,commands.BucketType.user)
async def beg(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    earnings = random.randrange(101)

    await ctx.send(f'{ctx.author.mention} Got {earnings} coins!!')

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json",'w') as f:
        json.dump(users,f)


@client.command()
async def daily(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    earnings = 50

    
    if user.id in daily_cd and (datetime.datetime.now() - daily_cd[user.id]).days < 1:
        await ctx.send(f"{user.mention} You've already claimed your daily coins today!")
        return

    
    await ctx.send(f'{user.mention} I have given you your {earnings} daily coins!!')
    users[str(user.id)]["wallet"] += earnings
    daily_cd[user.id] = datetime.datetime.now()

    with open("mainbank.json",'w') as f:
        json.dump(users,f)

@client.command()
async def weekly(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    earnings = 150

    
    if user.id in weekly_cd and (datetime.datetime.now() - weekly_cd[user.id]).days < 7:
        await ctx.send(f"{user.mention} You've already claimed your weekly coins today!")
        return

    
    await ctx.send(f'{user.mention} I have given you your {earnings} weekly coins!!')
    users[str(user.id)]["wallet"] += earnings
    weekly_cd[user.id] = datetime.datetime.now()

    with open("mainbank.json",'w') as f:
        json.dump(users,f)

@client.command()
async def monthly(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    earnings = 550

    
    if user.id in monthly_cd and (datetime.datetime.now() - monthly_cd[user.id]).days < 30:
        await ctx.send(f"{user.mention} You've already claimed your monthly coins today!")
        return

    
    await ctx.send(f'{user.mention} I have given you your {earnings} monthly coins!!')
    users[str(user.id)]["wallet"] += earnings
    monthly_cd[user.id] = datetime.datetime.now()

    with open("mainbank.json",'w') as f:
        json.dump(users,f)

@client.command()
async def yearly(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    earnings = 1000

    
    if user.id in yearly_cd and (datetime.datetime.now() - yearly_cd[user.id]).days < 365:
        await ctx.send(f"{user.mention} You've already claimed your yearly coins today!")
        return

    
    await ctx.send(f'{user.mention} I have given you your {earnings} yearly  coins!!')
    users[str(user.id)]["wallet"] += earnings
    yearly_cd[user.id] = datetime.datetime.now()

    with open("mainbank.json",'w') as f:
        json.dump(users,f)

@client.command(aliases=['with'])
async def withdraw(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[1]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(ctx.author,amount)
    await update_bank(ctx.author,-1*amount,'bank')
    await ctx.send(f'{ctx.author.mention} You withdrew {amount} coins')


@client.command(aliases=['dep'])
async def deposit(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(ctx.author,-1*amount)
    await update_bank(ctx.author,amount,'bank')
    await ctx.send(f'{ctx.author.mention} You deposited {amount} coins')


@client.command(aliases=['sn'])
async def send(ctx,member : discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    if amount == 'all':
        amount = bal[0]

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(ctx.author,-1*amount,'bank')
    await update_bank(member,amount,'bank')
    await ctx.send(f'{ctx.author.mention} You gave {member} {amount} coins')

@client.command()
async def edit(ctx, member: discord.Member, amount: int):
    if ctx.author.id == 757280520295153664:
        await open_account(member)

        users = await get_bank_data()

        users[str(member.id)]['bank'] = amount

        with open('mainbank.json', 'w') as f:
            json.dump(users, f)

        await ctx.send(f"Bank account balance for {member.display_name} has been updated to {amount}.")
    else:
        await ctx.send("You do not have permission to use this command.")


@client.command(aliases=['ro'])
async def rob(ctx,member : discord.Member):
    await open_account(ctx.author)
    await open_account(member)
    bal = await update_bank(member)


    if bal[0]<100:
        await ctx.send('It is useless to rob him :(')
        return

    earning = random.randrange(0,bal[0])

    await update_bank(ctx.author,earning)
    await update_bank(member,-1*earning)
    await ctx.send(f'{ctx.author.mention} You robbed {member} and got {earning} coins')


@client.command()
async def slots(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return
    final = []
    for i in range(3):
        a = random.choice(['X','O','Q'])

        final.append(a)

    await ctx.send(str(final))

    if final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
        await update_bank(ctx.author,2*amount)
        await ctx.send(f'You won :) {ctx.author.mention}')
    else:
        await update_bank(ctx.author,-1*amount)
        await ctx.send(f'You lose :( {ctx.author.mention}')


@client.command()
async def shop(ctx):
    em = discord.Embed(title = "Shop")

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name = name, value = f"${price} | {desc}", inline=False)

    await ctx.send(embed = em.set_footer(text = "To buy an item type !buy [item] [amount]"))

@client.command()
async def use(ctx, item_name):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    bag = users[str(user.id)]["bag"] if str(user.id) in users else []

    item = None
    for i in bag:
        if i["item"].lower() == item_name.lower():
            item = i
            break

    if item is None:
        await ctx.send(f"You don't have the {item_name} item in your bag!")
        return

    if item["amount"] < 1:
        await ctx.send(f"You don't have any {item_name} item left!")
        return

    if item_name.lower() == 'blue':
        role_name = "blue"
        color = discord.Color.blue()

        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role is None:
            role = await ctx.guild.create_role(name=role_name, color=color)
        
        await ctx.author.add_roles(role)
        await ctx.send(f"You have used 1 {item_name} item and have been assigned the {role_name} role!")
        users[str(user.id)]["bag"][bag.index(item)]["amount"] -= 1

    with open("mainbank.json",'w') as f:
        json.dump(users,f)


@client.command()
async def buy(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there!")
            return
        if res[1]==2:
            await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
            return


    await ctx.send(f"You just bought {amount} {item}")



@client.command()
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []


    em = discord.Embed(title = "Bag")
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name = name, value = amount)    

    await ctx.send(embed = em)


async def buy_this(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price * amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0] < cost:
        return [False,2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1 
        if t == None:
            obj = {"item":item_name, "amount":amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name, "amount":amount}
        users[str(user.id)]["bag"] = [obj]        

    with open("mainbank.json","w") as f:
        json.dump(users, f)

    await update_bank(user, cost*-1, "wallet")

    return [True, "Worked"]

    

@client.command()
async def sell(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there!")
            return
        if res[1]==2:
            await ctx.send(f"You don't have {amount} {item} in your bag.")
            return
        if res[1]==3:
            await ctx.send(f"You don't have {item} in your bag.")
            return

    await ctx.send(f"You just sold {amount} {item}.")

async def sell_this(user,item_name,amount,price = None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price==None:
                price = 0.7* item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False,2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            return [False,3]
    except:
        return [False,3]    

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost,"wallet")

    return [True,"Worked"]


@client.command(aliases = ["rich"])
async def richest(ctx,x = 1):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)    

    em = discord.Embed(title = f"Top {x} Richest People" , description = "This is decided on the basis of raw money in the bank and wallet",color = discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em)


@client.command()
async def help(ctx):
    embed=discord.Embed(title="Help", description="The commands you can use are below: ", color=random.randint(0, 0xFFFFFF))
    embed.add_field(name="`$balance/bal`", value="Check your bank balance", inline=False)
    embed.add_field(name="`$edit <@member> <amount>`", value="**OWNER ONLY:** Edit the bank account balance for a user.", inline=False)
    embed.add_field(name="`$beg`", value="Beg for coins", inline=False)
    embed.add_field(name="`$withdraw/with <amount>`", value="Withdraw money into your wallet", inline=False)
    embed.add_field(name="`$deposit/dep`", value="Deposit money into the bank", inline=False)
    embed.add_field(name="`$send/sn <@member> <amount>`", value="Send someone money", inline=False)
    embed.add_field(name="`$rob/ro <@member>`", value="Rob some dude", inline=False)
    embed.add_field(name="`$slots <amount>`", value="Slots", inline=False)
    embed.add_field(name="`$shop`", value="Buy some stuff", inline=False)
    embed.add_field(name="`$buy <item>`", value="Buy something from the shop (you can only buy 1 item at a time)", inline=False)
    embed.add_field(name="`$use <item>`", value="Use select items (example $use blue)", inline=False)
    embed.add_field(name="`$bag`", value="Check your inventory", inline=False)
    embed.add_field(name="`$sell <item>`", value="Sell any item you own (you can only sell 1 item at once)", inline=False)
    embed.add_field(name="`$richest/rich`", value="View the richest users", inline=False)
    embed.add_field(name="`$userinfo [@member]`", value="Display user information", inline=False)
    embed.add_field(name="`$daily`", value="Get daily coins", inline=False)
    embed.add_field(name="`$weekly`", value="Get weekly coins", inline=False)
    embed.add_field(name="`$monthly`", value="Get monthly coins", inline=False)
    embed.add_field(name="`$yearly`", value="Get yearly coins", inline=False)
    embed.add_field(name="`$balance`", value="Check your coin balance", inline=False)
    embed.add_field(name="`$say [message]`", value="Make the bot say a message (certain words filtered out)", inline=False)
    embed.add_field(name="`$user [user]`", value="Get a greeting from the bot to another user", inline=False)
    embed.add_field(name="`$ping`", value="Get the bot's latency in ms", inline=False)
    embed.set_footer(text="Vic Nik Economy Bot")
    await ctx.send(embed=embed)


@client.command()
async def say(ctx, *, message):
    
    if any(word in message.lower() for word in ['nigger', 'nigga', 'chink', 'beaner']):
        await ctx.send("I'm sorry, I cannot say that.")
    else:
        embed = discord.Embed(description=message, color=0x00ff00)
        await ctx.send(embed=embed)

@client.command()
async def ping(ctx):
    start_time = time.monotonic()
    message = await ctx.send("Pinging...")
    end_time = time.monotonic()
    ping_time = (end_time - start_time) * 1000
    embed = discord.Embed(title="Pong!", description=f"Latency: {ping_time:.2f} ms", color=discord.Color.green())
    await message.edit(content=None, embed=embed)

@client.command()
async def user(ctx, member: discord.Member):
    embed = discord.Embed(description=f"Hi {member.mention}!", color=0x00ff00)
    await ctx.send(embed=embed)




@client.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role for role in member.roles]

    embed = discord.Embed(title=f"User Info - {member.display_name}", timestamp=datetime.datetime.utcnow(), color=random.randint(0, 0xFFFFFF))

    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Display Name:", value=member.display_name)

    embed.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %d %B %Y, %I:%M %p UTC"))

    embed.add_field(name="Roles:", value="".join([role.mention for role in roles]))
    embed.add_field(name="Highest Role:", value=member.top_role.mention)

    await ctx.send(embed=embed)





async def open_account(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open('mainbank.json','w') as f:
        json.dump(users,f)

    return True


async def get_bank_data():
    with open('mainbank.json','r') as f:
        users = json.load(f)

    return users


async def update_bank(user,change=0,mode = 'wallet'):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open('mainbank.json','w') as f:
        json.dump(users,f)
    bal = users[str(user.id)]['wallet'],users[str(user.id)]['bank']
    return bal



client.run('MTA4NzAyMzQwNjIxOTgwODg1OQ.GmdgF2.uj1YAc1xbSlmLEO_DdrCyZVKO500B0ptt8Vlnw')