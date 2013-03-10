"""
Make sure that disabling a disabled module fails
"""

import seash

# We need to do module manipulation
import seash_dictionary
import seash_modules
#pragma out Enabled modules: modules
#pragma out To see a list of all available modules, use the 'show modules' command.
seash_modules.enable_modules_from_last_session(seash_dictionary.seashcommanddict)

#pragma error Module is not enabled
commands = [
  "disable geoip"
]
seash.command_loop(commands)