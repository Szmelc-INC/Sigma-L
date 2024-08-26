# SigmaⓁ Communicator

## About:
> SigmaⓁ started as a fun idea that became a real project. Created by [$x66] and [Se2] under [Szmelc.INC] and [Entropy Linux], it's a lightweight, encrypted, and customizable p2p communication tool. We’re focused on keeping it secure ans simple. \
> Our goal is to add as many APIs and bridges as possible to connect SigmaⓁ with platforms like Discord, Matrix, Telegram, IRC, and more. Down the line, we also plan to add GSM functionality, letting you use SIM card telephony and even build your own call center using our framework!

### Some other details:
> SigmaⓁ uses port `2137` as default communication's port \
> If Host has DDNS configured, it is possible to connect to a domain like `szmelc.com` instead of IP adress \
> 

### Project tree
```
$ tree
.
├── README.md
├── main.py
├── config.json
├── logs
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
- Add more usefull commands
- Fix /help command output formatting
- Make config easier and bigger
- Make URL / Img embeds
- Add player for video / audio
- Add preview for text files
- Add emoji / utf-8 support
- Improve `setup.sh`
