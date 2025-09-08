from discord.ext import commands
from datetime import datetime
from scraper.ENMscraper import enmScrap
from scraper.DRUZBAscraper import druzbaScrap
from scraper.FIITFOODscraper import fiitfoodScrap
from utils.config import load_config
from discord.ext.commands import Bot
from utils.emoji_map import title_emoji_mapper
from scraper.exceptions import MenuNotFoundError, MenuBodyNotFoundError
import discord

async def daily_menu(bot: Bot):
    config = load_config()
    for guild in bot.guilds:
        guild_id = str(guild.id)
        guild_config = config.get(guild_id)
        if not guild_config:
            continue

        channel_id = guild_config.get("channel_id")
        if not channel_id:
            continue

        channel = bot.get_channel(channel_id)
        if channel:
            await send_daily_menu(config, channel, guild.id)

async def send_daily_menu(config, channel, guild_id):
    try:
        # Premazanie správ pred poslaním novej spŕavy
        await channel.purge(limit=10)
        meal_names, main_prices, secondary_prices, allergens, meal_categories = enmScrap()
        
        embed_color = config.get(str(guild_id), {}).get("embed_color", 0xffe28a)

        embed_list = []

        # Správy o jednotlivých jedlách
        for i in range(len(meal_names)):
            emoji = title_emoji_mapper(meal_categories[i])
            category = f"{meal_categories[i]:<130}"
            name = f"{meal_names[i]}"

            embed = discord.Embed(
                title=f"{emoji} {category}\n{name}",
                #title=f"{emoji} {meal_categories[i]} \n{meal_names[i]}", 
                description=f"Cena: *{main_prices[i]}*  **{secondary_prices[i]}**",
                color=embed_color
            )
            embed.set_footer(text=f"{allergens[i]}")
            embed_list.append(embed)

        # Ping JSON role predtým ako sa pošle menu
        role_id = config[str(guild_id)].get("role_id")
        if role_id:
            role = channel.guild.get_role(int(role_id))
            if role:
                await channel.send(f"{role.mention}")
            else:
                await channel.send("Rola neexistuje na serveri.")
        else:
            await channel.send("Role ID nie je nastavené.")

        # Discord má limit 10 embedov v embede, ak ich je viac, treba poslať po dávkach po 10
        # Poslanie všetkých správ
        await channel.send(embeds=embed_list)
        
    except MenuNotFoundError as e:
        await channel.send("Nepodarilo sa nájsť dnešné menu.")
    except MenuBodyNotFoundError as e:
        await channel.send("Našlo sa menu, nepodarilo sa nájst položky z menu.")
    except Exception as e:
        await channel.send(f"Neočakávaná chyba: {type(e).__name__}: {e}")

async def send_druzba_menu(config, channel, guild_id):
    try:
        #await channel.purge(limit=6)
        meal_categories, meal_names, allergens, main_prices, secondary_prices = druzbaScrap()
        
        embed_color = config.get(str(guild_id), {}).get("embed_color", 0xffe28a)

        embed_list = []

        # Správy o jednotlivých jedlách
        for i in range(len(meal_names)):
            name = f"{meal_names[i]}"
            f_secondary_price = f"/ *{secondary_prices[i]}*"

            embed = discord.Embed(
                title=f"{meal_categories[i]} {name}",
                description=f"Cena: **{main_prices[i]}** {f_secondary_price}",
                color=embed_color
            )
            embed.set_footer(text=f"{allergens[i]}")
            embed_list.append(embed)

        # Ping JSON role predtým ako sa pošle menu
        role_id = config[str(guild_id)].get("role_id")
        if role_id:
            role = channel.guild.get_role(int(role_id))
            if role:
                await channel.send(f"{role.mention}")
            else:
                await channel.send("Rola neexistuje na serveri.")
        else:
            await channel.send("Role ID nie je nastavené.")

        # # Discord má limit 10 embedov v embede, ak ich je viac, treba poslať po dávkach po 10
        # Poslanie všetkých správ
        await channel.send(embeds=embed_list)
        
    except MenuNotFoundError as e:
        await channel.send("Nepodarilo sa nájsť dnešné menu.")
    except MenuBodyNotFoundError as e:
        await channel.send("Našlo sa menu, nepodarilo sa nájst položky z menu.")
    except Exception as e:
        await channel.send(f"Neočakávaná chyba: {type(e).__name__}: {e}")

