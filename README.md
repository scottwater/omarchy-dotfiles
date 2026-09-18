# Omarchy dotfiles

Configuration for my Omarchy machines only. This repository is independent of
`~/Code/dotfiles` (macOS/headless VMs).

Chezmoi manages selected files, not all of `~/.config`. Omarchy still owns its
packaged defaults and generated themes. There are no automatic install scripts,
package removals, service changes, or `exact_` directories in this repository.

## What is saved

- Bash startup files and shortcuts, XCompose, Git and mise configuration.
- Hyprland user entry points/overrides, Omarchy shell preferences and agent choice.
- Alacritty, Foot, Ghostty, Kitty, tmux, Starship, imv and Chromium flags.
- Neovim configuration and `lazy-lock.json`, including the generated-theme symlink
  as a **symlink**, not its target's contents.
- Personal `lt` and `nvim-ruby-lsp` scripts.
- Voxtype configuration, clipboard helper and service definition.
- Atuin, Herdr, OpenCode, btop, input-method and desktop preferences.
- Lerd's main configuration (including its current calculated fields; see below).
- Optional laptop-specific monitor, Dell haptic and speaker-tuning configuration.
- The Lerd shell widget as a checksum-verified, commit-pinned external archive.
- Per-host package/tool/service inventories under `inventory/`.

Some files are currently unchanged from Omarchy's seeds. They are included as
small user-facing configuration entry points for future edits, not copies of the
inherited defaults in `/usr/share/omarchy`. Review migrations before reapplying
an older copy.

## Daily edits

For an ordinary, non-templated file edited in place:

```sh
chezmoi diff
chezmoi add --secrets=error ~/.config/hypr/bindings.lua
chezmoi diff
```

`chezmoi diff` shows what **applying the source would change in the live files**;
it is not a command to save those edits. Review the source repository's Git diff
before committing and pushing.

Four files have home-directory templates so another username works:

- `~/.bashrc`
- `~/.config/voxtype/config.toml`
- `~/.config/lerd/config.yaml`
- `~/.config/gtk-3.0/bookmarks`

For those, edit with `chezmoi edit <path>`, review `chezmoi diff <path>`, then
`chezmoi apply <path>`. If already edited live, use `chezmoi merge <path>` and
preserve the template expressions. Do not blanket re-add templates or recursively
add `~/.config`.

After an Omarchy update, inspect any differences before applying. Keep useful
migrations instead of restoring the old source over them.

## Package and service inventory

```sh
python3 "$(chezmoi source-path)/scripts/inventory.py"
git -C "$(chezmoi source-path)" diff -- inventory
```

The script performs read-only queries and updates only this repository's inventory.
Repeated captures with unchanged state produce no changes. It does not commit,
push, schedule itself, install packages or enable services.

Explicit packages include Omarchy-installed packages. Foreign packages are not
necessarily AUR packages. The full version list is diagnostic history, not a
rolling-release lockfile. Do **not** install every recorded package or enable all
recorded services on a new machine. Keep Omarchy responsible for system updates.

`mise` tool declarations are managed; installing the tools remains an explicit
`mise install`. Non-mise binaries (for example Lerd) need their normal installer.
The inventory does not cover every downloaded binary, Composer dependency,
container image or application database.

## Restore or add an Omarchy machine

1. Install current Omarchy and chezmoi. Keep a backup before replacing any files.
2. Initialize this repository **without `--apply`**:

   ```sh
   chezmoi init --source ~/Code/omarchy-dotfiles <private-repository-url>
   ```

3. Answer the hardware prompt. It defaults to **false** on a fresh initialization.
   Opt in only for the saved laptop's compatible monitor/speaker/haptic setup.
   For a recovery of lendr, opt in after confirming the hardware. This choice is
   stored as `data.applyHardware` in the local chezmoi config, not shared between
   hosts. Existing values are preserved by subsequent `chezmoi init` calls.
4. Review `chezmoi diff`. Install needed applications separately (Atuin, Lerd,
   Voxtype, etc.). Installers should generate their own wrappers and deployment
   state; don't copy binaries or credentials from the old machine.
5. Review and apply selected files, or run `chezmoi apply` once the whole diff is
   acceptable. The shell widget archive downloads automatically and is verified
   against its pinned checksum; no plugin code is executed by chezmoi.
6. Run `mise install` after reviewing the tool list. Most agent tools use `latest`,
   so this is not an exact-version rebuild; consult the inventory for old versions.
7. Reapply the theme named in `inventory/lendr/theme.txt` using
   `omarchy theme set "Tokyo Night"` if desired. Omarchy generates theme outputs.
8. If restoring service definitions, run `systemctl --user daemon-reload`, then
   explicitly enable only the services wanted on this machine after installing
   their prerequisites. Applying files does not enable or start them.
9. Log out/in or reload affected applications. Validate Hyprland changes with
   `hyprctl reload` and `hyprctl configerrors`.

On a second machine, review local changes first, then pull and apply separately:

```sh
chezmoi git -- pull --ff-only
chezmoi diff
# Resolve differences before proceeding.
chezmoi apply
```

Do not use unattended apply/update. Each machine should capture and push its
intentional edits before receiving changes from the other.

## Lerd and generated integrations

`lerd/config.yaml` contains both preferences and calculated state (`php.realised`
and resolved versions). It is initially captured faithfully, with only the home
path templated. Review that section on a fresh machine; let Lerd rebuild images
and regenerate deployment files rather than assuming cached image hashes exist.
`lerd install` is its one-time setup command; run the installer/setup deliberately,
then reconcile any configuration changes. Project `.lerd.yaml`, `.env`, database
volumes and project files are not included here.

The Lerd widget is pinned in `.chezmoiexternal.toml`. Updating it requires changing
both the commit URL and SHA-256. The existing checkout's `.git` directory is left
alone; on a fresh machine the widget is restored without Git metadata. Do not
expect a later `git pull` in that directory to update the managed archive version.

Lerd service/container output, tool-launcher wrappers and Herdr-generated agent
integrations are not dotfiles to replay. Regenerate them through their installers.
The Lerd phpMyAdmin definition and generated containers contain credential fields
and are intentionally excluded. Recover credentials through a password manager or
encrypted backup, not this repository. Some MIME handlers similarly depend on
launchers supplied by application installers.

Atuin's existing dotfiles feature setting is preserved, not enabled by this repo.
Avoid configuring it to compete with chezmoi for the same settings.

## Exclusions and backup boundary

Browser/1Password/Slack/Codex profiles, credentials, histories, caches, session
state, Neovim downloads, generated themes, backup copies, systemd enablement links
and Omarchy setup-invitation hooks are excluded. Empty/lower-value application
state is not captured merely because it lives in `~/.config`.

`.chezmoiignore` is a safety net, not a guarantee that an arbitrary future recursive
add is safe. Review new files and Git diffs before publishing. A private repository
is not a safe place for plaintext credentials.

Use an encrypted off-machine backup for application data and secrets. The current
root Snapper configuration does not cover the separate `/home` subvolume.

A local source directory is not an off-machine backup: create a private remote,
review the initial contents, commit and push. No remote is configured by this setup.
