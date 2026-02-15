import discord
import os
import requests
import re
from discord.ext import commands
from dotenv import load_dotenv
from deobfuscator_core import Deobfuscator
from pattern_scanner import PatternScanner

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_content_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None

@bot.command()
async def deobf(ctx, link: str = None):
    content = ""
    file_name = "analiz_edilen_kod.lua"

    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        file_name = attachment.filename
        await attachment.save(file_name)
        with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    
    elif link and (link.startswith("http://") or link.startswith("https://")):
        await ctx.send("Link okunuyor...")
        content = get_content_from_url(link)
        if not content:
            await ctx.send("Linkten veri cekilemedi!")
            return
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
    
    else:
        await ctx.send("Lutfen bir dosya yukleyin veya bir link yapistirin.")
        return

    try:
        engine = Deobfuscator()
        results = engine.analyze_script(file_name)
        
        scanner = PatternScanner()
        patterns = scanner.analyze_target_file(file_name)

        embed = discord.Embed(title="Syniox Analiz Raporu", color=0x00ff00)
        embed.add_field(name="Kaynak", value="Dosya" if ctx.message.attachments else "Link", inline=True)
        embed.add_field(name="Risk", value=patterns.get('risk_assessment', 'N/A'), inline=True)
        embed.add_field(name="Bulunan String", value=str(len(results.get('decrypted_strings', []))), inline=True)
        
        await ctx.send(embed=embed)

        if results.get('decrypted_strings'):
            output_name = "cozulmus_cikti.txt"
            with open(output_name, "w", encoding="utf-8") as f:
                for s in results['decrypted_strings']:
                    f.write(s + "\n")
            await ctx.send(file=discord.File(output_name))
            os.remove(output_name)
            
    except Exception as e:
        await ctx.send(f"Hata: {str(e)}")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

bot.run(TOKEN)
