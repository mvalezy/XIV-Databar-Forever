<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ZelionGG/XIV_Databar-Continued">
    <kbd><img src="icon.png" alt="Logo" width="130" height="130"></kbd>
  </a>

  <h3 align="center">XIV_Databar Continued — Forever fork</h3>

  <p align="center">
    Personal fork of XIV_Databar Continued, adapted for <strong>World of Warcraft: Forever</strong> (beta 1.60.1)
    <br />
    <br />
    <a href="https://github.com/mvalezy/XIV-Databar-Forever/issues">Report a Forever compatibility bug</a>
    ·
    <a href="https://github.com/ZelionGG/XIV_Databar-Continued">Original project</a>
  </p>
</div>

> [!IMPORTANT]
> **I am not an official developer and I have no affiliation with the original
> authors of XIV_Databar Continued.** All credit goes to the authors listed
> below; my only contribution is making the addon run on WoW Forever, with the
> help of AI.
>
> **This is not the upstream repository.** For features, options, screenshots,
> the roadmap, translations and everything else about the addon, read the
> original project instead:
> **<https://github.com/ZelionGG/XIV_Databar-Continued>**
>
> Please do not send ZelionGG or the original contributors questions about this
> fork, and do not report Forever issues to them. Forever-related issues belong
> [here](https://github.com/mvalezy/XIV-Databar-Forever/issues).

## What this fork contains

- The addon code with the changes needed for **WoW Forever 1.60.1**
  (`_classic_beta_`): new interface version, Forever client detection, adjusted
  APIs and per-character storage, and Retail-only features disabled where
  Forever has no content for them.
- The full list of changes and the install steps: **[FOREVER.md](FOREVER.md)**.
- Everything else — description, slash commands (`/xivc`, `/xivbar`, `/xbc`),
  modules, profiles, media and localizations — is unchanged from upstream: see
  the [original README](https://github.com/ZelionGG/XIV_Databar-Continued#readme).

## Installation

**The repository does not contain the embedded libraries** (`Libs/`), by design:
Ace3, LibSharedMedia, LibQTip, LibDataBroker and the others are not stored here.
So **do not copy this folder into the game as-is** — it would load without its
libraries and fail. One command fetches them and builds the ready-to-use addon
folder.

### Requirements

- Windows (the game client runs there), plus **Python 3.10 or newer**
  (`python --version` or `py --version` in PowerShell; install from
  [python.org](https://www.python.org/downloads/) if needed).
- An internet connection for the libraries, which are downloaded and
  checksum-verified against the pinned versions in
  `scripts/forever-libs.json`.
- Keep the repository **outside** the game folder, otherwise WoW will try to
  read it as an addon.

### Steps (PowerShell)

```powershell
# 1. Get the code, once. (You can also use the green "Code" > "Download ZIP"
#    button and unzip it wherever you like.)
git clone https://github.com/mvalezy/XIV-Databar-Forever.git "$env:USERPROFILE\XIV-Databar-Forever"
$addon = "$env:USERPROFILE\XIV-Databar-Forever"

# 2. Build the complete addon folder: downloads the libraries, verifies the
#    checksums, checks every file reference, then writes a ZIP.
$py = "python"   # use "py" if that is what works on your machine
& $py "$addon\scripts\package_forever.py"

# 3. Install it into the game (change the path if your WoW is elsewhere).
$wow = "D:\World of Warcraft\_classic_beta_\Interface\AddOns"
$zip = Get-ChildItem "$addon\dist\XIV_Databar_Forever-*.zip" |
       Sort-Object LastWriteTime | Select-Object -Last 1
Expand-Archive $zip.FullName -DestinationPath $wow -Force
```

Before step 3, it is worth backing up `WTF\Account\<account>\SavedVariables\XIV_Databar_Continued.lua`
and the old addon folder, in case you want to restore your settings.

### Result to check

You must end up with exactly this structure, `XIV_Databar_Continued` being the
folder name given by the ZIP (do not rename it to `XIV-Databar-Forever`):

```
_classic_beta_\Interface\AddOns\XIV_Databar_Continued\
├── XIV_Databar_Continued.toc     <- ## Interface: 16001
├── Core\  Mainline\  locales\  media\
├── Libs\                          <- downloaded by the packager
├── core.lua  options.lua  embeds.xml  icon.png
```

Launch WoW, enable the addon for your character, then type `/xivc` in game.

### Prebuilt archive

If you would rather not run Python, grab the ZIP from the
[releases page](https://github.com/mvalezy/XIV-Databar-Forever/releases) and
extract it into `_classic_beta_\Interface\AddOns\`.

> [!NOTE]
> Building manually with `python3 scripts/package_forever.py --output dist/forever.zip`
> writes the archive wherever you ask. See [FOREVER.md](FOREVER.md) for the
> tested commands and the known limitations.

## Credits

All credit for the addon belongs to its original authors:

- [ZelionGG](https://github.com/ZelionGG) — maintainer of XIV_Databar Continued
  and author of most of the current code.
- [MilleXIV](https://github.com/MilleXIV) — revived the project and refactored
  the code. Original lead developer of the __XIV_Databar__ fork.
- [Vicious-wow](https://github.com/Vicious-wow/XIV_Databar) and
  [Kozoaku](https://github.com/Kozoaku/XIV_Databar) — kept the project going and
  modernized it before ZelionGG took over.
- [saxitoxin](https://www.wowinterface.com/downloads/info23745-SX_DataBar.html) —
  author of SX_Databar, which this addon reworks.
- u/sammojo — idea, textures and the bar description.
- u/keyboardturn — updated spec icons.
- Locale contributors: PhatsoTGT (German), Amanthuul (Russian), Yaoenqi
  (Chinese), [class2u](https://github.com/class2u) (Chinese, Taiwan),
  [BrunoKrugel](https://github.com/BrunoKrugel) (Brazilian Portuguese).

The WoW Forever adaptation was done by
[mvalezy](https://github.com/mvalezy) with AI assistance and applies to this
fork only.

## License

Distributed under the GPL-3.0 License, same as upstream. See `LICENSE`, or the
[original license file](https://github.com/ZelionGG/XIV_Databar-Continued/blob/master/LICENSE.txt).
