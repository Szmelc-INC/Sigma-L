# SigmaⓁ Communicator

## About:
> SigmaⓁ is a project that began as a joke, turned into reality. \
> By [$x66] and [_Se2_] 4 [Szmelc.INC] / [Entropy Linux] \
> It's point is to be light, encrypted p2p and configurable (and also funny name, don't forget the funny name!) \
> In future, we plan to add as much API's and "briges" as possible, to connect SigmaL to data stream from Discord, Matrix, Telegram, IRC or any other communicator. \
> Then in far future, we want to build in GSM functionality (SIM card telephony) + instructions & software on building your own call center!

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
