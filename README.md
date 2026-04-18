# MultiFMacro - Discord Server: https://discord.gg/4XsAKHmSg5

A feature-rich Roblox Sol's RNG macro with automatic biome, aura, egg, merchant, and Eden detection — all in one clean UI.

![Downloads](https://img.shields.io/github/downloads/pws32z/MultiFMacro/total?style=flat-square&color=7c6af7&label=Downloads)
![Version](https://img.shields.io/badge/version-V4.4-7c6af7?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)
![Language](https://img.shields.io/badge/language-Python-3776AB?style=flat-square&logo=python)
![TotalDownloads](https://img.shields.io/github/downloads/pws32z/MultiFMacro/total)

---

## Features

🌍 **Biome Detection**
Automatically detects active biomes from the Roblox log. Sends a Discord webhook notification when a biome starts or ends, with optional ping for specific biomes.

✨ **Aura Detection**
Detects aura rolls from the log and sends webhook notifications with rarity info. Supports custom rarity thresholds and optional Discord pings.

🥚 **Egg Detection**
Detects special eggs via log reading or Chat OCR (no FastFlags required). Sends a webhook notification with the egg name. Fully calibratable screen region with adjustable re-detect delay.

🛒 **Merchant Detection**
Detects merchant appearances (Mari, Jester, Rin) via log reading or OCR fallback. Sends a webhook with the merchant name and image. Configurable re-detect delay.

🌌 **Eden Detection**
Detects The Void Cracks event via log reader and a dedicated Chat OCR scanner (no FastFlags needed). Sends a Discord webhook with optional ping. Calibratable screen region and re-detect delay.

🎮 **Remote Control**
Control the macro remotely via Discord commands. Start and stop Egg, Merchant, and Eden OCR from anywhere. Buttons update live in the UI when toggled remotely. Starting any OCR via remote automatically stops the main macro.

Available commands:
`!start` `!stop` `!pause` `!starteggocr` `!stopeggocr` `!startmerchantocr` `!stopmerchantocr` `!startedenocr` `!stopedenocr` `!cmds`

📊 **Unified Detection Tab**
All detections are consolidated into one tab for easy management and monitoring.

🔔 **Discord Webhooks**
Full webhook support across all detections. Customizable embeds with timestamps, thumbnails, rarity info, and Discord ID pings.

⚙️ **Anti-Kick**
Built-in anti-kick system to keep your session alive during long macro runs.

--

## Requirements
- Windows 10/11
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) *(for Egg / Merchant / Eden OCR)*
- Python 3.10+ *(if running from source)*

---

## Installation
1. Download the latest release
2. Run `MultiFMacro.exe`
3. Configure your webhook URL and Discord ID in the Settings tab
4. Hit **Start**
