import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from deobfuscator_core import Deobfuscator
from pattern_scanner import PatternScanner
from execution_engine import ExecutionEngine

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Giris yapildi: {bot.user.name}')

@bot.command()
async def deobf(ctx):
    if not ctx.message.attachments:
        await ctx.send("Lutfen bir .lua dosyasi yukleyin.")
        return

    attachment = ctx.message.attachments[0]
    file_path = f"temp_{attachment.filename}"
    await attachment.save(file_path)

    try:
        deobf_engine = Deobfuscator()
        results = deobf_engine.analyze_script(file_path)
        
        scanner = PatternScanner()
        patterns = scanner.analyze_target_file(file_path)

        embed = discord.Embed(title="Analiz Raporu", color=0x00ff00)
        embed.add_field(name="Risk", value=patterns.get('risk_assessment', 'N/A'))
        embed.add_field(name="Stringler", value=str(len(results.get('decrypted_strings', []))))
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Hata: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

bot.run(TOKEN)
      
