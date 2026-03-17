; =====================================================
;   pws32z's Biome Macro - AHK v1
; =====================================================
#NoEnv
#SingleInstance Force
#Persistent
SetWorkingDir %A_ScriptDir%
SendMode Input

; ---------- Globals ----------
global ConfigFile     := A_ScriptDir . "\config.ini"
global WebhookURL     := ""
global PrivateServer  := ""
global DiscordID      := ""
global Started        := 0
global Paused         := 0
global LastBiome      := ""
global LogFilePath    := ""
global LogOffset      := 0
global RobloxLogPath  := ""

global BiomeWindy       := "Message"
global BiomeSnowy       := "Message"
global BiomeRainy       := "Message"
global BiomeSandStorm   := "Message"
global BiomeHell        := "Message"
global BiomeStarfall    := "Message"
global BiomeCorruption  := "Message"
global BiomeNull        := "Message"
global BiomePumpkinMoon := "Message"
global BiomeGraveyard   := "Message"

; ---------- Ensure Config Exists ----------
if !FileExist(ConfigFile)
{
    f := FileOpen(ConfigFile, "w", "CP0")
    f.WriteLine("[Webhook]")
    f.WriteLine("webhook_url=")
    f.WriteLine("private_server=")
    f.WriteLine("discord_user_id=")
    f.WriteLine("")
    f.WriteLine("[Biomes]")
    f.WriteLine("windy=Message")
    f.WriteLine("snowy=Message")
    f.WriteLine("rainy=Message")
    f.WriteLine("sand_storm=Message")
    f.WriteLine("hell=Message")
    f.WriteLine("starfall=Message")
    f.WriteLine("corruption=Message")
    f.WriteLine("null=Message")
    f.WriteLine("pumpkin_moon=Message")
    f.WriteLine("graveyard=Message")
    f.Close()
}

; ---------- Read Config ----------
IniRead, WebhookURL,      %ConfigFile%, Webhook, webhook_url,       ERROR
IniRead, PrivateServer,   %ConfigFile%, Webhook, private_server,    ERROR
IniRead, DiscordID,       %ConfigFile%, Webhook, discord_user_id,   ERROR
IniRead, BiomeWindy,      %ConfigFile%, Biomes,  windy,             Message
IniRead, BiomeSnowy,      %ConfigFile%, Biomes,  snowy,             Message
IniRead, BiomeRainy,      %ConfigFile%, Biomes,  rainy,             Message
IniRead, BiomeSandStorm,  %ConfigFile%, Biomes,  sand_storm,        Message
IniRead, BiomeHell,       %ConfigFile%, Biomes,  hell,              Message
IniRead, BiomeStarfall,   %ConfigFile%, Biomes,  starfall,          Message
IniRead, BiomeCorruption, %ConfigFile%, Biomes,  corruption,        Message
IniRead, BiomeNull,       %ConfigFile%, Biomes,  null,              Message
IniRead, BiomePumpkinMoon,%ConfigFile%, Biomes,  pumpkin_moon,      Message
IniRead, BiomeGraveyard,  %ConfigFile%, Biomes,  graveyard,         Message

if (WebhookURL    = "ERROR") WebhookURL    := ""
if (PrivateServer = "ERROR") PrivateServer := ""
if (DiscordID     = "ERROR") DiscordID     := ""

; ---------- Build GUI ----------
Gui, Main:New
Gui, Main:+LabelMainGui
Gui, Main:Color, 1e1e2e
Gui, Main:Font, s14 bold cE0E0FF, Segoe UI
Gui, Main:Add, Text, x10 y8 w480 Center, pws32z's Biome Macro

Gui, Main:Font, s11 bold cE0E0FF, Segoe UI
Gui, Main:Add, Button, x10  y35 w110 h28 gTabWebhook, Webhook
Gui, Main:Add, Button, x125 y35 w110 h28 gTabCredits, Credits

Gui, Main:Add, Text, x10 y68 w480 h1 +BackgroundSilver,

