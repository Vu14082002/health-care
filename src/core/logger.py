from typing import Optional, Literal
from copy import copy
import logging
import click
import sys

TRACE_LOG_LEVEL = 5


class ColourizedFormatter(logging.Formatter):

    level_name_colors = {
        TRACE_LOG_LEVEL: lambda level_name: click.style(str(level_name), fg="blue"),
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(
            str(level_name), fg="bright_red"
        ),
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: Optional[bool] = None,
    ):
        # Set the use_colors flag to True if colors are enabled.
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        """
         Color a level name according to the color scheme. This is a function so we can use it in place of : func : ` color_level `
         
         @param level_name - The level name to color
         @param level_no - The level number to color the level name
         
         @return The colorized level name or the level name if no color is defined for the level_no -
        """
        def default(level_name: str) -> str:
            """
             Returns the default value for a level. This is used to determine the default value for an error or warning level.
             
             @param level_name - The name of the level. It can be anything that can be converted to a string e. g.
             
             @return The default value for the level. If you don't want to change this use : func : ` level_name `
            """
            return str(level_name)

        func = self.level_name_colors.get(level_no, default)
        return func(level_name)

    def should_use_colors(self) -> bool:
        """
         Whether or not to use colors. This is a hack to avoid having to re - define colors in a test method that doesn't work with Python 2.
         
         
         @return True if colors should be used
        """
        return True

    def formatMessage(self, record: logging.LogRecord) -> str:
        """
         Format a log record for display. This is overridden to add color information to the message and levelprefix attributes
         
         @param record - The log record to format
         
         @return The formatted log record as a string or None if there was no formatting to do for the log record
        """
        recordcopy = copy(record)
        levelname = recordcopy.levelname
        process = recordcopy.process
        seperator = " " * (8 - len(recordcopy.levelname))
        # Set recordcopy. msg to color_level_name levelname recordcopy. levelno
        if self.use_colors:
            levelname = self.color_level_name(levelname, recordcopy.levelno)
            # This function is used to set the message of the recordcopy.
            if "color_message" in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__["color_message"]
                recordcopy.__dict__["message"] = recordcopy.getMessage()
        recordcopy.__dict__["levelprefix"] = levelname + ":" + seperator
        recordcopy.__dict__["process"] = click.style(str(process), fg="blue")
        return super().formatMessage(recordcopy)


class DefaultFormatter(ColourizedFormatter):
    def should_use_colors(self) -> bool:
        """
         Whether or not we should use colors. This is based on the value of sys. stderr. isatty ().
         
         
         @return True if color is used False otherwise. Defaults to : data : ` True ` if stderr is a terminal
        """
        return sys.stderr.isatty()


logger = logging.getLogger("__main__")
logger.setLevel(logging.DEBUG)
formatter = DefaultFormatter(
    fmt="%(levelprefix)s %(asctime)s [%(process)s] [%(filename)s:%(lineno)d] %(message)s",
    use_colors=True,
    datefmt="%d-%m-%Y %H:%M:%S",
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
