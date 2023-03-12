import requests, json
import discord
from bs4 import BeautifulSoup
from discord.ext import commands
import emoji
import DiscordUtils

client = commands.Bot(command_prefix='~', case_insensitive=True)

@client.event
async def on_ready():
    print ("Bot is ready")

@client.command()
async def weather(ctx, city="", country = "", extra = ""):
    if city != "":
        url = f"http://api.weatherapi.com/v1/forecast.json?key=4dcd8c3ec3634e85b7c190411211204&q={city} {country}&days=7&aqi=no&alerts=yes"
        response = requests.get(url)
        data = response.json()        
        #location data
        location = data['location']
        cityname = location['name']
        region = str(location['region'])
        country = location['country']
        lat = str(location['lat'])
        lon = str(location['lon'])
        localtime = location['localtime']
        if region != "":
            geoname = f"{cityname}, {region}, {country}"
        elif region == "":
            geoname = f"{cityname}, {country}"
        ns = "N"
        ew = "E"
        if "-" in lat:
            lat = lat.replace("-", "")
            ns = "S"
        if "-" in lon:
            lon = lon.replace("-", "")
            ew = "W"
        
        #time of day icon
        currenttime = localtime.split(" ")[1]
        astro = data['forecast']['forecastday'][0]['astro']
        sunrise = astro['sunrise']
        sunset = astro['sunset']
        times = [currenttime, sunrise, sunset]
        list1 = []
        for x in times:
            if "AM" in x:
                x = x.split(" ")[0]
                x = x.split(":")
                x = list(map(int, x))
                if x[0] == 12:
                    x[0] = 0
            elif "PM" in x:
                x = x.split(" ")[0]
                x = x.split(":")
                x = list(map(int, x))
                if x[0] == 12:
                    x[0] = 0
                x[0] += 12
            else:
                x = x.split(":")
            list1.append(str(x[0]))
            list1.append(str(x[1]))
        list1 = list(map(int, list1))
        for i in range(1, len(list1), 2):
            if i % 2 == 1:
                list1[i - 1] *= 60
        plist = [list1[y] + list1[y+1] for y in range(0, len(list1)-1, 2)]
        if len(list1) % 2 == 1:
            plist.append(list1[len(list1)-1])
        plist.append(plist[1] + 30)
        plist.append(plist[2] - 30)
        if plist[0] >= plist[1] and plist[0] <= plist[3]:
            emoji = ":city_sunrise:"
        if plist[0] > plist[3]  and plist[0] < plist [4]:
            emoji = ":cityscape:"
        if plist[0] >= plist[4] and plist[0] <= plist[2]:
            emoji = ":city_dusk:"
        if plist[0] > plist[2] or plist[0] < plist[1]:
            emoji = ":night_with_stars:"
        
        #hourly weather
        time = localtime.split(" ")[1]
        time = int(time.split(":")[0])
        x = 0 
        y = 0
        z = 0
        list1 = []
        while x < 35:    
            hour = data['forecast']['forecastday'][y]['hour'][z]
            temph = f"{hour['temp_c']}°C"
            timeh = str(hour['time'])
            condh = str(hour['condition']['text']).title()
            windh = f"{hour['wind_kph']} km/h"
            gusth = f"{hour['gust_kph']} km/h"
            prainh = f"{hour['chance_of_rain']} %"
            psnowh = f"{hour['chance_of_snow']} %"
            preciph = f"{hour['precip_mm']} mm"
            feelsh = float(hour['feelslike_c'])
            if feelsh <= 5:
                hemoji = ":cold_face:"
            elif feelsh < 15 and feelsh > 5:
                hemoji = ":grimacing:"
            elif feelsh >= 15 and feelsh < 25:
                hemoji = ":slight_smile:"
            elif feelsh >= 25 and feelsh < 30:
                hemoji = ":sweat:"
            else:
                hemoji = ":hot_face:"
            feelsh = f"{hemoji} Feels Like: **{feelsh}°C**"
            listh = [timeh, temph,feelsh, condh, windh, prainh, psnowh, preciph, gusth]
            list1.append(listh)
            x += 1
            z += 1
            if x == 24:
                y = 1
                z = 0
        list1 = list1[time:time+12]
        embeds = dict()
        for x in range(1, 13):
            embeds[x] = f":thermometer: **{list1[x-1][1]}** | **{list1[x-1][3]}** \n {list1[x-1][2]} \n :dash: Wind: **{list1[x-1][4]}** | Gust: **{list1[x-1][8]}** \n :umbrella: Chance of Rain: **{list1[x-1][5]}** | :snowflake: Chance of Snow: **{list1[x-1][6]}** | :droplet: Total Precip: **{list1[x-1][7]}** \n"
        
        #daily weather
        x = 0
        listday = []
        listtd = []
        dayembed = dict()
        while x < 3:
            ddate = data['forecast']['forecastday'][x]['date']
            day = data['forecast']['forecastday'][x]['day']
            dmax = f"{day['maxtemp_c']}°C"
            dmin = f"{day['mintemp_c']}°C"
            davg = f"{day['avgtemp_c']}°C"
            dcond = str(day['condition']['text']).title()
            dwind = f"{day['maxwind_kph']} km/h"
            dprecip = f"{day['totalprecip_mm']} mm"
            drchance = f"{day['daily_chance_of_rain']} %"
            dschance = f"{day['daily_chance_of_snow']} %"
            listday = [ddate, dmax, dmin, davg, dcond, dwind, dprecip, drchance, dschance]
            listtd.append(listday)
            dayembed[x] = f"**{listtd[x][4]}** \n :thermometer: Avg: **{listtd[x][3]}** | Max: **{listtd[x][1]}** | Min: **{listtd[x][2]}** \n :dash: Max Wind: **{listtd[x][5]}** \n :umbrella: Chance of Rain: **{listtd[x][7]}** | :snowflake: Chance of Snow: **{listtd[x][8]}** | :droplet: Total Precip: **{listtd[x][6]}** \n "
            x += 1
        embedd = discord.Embed(title = "Daily Forecast (3 Days)", color=discord.Colour.red()).add_field(name=f"{listtd[0][0]}", value=dayembed[0], inline = False).add_field(name=f"{listtd[1][0]}", value=dayembed[1], inline = False).add_field(name=f"{listtd[2][0]}", value=dayembed[2], inline = False).set_author(name="🌪️ WeatherBuddy")
        
        
        #current weather
        current = data['current']
        cl_updated = current['last_updated']
        cl_updated = cl_updated.split(" ")[1]
        ctempc = float(current['temp_c'])
        
        #feelmoji
        feelstempc = float(current['feelslike_c'])
        if feelstempc <= 5:
            feelmoji = ":cold_face:"
        elif feelstempc < 15 and feelstempc > 5:
            feelmoji = ":grimacing:"
        elif feelstempc >= 15 and feelstempc < 25:
            feelmoji = ":slight_smile:"
        elif feelstempc >= 25 and feelstempc < 30:
            feelmoji = ":sweat:"
        else:
            feelmoji = ":hot_face:"
        condition = str(current['condition']['text'])
        condition = condition.title()
        cond_icon = current['condition']['icon']
        cwind = current['wind_kph']
        cprecip = current['precip_mm']
        chumid = current['humidity']
        
        #main menu embed
        embed = discord.Embed(title = f"{geoname} ({lat}°{ns}, {lon}°{ew})", description = f"Current Date/Time: **{localtime} (Local)** {emoji}", color=discord.Colour.green()) 
        embed.set_author(name="🌪️ WeatherBuddy")
        embed.add_field(name=f"Current Weather (Updated @ {cl_updated}):", value=f":thermometer: **{ctempc}°C | {condition}** \n {feelmoji} Feels Like **{feelstempc}°C** \n :dash: Wind: **{cwind} km/h** | :umbrella: Precipitation: **{cprecip} mm** | :sweat_drops: Humidity: **{chumid}%**", inline=False)
        embed.set_thumbnail(url=f"https:{cond_icon}")
        msg = await ctx.send(embed = embed)
        await msg.add_reaction(u"\U0001F552")
        await msg.add_reaction(u"\U0001F5D3")
        
        #hourly embed
        embed1 = discord.Embed(title = "Hourly Forecast (1/4)", color=discord.Colour.blue()).add_field(name=f"{list1[0][0]}", value=embeds[1], inline = False).add_field(name=f"{list1[1][0]}", value=embeds[2], inline = False).add_field(name=f"{list1[2][0]}", value=embeds[3], inline = False).set_author(name="🌪️ WeatherBuddy")
        embed2 = discord.Embed(title = "Hourly Forecast (2/4)",color=discord.Colour.blue()).add_field(name=f"{list1[3][0]}", value=embeds[4], inline = False).add_field(name=f"{list1[4][0]}", value=embeds[5], inline = False).add_field(name=f"{list1[5][0]}", value=embeds[6], inline = False).set_author(name="🌪️ WeatherBuddy")
        embed3 = discord.Embed(title = "Hourly Forecast (3/4)",color=discord.Colour.blue()).add_field(name=f"{list1[6][0]}", value=embeds[7], inline = False).add_field(name=f"{list1[7][0]}", value=embeds[8], inline = False).add_field(name=f"{list1[8][0]}", value=embeds[9], inline = False).set_author(name="🌪️ WeatherBuddy")
        embed4 = discord.Embed(title = "Hourly Forecast (4/4)",color=discord.Colour.blue()).add_field(name=f"{list1[9][0]}", value=embeds[10], inline = False).add_field(name=f"{list1[10][0]}", value=embeds[11], inline = False).add_field(name=f"{list1[11][0]}", value=embeds[12], inline = False).set_author(name="🌪️ WeatherBuddy")
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx,timeout = 10, remove_reactions=True)
        paginator.add_reaction('◀', "back")
        paginator.add_reaction('▶', "next")
        embeds = [embed1, embed2, embed3, embed4]

        #reaction ui          
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [u"\U0001F552", u"\U0001F5D3"]
        member = ctx.author
        bot = client.user
        while True:
            reaction, user = await client.wait_for("reaction_add", timeout = 120, check=check)
            if reaction.message == msg:
                if str(reaction.emoji) == u"\U0001F552":
                    await reaction.remove(member)
                    await reaction.remove(bot)
                    await paginator.run(embeds)
                if str(reaction.emoji) == u"\U0001F5D3":
                    await reaction.remove(member)
                    await reaction.remove(bot)
                    await ctx.send(embed = embedd)    
        
client.run("ODMxMjU1NzExNDg4OTMzOTY4.YHSlNQ.9LhkoLLEVGjDNhmmDoeMcprAN_8")