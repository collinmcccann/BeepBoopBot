import discord
from discord.ext import commands
import urllib
from .utils.dataIO import dataIO
from urllib.request import urlopen
import requests
import aiohttp
import operator


class Fortnite:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot
        self.data = dataIO.load_json("data/fortnite/players.json")
        self.apikey = 'QS5PLx4gAdhecXk8lsNy'

    @commands.command()
    async def fnranks(self):
        """This command gives the leaderboard of all of the fortnite players on this server's stats"""
        rankings = {}
        for discordid in self.data:
            response = requests.get('https://fortnite.y3n.co/v2/player/' + self.data[discordid], headers={'X-Key': self.apikey})
            data = response.json()
            rating = self.getrating(data)

            for server in self.bot.servers:
                member = discord.utils.find(lambda m: m.id == discordid, server.members)
                if member:
                    rankings[member.name] = rating
                    break


        leaderboard = sorted(rankings.items(), key=operator.itemgetter(1))
        leaderboard.reverse()

        printstr = '```Wiff City United Fortnite Ratings\n\n'
        printstr += 'Rank'.ljust(7) + 'Name'.ljust(15) + 'Rating'.ljust(15) + '\n'
        printstr += '-----------------------------------\n'
        for index, tuple in enumerate(leaderboard):
            printstr += str(index + 1).ljust(7) + (str(tuple[0])).ljust(15) + str(tuple[1]).ljust(15) + '\n'

        printstr += '```'
        await self.bot.say(printstr)

    @commands.command()
    async def fnranksdetail(self):
        """This gives the rank leaderboard with more detail than regular fnranks"""
        rankings = {}
        winrates = {}
        kds = {}
        for discordid in self.data:
            response = requests.get('https://fortnite.y3n.co/v2/player/' + self.data[discordid], headers={'X-Key': self.apikey})
            data = response.json()
            rating = self.getrating(data)
            winrate = self.getwinrate(data)
            kd = self.getkd(data)

            for server in self.bot.servers:
                member = discord.utils.find(lambda m: m.id == discordid, server.members)
                if member:
                    rankings[member.name] = rating
                    winrates[member.name] = winrate
                    kds[member.name] = kd
                    break

        leaderboard = sorted(rankings.items(), key=operator.itemgetter(1))
        leaderboard.reverse()

        printstr = '```Wiff City United Detailed Fortnite Ratings\n\n'
        printstr += 'Rank'.ljust(7) + 'Name'.ljust(15) + 'Rating'.ljust(12) + 'Winrate'.ljust(12) +'K/D'.ljust(12) + '\n'
        printstr += '---------------------------------------------------\n'
        for index, tuple in enumerate(leaderboard):
            name = tuple[0]
            rating = tuple[1]
            wr = winrates[name]
            kd = kds[name]
            printstr += str(index + 1).ljust(7) + str(name).ljust(15) + str(rating).ljust(12) + str(wr).ljust(12) + str(kd).ljust(12) +'\n'

        printstr += '```'
        await self.bot.say(printstr)


    @commands.command(pass_context=True)
    async def linkfort(self, ctx, username):
        """Call this command with your username to link your discord account to your fortnite account in this server"""

        discordID = ctx.message.author.id
        try:
            data = requests.get('https://fortnite.y3n.co/v2/player/' + username, headers={'X-Key': self.apikey})
            if data.status_code != 200:
                raise Exception
        except:
            await self.bot.say('This account doesn\'t seem to exist. Did you spell your username right?')
            return

        self.data[discordID] = username
        dataIO.save_json("data/fortnite/players.json", self.data)
        await self.bot.say('Username ' + str(username) + ' successfully linked')


    def getrating(self, data):
        """This gives an adjusted rating of win rating * k/d normalized"""
        winrate = self.getwinrate(data)
        kd = self.getkd(data)
        wins = self.getwins(data)

        adjwinrate = (winrate / 100)
        adjkd = (kd / 10) / 3

        rating = (10000 * adjwinrate * adjkd) + wins

        return round(rating, 2)

    def getwinrate(self, data):
        return round(data['br']['stats']['pc']['all']['winRate'], 2)

    def getnumwins(self, data):
        return data['br']['stats']['pc']['all']['wins']


    def getkd(self, data):
        return round(data['br']['stats']['pc']['all']['kpd'], 2)


def setup(bot):
    bot.add_cog(Fortnite(bot))
