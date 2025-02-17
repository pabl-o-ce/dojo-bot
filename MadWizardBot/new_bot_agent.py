import asyncio
from logging.handlers import RotatingFileHandler

import logging
import os

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions

from dotenv import load_dotenv

from ToolAgents.agents import ChatToolAgent
from ToolAgents.messages import ChatHistory
from ToolAgents.provider import OpenAIChatAPI
from ToolAgents.utilities import RecursiveCharacterTextSplitter

from system_prompts import system_prompts
load_dotenv()
handler = RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
TOKEN = os.getenv('DISCORD_TOKEN')
MY_GUILD = discord.Object(id=int(os.getenv('DISCORD_GUILD')))

class MyClient(discord.Client):
    def __init__(self, intents: discord.Intents, load_chat_history=False):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        # Openrouter API
        api = OpenAIChatAPI(api_key=os.getenv("OPENROUTER_API_KEY"), model="mistralai/mistral-small-24b-instruct-2501",
                            base_url="https://openrouter.ai/api/v1", debug_mode=True)
        # Create the ChatAPIAgent
        self.agent = ChatToolAgent(chat_api=api)
        self.chat_history = ChatHistory()
        self.sampling_settings = api.get_default_settings()
        self.sampling_settings.temperature = 0.45
        self.sampling_settings.top_p = 1.0
        self.sampling_settings.set_extra_body({"repetition_penalty": 1.1})
        self.is_generating_chat_result = False
        if load_chat_history:
            self.chat_history = ChatHistory.load_from_json("chat_history.json")
        else:
            self.chat_history.add_system_message(system_prompts['Vajrayogini'])

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        channel = message.channel

        if self.is_generating_chat_result:
            return False
        output_text = ""

        self.is_generating_chat_result = True
        cmp_str = f'Compute Result'
        msg = await channel.send(cmp_str)

        loop = asyncio.get_running_loop()
        output_text = await loop.run_in_executor(None, self.agent_response, message.author, message.content)

        # bot.save_messages("bot.json")
        splitter = RecursiveCharacterTextSplitter(
            separators=[
                "\n\n\n",  # Triple line breaks (section breaks)
                "\n\n",  # Double line breaks (paragraph breaks)
                "\n"
            ],
            chunk_size=1900,
            chunk_overlap=0,
            keep_separator=True
        )
        chunks = splitter.get_chunks(output_text)
        for chunk in chunks:
            await channel.send(chunk)

        await msg.delete()
        self.is_generating_chat_result = False

    def agent_response(self, author, content):
        self.chat_history.add_user_message(f"{author}: {content}")
        output = self.agent.get_response(messages=self.chat_history.get_messages(), settings=self.sampling_settings)
        self.chat_history.add_messages(output.messages)
        self.chat_history.save_to_json("chat_history.json")
        return output.response


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = MyClient(intents=intents, load_chat_history=False)


@client.tree.command(name='purge')
@has_permissions(administrator=True)
async def purge(ctx, limit: int):
    await ctx.channel.send("Successfully purged channel.")
    await ctx.channel.purge(limit=limit + 1)  # +1 to include the command message itself

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please specify a valid number of messages to delete.")

client.run(TOKEN, log_handler=handler)