; --- Webhook tab ---
Gui, Main:Font, s11 cE0E0FF, Segoe UI
Gui, Main:Add, Text, x10  y80  w130 h22 vLblWH, Webhook URL:
Gui, Main:Add, Edit, x145 y78  w340 h24 vWebhookURLField +BackgroundWhite, %WebhookURL%

Gui, Main:Add, Text, x10  y112 w130 h22 vLblPS, Private Server:
Gui, Main:Add, Edit, x145 y110 w340 h24 vPSField +BackgroundWhite, %PrivateServer%

Gui, Main:Add, Text, x10  y144 w130 h22 vLblDI, Discord User ID:
Gui, Main:Add, Edit, x145 y142 w340 h24 vDiscIDField +BackgroundWhite, %DiscordID%

; --- Credits tab (hidden) ---
Gui, Main:Add, Text,   x10 y80  w460 h22 vCredLine1 Hidden, pws32z - Creator
Gui, Main:Add, Text,   x10 y102 w460 h22 vCredLine2 Hidden, pws32z's Biome Macro
Gui, Main:Font, s11 bold cE0E0FF, Segoe UI
Gui, Main:Add, Button, x10 y130 w160 h30 vCredDiscord Hidden gOpenDiscord, Join our Discord

; --- Bottom bar ---
Gui, Main:Font, s11 cE0E0FF, Segoe UI
Gui, Main:Add, Text, x10 y250 w480 h20 vStatusLabel, Status: Idle

Gui, Main:Font, s11 bold cE0E0FF, Segoe UI
Gui, Main:Add, Button, x10  y272 w75 h30 gStartMacro,  Start
Gui, Main:Add, Button, x92  y272 w75 h30 gPauseMacro,  Pause
Gui, Main:Add, Button, x174 y272 w75 h30 gStopMacro,   Stop
Gui, Main:Add, Button, x256 y272 w90 h30 gTestWebhook, Test Hook
Gui, Main:Add, Button, x354 y272 w130 h30 gSaveConfig, Save Config

Gui, Main:Show, w505 h312, pws32z's Biome Macro

; White background brush for edit fields
EditBrush := DllCall("CreateSolidBrush", "UInt", 0xFFFFFF)
OnMessage(0x0133, "WM_CTLCOLOREDIT")

GoSub, TabWebhook
return

; =====================================================
WM_CTLCOLOREDIT(wParam, lParam) {
    global EditBrush
    DllCall("SetTextColor", "Ptr", wParam, "UInt", 0x000000)
    DllCall("SetBkColor",   "Ptr", wParam, "UInt", 0xFFFFFF)
    return EditBrush
}

; =====================================================
TabWebhook:
    GuiControl, Main:Show, LblWH
    GuiControl, Main:Show, WebhookURLField
    GuiControl, Main:Show, LblPS
    GuiControl, Main:Show, PSField
    GuiControl, Main:Show, LblDI
    GuiControl, Main:Show, DiscIDField
    GuiControl, Main:Hide, CredLine1
    GuiControl, Main:Hide, CredLine2
    GuiControl, Main:Hide, CredDiscord
return

TabCredits:
    GuiControl, Main:Hide, LblWH
    GuiControl, Main:Hide, WebhookURLField
    GuiControl, Main:Hide, LblPS
    GuiControl, Main:Hide, PSField
    GuiControl, Main:Hide, LblDI
    GuiControl, Main:Hide, DiscIDField
    GuiControl, Main:Show, CredLine1
    GuiControl, Main:Show, CredLine2
    GuiControl, Main:Show, CredDiscord
return

