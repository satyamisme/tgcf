"""Subpackage of tgcf: plugins.

Contains all the first-party tgcf plugins.
"""


import inspect
import logging
from enum import Enum
from importlib import import_module
from typing import Any, Dict

from telethon.tl.custom.message import Message

from tgcf.config import CONFIG
from tgcf.plugin_models import FileType, ASYNC_PLUGIN_IDS
from tgcf.utils import cleanup, stamp

PLUGINS = CONFIG.plugins


class TgcfMessage:
    """
    A wrapper around Telethon's Message object that carries data through the plugin chain.

    Plugins can modify attributes of this object (e.g., text, new_file)
    to change the message content before it's forwarded.

    Attributes:
        message (telethon.tl.custom.message.Message): The original Telethon message.
        text (str): The text of the message. Can be modified by plugins.
        raw_text (str): The raw text of the message (usually same as text).
        sender_id (int): The ID of the sender of the original message.
        file_type (FileType): The type of media file in the message, if any.
        new_file (Optional[str]): Path to a new file if a plugin generates/modifies a file.
                                  If set, this file will be sent instead of the original.
        cleanup (bool): If True and new_file is set, new_file will be deleted after sending.
        reply_to (Optional[int]): Message ID to reply to in the destination chat.
        client (telethon.TelegramClient): The Telethon client instance.
    """
    def __init__(self, message: Message) -> None:
        self.message = message
        self.text = self.message.text
        self.raw_text = self.message.raw_text
        self.sender_id = self.message.sender_id
        self.file_type = self.guess_file_type()
        self.new_file = None
        self.cleanup = False
        self.reply_to = None
        self.client = self.message.client

    async def get_file(self) -> str:
        """Downloads the file in the message and returns the path where its saved."""
        if self.file_type == FileType.NOFILE:
            raise FileNotFoundError("No file exists in this message.")
        self.file = stamp(await self.message.download_media(""), self.sender_id)
        return self.file

    def guess_file_type(self) -> FileType:
        for i in FileType:
            if i == FileType.NOFILE:
                return i
            obj = getattr(self.message, i.value)
            if obj:
                return i

    def clear(self) -> None:
        if self.new_file and self.cleanup:
            cleanup(self.new_file)
            self.new_file = None


class TgcfPlugin:
    """
    Base class for all tgcf plugins.

    Plugins are used to modify messages before they are forwarded.
    Each plugin must have a unique `id_`.

    Methods:
        __init__(data): Initializes the plugin with its specific configuration data.
        __ainit__(): Optional asynchronous initialization method for plugins
                     that need to perform async operations during setup.
        modify(tm): Processes/modifies the TgcfMessage object.
    """
    id_ = "plugin"

    def __init__(self, data: Dict[str, Any]) -> None:  # TODO data type has changed: This comment refers to the 'data' dict structure, which varies per plugin. Type hinting 'data' more specifically is complex here; individual plugins handle their own config model (e.g., FilterConfig).
        self.data = data

    async def __ainit__(self) -> None:
        """Optional asynchronous initialization method for plugins.

        This method is called once when tgcf starts if the plugin ID
        is listed in ASYNC_PLUGIN_IDS. It can be used for setup
        tasks that require asynchronous operations (e.g., API calls).
        """

    def modify(self, tm: TgcfMessage) -> TgcfMessage:
        """
        Processes or modifies a TgcfMessage object.

        This is the core method of a plugin. It can alter attributes of `tm`
        (e.g., `tm.text`, `tm.new_file`) to change the message content.

        Args:
            tm (TgcfMessage): The message object to process.

        Returns:
            TgcfMessage: The modified message object. If a plugin returns `None`,
                         the message will not be forwarded and processing for this
                         message stops.
        """
        return tm


def load_plugins() -> Dict[str, TgcfPlugin]:
    """Load the plugins specified in config."""
    _plugins = {}
    for item in PLUGINS:
        plugin_id = item[0]
        if item[1].check == False:
            continue

        plugin_class_name = f"Tgcf{plugin_id.title()}"

        try:  # try to load first party plugin
            plugin_module = import_module("tgcf.plugins." + plugin_id)
        except ModuleNotFoundError:
            logging.error(
                f"{plugin_id} is not a first party plugin. Third party plugins are not supported."
            )
        else:
            logging.info(f"First party plugin {plugin_id} loaded!")

        try:
            plugin_class = getattr(plugin_module, plugin_class_name)
            if not issubclass(plugin_class, TgcfPlugin):
                logging.error(
                    f"Plugin class {plugin_class_name} does not inherit TgcfPlugin"
                )
                continue
            plugin: TgcfPlugin = plugin_class(item[1])
            if not plugin.id_ == plugin_id:
                logging.error(f"Plugin id for {plugin_id} does not match expected id.")
                continue
        except AttributeError:
            logging.error(f"Found plugin {plugin_id}, but plugin class not found.")
        else:
            logging.info(f"Loaded plugin {plugin_id}")
            _plugins.update({plugin.id_: plugin})
    return _plugins


async def load_async_plugins() -> None:
    """Load async plugins specified plugin_models."""
    if plugins:
        for id in ASYNC_PLUGIN_IDS:
            if id in plugins:
                await plugins[id].__ainit__()
                logging.info(f"Plugin {id} asynchronously loaded")


async def apply_plugins(message: Message) -> TgcfMessage:
    """Apply all loaded plugins to a message."""
    tm = TgcfMessage(message)

    for _id, plugin in plugins.items():
        try:
            if inspect.iscoroutinefunction(plugin.modify):
                ntm = await plugin.modify(tm)
            else:
                ntm = plugin.modify(tm)
        except Exception as err:
            logging.error(f"Failed to apply plugin {_id}. \n {err} ")
        else:
            logging.info(f"Applied plugin {_id}")
            if not ntm:
                tm.clear()
                return None
    return tm


plugins = load_plugins()
