from mesonet_utils import Config

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    pass


CONFIG = Config.load(Config.file)
