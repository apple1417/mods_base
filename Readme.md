# Mods Base
A common set of classes for describing mods made with
[pyunrealsdk](https://github.com/bl-sdk/pyunrealsdk/), as well as various common utilities.

Aimed at the Borderlands series, though likely suitable for others with slight modification.

### Setting up a new Mod Manager
While this repo contains all the base info for a new mod manager, you still need to add a few other
game specific things:

- A mod menu. Consider using [console_mod_menu](https://github.com/bl-sdk/console_mod_menu/)
  while developing, though you likely want to create a gui version for users.

- A keybind implementation, which overwrites `KeybindType.enable` and `KeybindType.disable`, and
  sets up some hooks to run the callbacks as appropriate.

- An initialization script. This should import this and the keybind implementation, then find and
  import all mods, and finally call `mods_base.mod_list.register_base_mod `

# Changelog

### v1.5
- Added a default `rlm` command, which is a helper to reload Python modules during development.
- Deprecated the `auto_enable` arg in the `@hook` decorator, since it was misleading and in 99% of
  cases was not needed.
- Reworked `@hook` decorator internals to better support use on methods. It essentially creates a
  factory, which must be bound to the specific object before use. This is done automatically on mod
  instances.
- `KeybindOption.from_keybind()` now forwards the `default_key` -> `default_value`, so that
  resetting to default works consistently.
  
### Older
Versions 1.0 through 1.4 were developed as part of the
[oak-mod-manager](https://github.com/bl-sdk/oak-mod-manager/blob/master/changelog.md#v14), see it
for a full changelog.