# SigmaⓁ Communicator
<img src="https://i.imgur.com/dAGTvMK.png" width="350">

## About:
> SigmaⓁ started as a fun idea that became a real project. Created by [$x66] and [Se2] under [Szmelc.INC] and [Entropy Linux], it's a lightweight, encrypted, and customizable p2p communication tool. We’re focused on keeping it secure ans simple. \
> Our goal is to add as many APIs and bridges as possible to connect SigmaⓁ with platforms like Discord, Matrix, Telegram, IRC, and more. Down the line, we also plan to add GSM functionality, letting you use SIM card telephony and even build your own call center using our framework! \
> Android & iOS Apps are also possibly comming in near future!

### Some other details:
> SigmaⓁ uses port `2137` as default communication's port \
> If Host has DDNS configured, it is possible to connect to a domain like `szmelc.com` instead of IP adress \
> Make sure Host has firewall rule allowing port `2137` as well as know's it's `public IP` adress (ipv4, ipv6 or domain name) \
> SigmaⓁ uses serializing RSA keypairs for encryption / decryption of most traffic. \
> It's actually possible to connect more clients to single host in single chatroom.

## Usage:
0. Setup: 
> First, make sure you have all dependencies by running `setup.sh` \
> After that you should be ready to roll, starting sigmal from `main.py` 

1. Commands: \
-`/clear` - Clear the chat screen \
-`/exit` - Exit the application \
-`/save` - Save chat history to a log file \
-`/help` - Display this help message \
-`/reload config` - Reload configuration from config.json \
-`/reconnect` - Reconnect to the current session \
-`/nick <new_nickname>` - Change your nickname \
-`/color <#HEX>` - Change your text color \
-`/toggle sound` - Toggle sound on/off \
-`/transfer` - Open file selection to send a file \
-`/fullscreen` - Toggle fullscreen mode on/off \

2. Config: \
```
{
  "window": {
    "width": 666,
    "height": 420
  },
  "colors": {
    "background": "#121212",
    "text": "#d3d3d3",
    "input_background": "#0b1a10",
    "input_text": "#ffffff",
    "host_color": "red",
    "client_color": "yellow",
    "system_message_color": "lightgreen"
  },
  "nicknames": {
    "host": "[H]",
    "client": "[C]"
  },
  "sound": {
    "enabled": true,
    "volume": {
      "message": 1,
      "error": 0.8,
      "connection_lost": 0.8
    },
    "paths": {
      "message": "sound/beep.wav",
      "error": "sound/error.wav",
      "connection_lost": "sound/silencer.wav"
    }
  }
}
```

### Project tree
```
$ tree
.
├── README.md
├── main.py
├── config.json
├── logs
├── sound
|   ├── ...
├── src
│   ├── cipher.py
│   ├── commands.py
│   ├── core.py
└── transfer

5 directories, 9 files
```

### Known issues:
- Buggy file transfer that auto saves any file
- Non clickable "clickable" URL's on receiving end
- ~~/recconect just crashes client~~ (Fixed!)
- Embeds don't work idk
- 

### To-Do
- Add markdown & css formatting support
- Add more commands
- Fix `/help` command output formatting
- Make config easier and bigger
- Make URL / Img embeds
- Add player for video / audio
- Add preview for text files
- Add emoji / utf-8 support
- Improve `setup.sh`
- Add bridges / webhooks for other platforms
- Add `/register` & `/login` functions. (will work on unique system UUID as authentication, letting user choose static nickname + password)
- Create dedicated SigmaⓁ Comm protocol to make it easier to write custom clients / modules for.
- Add support for static RSA
- Improve UI
- Encrypt files / URL's, everything
- Built in temporary file hosting like `bashupload.com` & `szmelc.com/trashupload` for alternative file transfer method.
- 