async def send_fiitfood_menu(config, channel, guild_id):
    try:
        meal_categories, meal_names, main_prices, allergens = fiitfoodScrap()

        embed_color = config.get(str(guild_id), {}).get("embed_color", 0xffe28a)

        embed_list = []

        # Správy o jednotlivých jedlách
        for i in range(len(meal_names)):
            name = f"{meal_names[i]}"

            embed = discord.Embed(
                title=f"{meal_categories[i]} {name}",
                description=f"Cena: **{main_prices[i]}**",
                color=embed_color
            )
            embed.set_footer(text=f"{allergens[i]}")
            embed_list.append(embed)

        # Ping JSON role predtým ako sa pošle menu
        role_id = config[str(guild_id)].get("role_id")
        if role_id:
            role = channel.guild.get_role(int(role_id))
            if role:
                await channel.send(f"{role.mention}")
            else:
                await channel.send("Rola neexistuje na serveri.")
        else:
            await channel.send("Role ID nie je nastavené.")

        # # Discord má limit 10 embedov v embede, ak ich je viac, treba poslať po dávkach po 10
        # Poslanie všetkých správ
        await channel.send(embeds=embed_list)
        
    except MenuNotFoundError as e:
        await channel.send("Nepodarilo sa nájsť dnešné menu.")
    except MenuBodyNotFoundError as e:
        await channel.send("Našlo sa menu, nepodarilo sa nájst položky z menu.")
    except Exception as e:
        await channel.send(f"Neočakávaná chyba: {type(e).__name__}: {e}")
    
    #await channel.purge(limit=2)
    #await channel.send([meal_categories, meal_names, main_prices, allergens])

def use_commands(bot):
    # Ping príkaz
    @bot.command()
    async def ping(ctx):
        guild_id = str(ctx.guild.id)
        config = load_config()

        # Skontroluj, či pre daný server existujú údaje
        if guild_id not in config or "role_id" not in config[guild_id]:
            #await ctx.send("Rola s týmto ID neexistuje na serveri.")
            return
        
        expected_channel_id = config[guild_id]["channel_id"]

        if ctx.channel.id != expected_channel_id:
            #await ctx.send("Tento príkaz je možné použiť iba v kanáli určenom pre denné menu.")
            return

        role_id = config[guild_id]["role_id"]
        role = ctx.guild.get_role(int(role_id))

        if role:
            await ctx.send(f'{role.mention} bu!')
        else:
            await ctx.send("Rola s týmto ID neexistuje na serveri.")

    @bot.command()
    async def info(ctx):
        info_embed = discord.Embed(
        title="ℹ️ Info",
        description=(
            "[🌐 Stránka Eat&Meet](https://eatandmeet.sk/)"
        ),
        color=0x57F287
        )
        await ctx.send(embed=info_embed)

    # Príkaz na testovanie posielania obrázku
    @bot.command()
    async def testimage(ctx):
        url = "https://htmlcolorcodes.com/assets/images/colors/baby-blue-color-solid-background-1920x1080.png"
        embed = discord.Embed(title="Test obrázok :)))")
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    # Príkaz na manuálne posielanie denného menu
    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def eat(ctx):
        config = load_config()
        guild_id = str(ctx.guild.id)

        if guild_id not in config or "channel_id" not in config[guild_id]:
            #await ctx.send("Pre tento server nie je nastavený kanál pre denné menu.")
            return
        
        expected_channel_id = config[guild_id]["channel_id"]

        if ctx.channel.id != expected_channel_id:
            #await ctx.send("Tento príkaz je možné použiť iba v kanáli určenom pre denné menu.")
            return

        await send_daily_menu(config, ctx.channel, ctx.guild.id)

    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def druzba(ctx):
        config = load_config()
        guild_id = str(ctx.guild.id)

        if guild_id not in config or "channel_id" not in config[guild_id]:
            #await ctx.send("Pre tento server nie je nastavený kanál pre denné menu.")
            return
        
        expected_channel_id = config[guild_id]["channel_id"]

        if ctx.channel.id != expected_channel_id:
            #await ctx.send("Tento príkaz je možné použiť iba v kanáli určenom pre denné menu.")
            return

        await send_druzba_menu(config, ctx.channel, ctx.guild.id)

    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def ff(ctx):
        config = load_config()
        guild_id = str(ctx.guild.id)

        if guild_id not in config or "channel_id" not in config[guild_id]:
            return
        
        expected_channel_id = config[guild_id]["channel_id"]

        if ctx.channel.id != expected_channel_id:
            return

        await send_fiitfood_menu(config, ctx.channel, ctx.guild.id)

    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def mnam(ctx):
        config = load_config()
        guild_id = str(ctx.guild.id)

        if guild_id not in config or "channel_id" not in config[guild_id]:
            #await ctx.send("Pre tento server nie je nastavený kanál pre denné menu.")
            return
        
        expected_channel_id = config[guild_id]["channel_id"]

        if ctx.channel.id != expected_channel_id:
            #await ctx.send("Tento príkaz je možné použiť iba v kanáli určenom pre denné menu.")
            return
        
        await send_daily_menu(config, ctx.channel, ctx.guild.id)
        await send_druzba_menu(config, ctx.channel, ctx.guild.id)
        await send_fiitfood_menu(config, ctx.channel, ctx.guild.id)