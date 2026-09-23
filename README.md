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

1. Exit WoW completely and back up the current addon folder plus
   `WTF/Account/<account>/SavedVariables/XIV_Databar_Continued.lua`.
2. Replace the old addon folder with the files from a
   [release archive](https://github.com/mvalezy/XIV-Databar-Forever/releases),
   so that you end up with:
   `_classic_beta_\Interface\AddOns\XIV_Databar_Continued\`.
3. The folder must be named `XIV_Databar_Continued` and contain
   `XIV_Databar_Continued.toc`, `Core/`, `Mainline/`, `Libs/` and `options.lua`.

> [!NOTE]
> A ZIP downloaded from the green “Code” button has no libraries and will not
> work. Use a release archive, or build one with
> `python3 scripts/package_forever.py --output dist/forever.zip`
> (see [FOREVER.md](FOREVER.md)).

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