; =====================================================
SaveConfig:
    Gui, Main:Submit, NoHide
    WebhookURL    := WebhookURLField
    PrivateServer := PSField
    DiscordID     := DiscIDField

    FileDelete, %ConfigFile%
    f := FileOpen(ConfigFile, "w", "CP0")
    f.WriteLine("[Webhook]")
    f.WriteLine("webhook_url="     . WebhookURL)
    f.WriteLine("private_server="  . PrivateServer)
    f.WriteLine("discord_user_id=" . DiscordID)
    f.WriteLine("")
    f.WriteLine("[Biomes]")
    f.WriteLine("windy="        . BiomeWindy)
    f.WriteLine("snowy="        . BiomeSnowy)
    f.WriteLine("rainy="        . BiomeRainy)
    f.WriteLine("sand_storm="   . BiomeSandStorm)
    f.WriteLine("hell="         . BiomeHell)
    f.WriteLine("starfall="     . BiomeStarfall)
    f.WriteLine("corruption="   . BiomeCorruption)
    f.WriteLine("null="         . BiomeNull)
    f.WriteLine("pumpkin_moon=" . BiomePumpkinMoon)
    f.WriteLine("graveyard="    . BiomeGraveyard)
    f.Close()

    GuiControl, Main:, StatusLabel, Status: Config saved!
    SetTimer, ResetStatus, -2000
return

ResetStatus:
    if (Started && !Paused)
        GuiControl, Main:, StatusLabel, % "Running | Last biome: " . (LastBiome = "" ? "Normal" : LastBiome)
    else if Paused
        GuiControl, Main:, StatusLabel, Status: Paused
    else
        GuiControl, Main:, StatusLabel, Status: Idle
return

; =====================================================
TestWebhook:
    GoSub, SaveConfig
    if (WebhookURL = "") {
        MsgBox, 48, Error, No webhook URL entered.
        return
    }
    SendWebhook("{""embeds"":[{""description"":""Test webhook from pws32z's Biome Macro!"",""color"":65280}]}")
    MsgBox, 64, Test, Webhook sent! Check your Discord channel.
return

; =====================================================
StartMacro:
    if Started
        return
    GoSub, SaveConfig
    if (WebhookURL = "") {
        MsgBox, 48, Error, Please enter a Webhook URL first.
        return
    }

    ; Find log folder
    EnvGet, LocalAppData, LOCALAPPDATA
    RobloxLogPath := LocalAppData . "\Roblox\logs"
    if !FileExist(RobloxLogPath) {
        ; Try store version
        Loop, %LocalAppData%\Packages\ROBLOXCORPORATION*
        {
            candidate := A_LoopFileFullPath . "\LocalState\logs"
            if FileExist(candidate) {
                RobloxLogPath := candidate
                break
            }
        }
    }

    LogFilePath := GetNewestLog(RobloxLogPath)
    if (LogFilePath = "") {
        MsgBox, 48, Error, Could not find Roblox log file.`nMake sure Roblox is open first.
        return
    }

    ; Start at end of current log so we only catch NEW biome events
    FileGetSize, LogOffset, %LogFilePath%
    LogOffset += 0

    Started   := 1
    Paused    := 0
    LastBiome := ""

    GuiControl, Main:, StatusLabel, Status: Running - watching log...
    SendWebhook("{""embeds"":[{""description"":""Macro started!"",""footer"":{""text"":""pws32z's Biome Macro""}}]}")
    SetTimer, PollLog, 500
return

PauseMacro:
    if !Started
        return
    Paused := !Paused
    if Paused
        GuiControl, Main:, StatusLabel, Status: Paused
    else
        GuiControl, Main:, StatusLabel, % "Running | Last biome: " . (LastBiome = "" ? "Normal" : LastBiome)
return

StopMacro:
    SetTimer, PollLog, Off
    if Started
        SendWebhook("{""embeds"":[{""description"":""Macro stopped."",""footer"":{""text"":""pws32z's Biome Macro""}}]}")
    Started := 0
    Paused  := 0
    GoSub, SaveConfig
    GuiControl, Main:, StatusLabel, Status: Idle
return

; =====================================================
PollLog:
    global LogFilePath, LogOffset, LastBiome, RobloxLogPath

    if (!Started || Paused)
        return

    ; Switch to newer log if Roblox restarted
    newLog := GetNewestLog(RobloxLogPath)
    if (newLog != "" && newLog != LogFilePath) {
        LogFilePath := newLog
        FileGetSize, LogOffset, %LogFilePath%
        LogOffset += 0
        return
    }

    ; Check if file grew
    FileGetSize, curSize, %LogFilePath%
    curSize += 0
    if (curSize = 0 || curSize <= LogOffset)
        return

    bytesToRead := curSize - LogOffset

    ; Open file with FILE_SHARE_READ|FILE_SHARE_WRITE so Roblox lock is bypassed
    hFile := DllCall("CreateFileW"
        , "Str",  LogFilePath
        , "UInt", 0x80000000        ; GENERIC_READ
        , "UInt", 0x3               ; FILE_SHARE_READ | FILE_SHARE_WRITE
        , "Ptr",  0
        , "UInt", 3                 ; OPEN_EXISTING
        , "UInt", 0
        , "Ptr",  0
        , "Ptr")

    if (hFile = -1 || hFile = 0)
        return

    ; Seek to offset
    DllCall("SetFilePointer", "Ptr", hFile, "Int", LogOffset, "Ptr", 0, "UInt", 0)

    ; Read bytes into buffer
    VarSetCapacity(buf, bytesToRead + 1, 0)
    DllCall("ReadFile", "Ptr", hFile, "Ptr", &buf, "UInt", bytesToRead, "UInt*", bytesRead, "Ptr", 0)
    DllCall("CloseHandle", "Ptr", hFile)

    if (bytesRead = 0)
        return

    LogOffset := curSize
    chunk := StrGet(&buf, bytesRead, "UTF-8")

    if (chunk = "")
        return

    ; Parse lines
    Loop, Parse, chunk, `n, `r
    {
        line := A_LoopField
        if !InStr(line, "hoverText")
            continue

        biome := ExtractHoverText(line)
        ToolTip, Last line matched:`n%biome%
        if (biome = "" || biome = LastBiome)
            continue

        prevBiome := LastBiome
        LastBiome := biome
        GuiControl, Main:, StatusLabel, % "Running | Biome: " . biome

        if (biome = "NORMAL") {
            if (prevBiome != "" && prevBiome != "NORMAL") {
                setting := GetBiomeSetting(prevBiome)
                if (setting != "Nothing")
                    SendBiomeEmbed(prevBiome, false)
            }
        } else {
            setting := GetBiomeSetting(biome)
            if (setting != "Nothing")
                SendBiomeEmbed(biome, true)
        }
    }
