# CS2 Settings Manager

A Windows app for switching CS2 settings on all Steam accounts on your PC. You keep different setting presets in `SET` folders and copy the one you want into every Steam account at once.

<img width="1182" height="822" alt="CS2 Settings Manager window" src="https://github.com/user-attachments/assets/7437a354-4135-417d-aedf-b232b715f8ee" />

## Presets

- SET MAIN
- SET TRYHARD
- SET FARMING
- SET ARMSRACE
- SET SKIN INSPECT
- SET PLAYHOUR

Each folder holds one set of CS2 config files. Applying a preset copies that folder into every Steam `userdata` profile it finds, so you don't have to copy settings to each account by hand.

## Features

- Creates any missing `SET` folders.
- Applies the chosen preset to every Steam profile.
- Buttons to open the app folder, the Steam `userdata` folder, and each `SET` folder.
- Log of what it did.
- Replaces the old separate BAT files with one app.

## How to use

1. Run `CS2 Settings Manager.exe` (in this repo, or from [Releases](../../releases)).
2. Click **Create SET Folders** if they are missing.
3. Put your CS2 config files in the right `SET` folder.
4. Pick a preset.
5. Check the Steam `userdata` path.
6. Click **Apply Selected Settings**.

The two `Launch Option` text files hold the CS2 launch options used for main and farming accounts.
