-- Keep only your personal keybinding overrides here. Add new bindings or
-- unbind defaults before replacing them.

-- See current bindings and descriptions:
--   omarchy menu keybindings --print

-- To disable every Omarchy default binding, set this in
-- ~/.config/hypr/hyprland.lua before require("default.hypr.omarchy"), then add
-- only the bindings you want below:
--   omarchy_default_bindings = false

-- To disable all preinstalled app/webapp bindings, set:
--   omarchy_preinstalled_bindings = false

-- Add a new binding.
-- o.bind("SUPER + SHIFT + R", "SSH", "alacritty -e ssh your-server")

-- Change an existing binding by unbinding it first, then binding the key again.
-- This example changes SUPER+SPACE from the launcher to the Omarchy root menu.
-- hl.unbind("SUPER + SPACE")
-- o.bind("SUPER + SPACE", "Omarchy menu", "omarchy-menu toggle root")

-- Disable a default binding without replacing it.
-- hl.unbind("SUPER + SHIFT + B")

-- Logitech MX Keys examples:
-- o.bind("SUPER + SHIFT + S", nil, "omarchy-capture-screenshot")
-- o.bind("SUPER + H", nil, "voxtype record toggle")
-- o.bind("SUPER + PERIOD", nil, "omarchy-shell shell toggle omarchy.emojis")

-- Easy dictation toggle: either Alt key, including Right Alt.
o.bind("ALT + SPACE", "Toggle dictation", "voxtype record toggle")

-- Consume Escape only during dictation; leave normal app Escape untouched when idle.
do
  local cancel = hl.bind("ESCAPE", hl.dsp.exec_cmd("voxtype record cancel"), {
    description = "Cancel dictation",
    ignore_mods = true,
  })
  cancel:set_enabled(false)
  local state_path = os.getenv("XDG_RUNTIME_DIR") .. "/voxtype/state"
  local function update_cancel_binding()
    local file = io.open(state_path, "r")
    local state = file and file:read("*l") or "idle"
    if file then file:close() end
    cancel:set_enabled(state == "recording" or state == "transcribing")
  end
  update_cancel_binding()
  hl.timer(update_cancel_binding, { timeout = 50, type = "repeat" })
end

-- Omasnap replaces Omarchy's Print screenshot action.
hl.unbind("PRINT")
hl.unbind("F12")
hl.unbind("ALT + SHIFT + 4")

o.bind("PRINT", "Screenshot", "omasnap")
o.bind("F12", "Screenshot", "omasnap")
o.bind("ALT + SHIFT + 4", "Screenshot", "omasnap")

hl.layer_rule({
  match = { namespace = "^omasnap$" },
  no_anim = true,
  animation = "none",
  no_screen_share = true,
})