return

; =====================================================
GetNewestLog(logDir) {
    if (logDir = "" || !FileExist(logDir))
        return ""
    newest := ""
    newestTime := 0
    Loop, %logDir%\*.log
    {
        if InStr(A_LoopFileName, "Installer")
            continue
        if InStr(A_LoopFileName, "bootstrapper")
            continue
        FileGetTime, ft, %A_LoopFileFullPath%, M
        if (ft > newestTime) {
            newestTime := ft
            newest := A_LoopFileFullPath
        }
    }
    return newest
}

ExtractHoverText(line) {
    needle := "hoverText"":"""
    nLen := StrLen(needle)

    ; Get first hoverText
    pos1 := InStr(line, needle, false, 1)
    if (!pos1)
        return ""
    start1 := pos1 + nLen
    rest1 := SubStr(line, start1)
    end1 := InStr(rest1, """")
    if (!end1)
        return ""
    val1 := SubStr(rest1, 1, end1 - 1)

    ; Try to get second hoverText
    pos2 := InStr(line, needle, false, pos1 + nLen)
    if (pos2) {
        start2 := pos2 + nLen
        rest2 := SubStr(line, start2)
        end2 := InStr(rest2, """")
        if (end2) {
            val2 := SubStr(rest2, 1, end2 - 1)
            StringUpper, val2, val2
            ; Second hoverText is the biome (smallImage)
            ToolTip, Detected biome: %val2%
            return val2
        }
    }

    ; Only one hoverText found - use it only if it looks like a biome
    StringUpper, val1, val1
    knownBiomes := "NORMAL|WINDY|SNOWY|RAINY|SAND STORM|HELL|STARFALL|CORRUPTION|NULL|GLITCHED|DREAMSPACE|PUMPKIN MOON|GRAVEYARD|BLOOD RAIN"
    Loop, Parse, knownBiomes, |
    {
        if (val1 = A_LoopField) {
            ToolTip, Detected biome (single): %val1%
            return val1
        }
    }
    return ""
}

