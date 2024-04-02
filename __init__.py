import tomllib
from functools import wraps
from pathlib import Path
from typing import Literal, overload

import unrealsdk
from unrealsdk.unreal import UObject

from .dot_sdkmod import open_in_mod_dir

# Need to define a few things first to avoid circular imports
with open_in_mod_dir(Path(__file__).parent / "pyproject.toml", binary=True) as _pyproject:
    # We're being a bit unsafe here, but we know what we expect to see, and given we expect to be
    # in a .sdkmod it's quite unlikely that a regular user will unknowingly edit it
    _pyproject_data = tomllib.load(_pyproject)
    _version_str = _pyproject_data["project"]["version"]
    _major, _, _minor = _version_str.partition(".")

    __version_info__: tuple[int, int] = (int(_major), int(_minor))
    __version__: str = _pyproject_data["tool"]["sdkmod"].get("version", _version_str)
    del _major, _, _minor, _version_str, _pyproject_data, _pyproject

    # This doesn't need to be in the inner block, but exiting would cause E402 for following imports
    MODS_DIR: Path = (
        _mod_dir
        if (_mod_dir := Path(__file__).parent.parent).is_dir()
        else _mod_dir.parent  # If in a .sdkmod, need to go up an extra folder
    )
    del _mod_dir

from . import raw_keybinds
from .command import (
    AbstractCommand,
    ArgParseCommand,
    capture_next_console_line,
    command,
    remove_next_console_line_capture,
)
from .hook import HookProtocol, hook
from .html_to_plain_text import html_to_plain_text
from .keybinds import EInputEvent, KeybindType, keybind
from .mod import Game, Library, Mod, ModType
from .mod_factory import build_mod
from .mod_list import (
    deregister_mod,
    get_ordered_mod_list,
    register_mod,
)
from .options import (
    JSON,
    BaseOption,
    BoolOption,
    ButtonOption,
    DropdownOption,
    GroupedOption,
    HiddenOption,
    KeybindOption,
    NestedOption,
    SliderOption,
    SpinnerOption,
    ValueOption,
)
from .settings import SETTINGS_DIR

__all__: tuple[str, ...] = (
    "__version__",
    "__version_info__",
    "AbstractCommand",
    "ArgParseCommand",
    "BaseOption",
    "BoolOption",
    "build_mod",
    "ButtonOption",
    "capture_next_console_line",
    "command",
    "deregister_mod",
    "DropdownOption",
    "EInputEvent",
    "ENGINE",
    "Game",
    "get_ordered_mod_list",
    "get_pc",
    "GroupedOption",
    "HiddenOption",
    "hook",
    "HookProtocol",
    "html_to_plain_text",
    "JSON",
    "keybind",
    "KeybindOption",
    "KeybindType",
    "Library",
    "Mod",
    "MODS_DIR",
    "ModType",
    "NestedOption",
    "open_in_mod_dir",
    "raw_keybinds",
    "register_mod",
    "remove_next_console_line_capture",
    "SETTINGS_DIR",
    "SliderOption",
    "SpinnerOption",
    "ValueOption",
)

ENGINE: UObject


@overload
def get_pc() -> UObject: ...


@overload
def get_pc(*, possibly_loading: Literal[True] = True) -> UObject | None: ...


def get_pc(*, possibly_loading: bool = False) -> UObject | None:  # noqa: ARG001
    """
    Gets the main (local) player controller object.

    Note that this may return None if called during a loading screen. Since hooks and keybinds
    should never be able to trigger at this time, for convenience the default type hinting does not
    include this possibility. If running on another thread however, this can happen, pass the
    `possibly_loading` kwarg to update the type hinting.

    Args:
        possibly_loading: Changes the type hinting to possibly return None. No runtime impact.
    Returns:
        The player controller.
    """
    raise NotImplementedError


match Game.get_tree():
    case Game.Willow2:
        ENGINE = unrealsdk.find_object(  # pyright: ignore[reportConstantRedefinition]
            "WillowGameEngine",
            "Transient.WillowGameEngine_0",
        )

        _GAME_PLAYERS_PROP = ENGINE.Class._find_prop("GamePlayers")
        _ACTOR_PROP = _GAME_PLAYERS_PROP.Inner.PropertyClass._find_prop("Actor")

        @wraps(get_pc)
        def get_pc_willow(*, possibly_loading: bool = False) -> UObject | None:  # noqa: ARG001
            return ENGINE._get_field(_GAME_PLAYERS_PROP)[0]._get_field(_ACTOR_PROP)

        get_pc = get_pc_willow  # type: ignore

    case Game.Oak:
        ENGINE = unrealsdk.find_object(  # pyright: ignore[reportConstantRedefinition]
            "OakGameEngine",
            "/Engine/Transient.OakGameEngine_0",
        )

        _GAME_INSTANCE_PROP = ENGINE.Class._find_prop("GameInstance")
        _LOCAL_PLAYERS_PROP = _GAME_INSTANCE_PROP.PropertyClass._find_prop("LocalPlayers")
        _PLAYER_CONTROLLER_PROP = _LOCAL_PLAYERS_PROP.Inner.PropertyClass._find_prop(
            "PlayerController",
        )

        @wraps(get_pc)
        def get_pc_oak(*, possibly_loading: bool = False) -> UObject | None:  # noqa: ARG001
            return (
                ENGINE._get_field(_GAME_INSTANCE_PROP)
                ._get_field(_LOCAL_PLAYERS_PROP)[0]
                ._get_field(_PLAYER_CONTROLLER_PROP)
            )

        get_pc = get_pc_oak  # type: ignore
