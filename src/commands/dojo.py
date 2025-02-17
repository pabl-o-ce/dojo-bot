"""
This module contains the Dojo command for bot.
"""

import asyncio
import os
import time
import io
import uuid

from typing import List
from dotenv import load_dotenv
from interactions import slash_command, SlashCommandChoice, slash_option, \
    SlashContext, max_concurrency, Buckets, Button, ActionRow, ButtonStyle, \
    Embed, EmbedAuthor, EmbedFooter, Extension, OptionType, listen, File
from interactions.ext.paginators import Paginator
from interactions.api.events import Component



load_dotenv()
DOJO_PATH = os.getenv('DOJO_PATH')
DOJO_MODELS = os.getenv('DOJO_MODELS')
DOJO_REDIS = os.getenv('DOJO_REDIS')
DOJO_GPU_LAYERS = os.getenv('DOJO_GPU_LAYERS')
DOJO_NTHREADS = os.getenv('DOJO_NTHREADS')
DOJO_SYSTEM_PROMPT = os.getenv('DOJO_SYSTEM_PROMPT')
DOJO_EMBED_URL = os.getenv('DOJO_EMBED_URL')
DOJO_EMBED_IMG = os.getenv('DOJO_EMBED_IMG')
DOJO_CMD_SCOPE = int(os.getenv('DOJO_CMD_SCOPE',str(1156064224225808488)))
DOJO_CMD_CHANNEL = int(os.getenv('DOJO_CMD_CHANNEL',str(1189670522653511740)))
DOJO_MAX_REQ = int(os.getenv('DOJO_MAX_REQ', str(1)))

class CommandsDojo(Extension):
    """
    This class contains the CommandsDojo.
    """

    def __init__(self, bot) -> None:
        self.bot = bot

    # def drop(self):
    #     super().drop()

    @max_concurrency(bucket=Buckets.CHANNEL, concurrent=DOJO_MAX_REQ)
    @slash_command(
        name="Dojo",
        description="Dojo: Large Language Model Text Generation Inference Bot.",
        dm_permission=False,
        scopes=[DOJO_CMD_SCOPE]
    )
    @slash_option(
        name="prompt",
        description="Ask anything",
        opt_type=OptionType.STRING,
        required=True,
        min_length=1,
        max_length=2048
    )
    @slash_option(
        name="model",
        description="Select your Dojo model. Default",
        required=False,
        opt_type=OptionType.INTEGER,
        choices=[
            SlashCommandChoice(name="Dojo 2.9 llama 8B", value=0),
            SlashCommandChoice(name="Dojo 2.8 mistral 7B v02", value=1),
            SlashCommandChoice(name="Dojo 2.8 experiment26 7B", value=2),
            SlashCommandChoice(name="Dojo 2.6 mistral 7B DPO", value=3),
            SlashCommandChoice(name="laserxtral", value=4)
        ]
    )
    @slash_option(
        name="max_new_tokens",
        description="The maximum length of the sequence to be generated. Default: 2048",
        required=False,
        opt_type=OptionType.INTEGER,
        min_value=32,
        max_value=2048
    )
    @slash_option(
        name="temperature",
        description="The sampling temperature. Default: 0.1",
        required=False,
        opt_type=OptionType.NUMBER,
        min_value=0.05,
        max_value=2
    )
    @slash_option(
        name="repeat_penalty",
        description="The penalty for repetition. Default: 1.3",
        required=False,
        opt_type=OptionType.NUMBER,
        min_value=0.05,
        max_value=2
    )
    @slash_option(
        name="top_k",
        description="The number of highest probability vocabulary tokens to keep. Default: 50",
        required=False,
        opt_type=OptionType.INTEGER,
        min_value=0,
        max_value=100
    )
    @slash_option(
        name="top_p",
        description="The cumulative probability for top-p filtering. Default: 0.95",
        required=False,
        opt_type=OptionType.NUMBER,
        min_value=0.05,
        max_value=2
    )

    async def command(
        self,
        ctx: SlashContext,
        prompt: str,
        model: int = 0,
        max_new_tokens: int = 2048,
        temperature: float = 0.1,
        repeat_penalty: float = 1.3,
        top_k: int = 50,
        top_p: float = 0.95
    ) -> None:
        """
        This function executes the command.
        
        Args:
            ctx (SlashContext): The context of the command.
            prompt (str): The prompt for the model.
            model (int, optional): The model to use (default is 0).
            max_new_tokens (int, optional): The maximum number of tokens
            to generate (default is 2048).
            temperature (float, optional): The temperature parameter for
            text generation (default is 0.1).
            repeat_penalty (float, optional): The repeat penalty parameter (default is 1.3).
            top_k (int, optional): The top k parameter for text generation (default is 50).
            top_p (float, optional): The top p parameter for text generation (default is 0.95).
        """
        print("Command start")
        conversation_id = uuid.uuid4()
        try:
            print("Dojo start")
        except ImportError:
            print(f"Error occurred in command: {ImportError}")

        finally:
            print("Dojo end")
            print(ctx.resolved)

    @listen()
    async def an_event_handler(self, event: Component):
        """
        Listen an_event_handler function
        """
        print("An event handler");

    @command.error
    async def command_error(self, e, *args, **kwargs):
        """
        Command error function handle error event
        """
        print(f"Command hit error with {args=}, {kwargs=}")
        print(e)

    @command.pre_run
    async def command_pre_run(self, *args, **kwargs):
        """
        Command pre-run function event
        """
        print(f"I ran before the command did! {args=}, {kwargs=}")

    @command.post_run
    async def command_post_run(self, *args, **kwargs):
        """
        Command post-run function event
        """
        print(f"I ran after the command did! {args=}, {kwargs=}")



def setup(bot):
    """
    Setup def for CommandsDojo
    """
    CommandsDojo(bot)