GetBiomeSetting(b) {
    global BiomeWindy, BiomeSnowy, BiomeRainy, BiomeSandStorm, BiomeHell
    global BiomeStarfall, BiomeCorruption, BiomeNull, BiomePumpkinMoon, BiomeGraveyard
    StringUpper, b, b
    if (b = "WINDY")        return BiomeWindy
    if (b = "SNOWY")        return BiomeSnowy
    if (b = "RAINY")        return BiomeRainy
    if (b = "SAND STORM")   return BiomeSandStorm
    if (b = "HELL")         return BiomeHell
    if (b = "STARFALL")     return BiomeStarfall
    if (b = "CORRUPTION")   return BiomeCorruption
    if (b = "NULL")         return BiomeNull
    if (b = "PUMPKIN MOON") return BiomePumpkinMoon
    if (b = "GRAVEYARD")    return BiomeGraveyard
    return "Message"
}

SendBiomeEmbed(biomeName, isStart) {
    global WebhookURL, PrivateServer, DiscordID
    color := GetBiomeColor(biomeName)
    ts    := A_Hour . ":" . A_Min . ":" . A_Sec

    if isStart {
        psLine := (PrivateServer != "") ? "\n" . PrivateServer : ""
        desc := "> ## Biome Started - " . biomeName . psLine
    } else {
        desc := "> ## Biome Ended - " . biomeName
    }

    pingContent := ""
    if isStart {
        setting := GetBiomeSetting(biomeName)
        if (setting = "Ping" && DiscordID != "")
            pingContent := ",""content"":""<@" . DiscordID . ">"""
        if (biomeName = "GLITCHED" || biomeName = "DREAMSPACE")
            pingContent := ",""content"":""@everyone"""
    }

    payload := "{""embeds"":[{""title"":""[" . ts . "]"",""color"":" . color . ",""description"":""" . desc . """,""footer"":{""text"":""pws32z's Biome Macro""}}]" . pingContent . "}"
    ToolTip, Sending webhook for: %biomeName%
    SendWebhook(payload)
    ToolTip
}

GetBiomeColor(b) {
    StringUpper, b, b
    if (b = "WINDY")        return 9498623
    if (b = "SNOWY")        return 12908278
    if (b = "RAINY")        return 4423167
    if (b = "SAND STORM")   return 15974012
    if (b = "HELL")         return 6029081
    if (b = "STARFALL")     return 6784224
    if (b = "CORRUPTION")   return 9454591
    if (b = "NULL")         return 1
    if (b = "GLITCHED")     return 6749952
    if (b = "DREAMSPACE")   return 16744447
    if (b = "PUMPKIN MOON") return 13983497
    if (b = "GRAVEYARD")    return 8947848
    if (b = "BLOOD RAIN")   return 16711680
    return 7929855
}

SendWebhook(payload) {
    global WebhookURL
    if (WebhookURL = "") {
        ToolTip, ERROR: WebhookURL is empty!
        return
    }
    try {
        whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
        whr.Open("POST", WebhookURL, true)
        whr.SetRequestHeader("Content-Type", "application/json; charset=utf-8")
        whr.Send(payload)
        whr.WaitForResponse(5000)
        status := whr.Status
        ToolTip, Webhook sent - HTTP %status%
        SetTimer, ClearToolTip, -3000
    } catch e {
        ToolTip, Webhook ERROR: %e%
        SetTimer, ClearToolTip, -5000
    }
}

ClearToolTip:
    ToolTip
return

; =====================================================
OpenDiscord:
    Run, https://discord.gg/CDkdD4Whkx
return

MainGuiClose:
MainGuiEscape:
    GoSub, StopMacro
    DllCall("DeleteObject", "Ptr", EditBrush)
    ExitApp
return
