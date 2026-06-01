# 🐱 Cat Dashboard Widget

I'm a person with severe brain difficulties in the regard that I constantly keep losing track of things I'm doing or supposed to be doing. Taking care of my cats is one of the main things I struggle with — I love them to the moon, but goddammit I can never remember to check the auto litter box and the auto food dispenser. Yes, auto. We have everything automatic that just needs replacing every once in a while, and I still struggle with that.

All culminated in a fatidic day where my girlfriend woke me up on a Sunday at 8am because I forgot to replenish the feeders. Waking up at 8am on a Sunday should be a crime, so I decided "no more!" and designed this little widget/dashboard in Python using PySide6. Pretty simple dashboard connected with Home Assistant API calls that allows you to monitor litter box and feeder states and send manual feed actions to the cats. Took around 2/3 sessions to fully get it down since I am an apologist of programming my personal stuff with absolutely no AI in my IDE, just like the good? old days. There is already a lot of AI in my work — we can leave that there.

---

## What it does

- Monitors litter box bin status and cleaning state via Home Assistant sensors
- Shows per-cat food level, last feed time, and today's feeding count
- Manual feed buttons per cat and a "Feed all" option
- Sits permanently on your desktop as a borderless always-on-bottom widget — you can't ignore it
- System tray icon with quit and Windows startup toggle
- Auto-refreshes every minute without freezing the UI (threaded API calls)

---

## Screenshot

![Dashboard](screenshots/dashboard.png)

---

## Built with

- **Python** — core language
- **PySide6** — UI framework
- **Home Assistant** — smart home platform providing all sensor data and actions
- **requests** — HTTP calls to the HA API
- **python-dotenv** — managing credentials via `.env`
- **pywin32** — Windows API integration
- **PyInstaller** — packaging into a standalone `.exe`
- **Excalidraw** — initial sketching and planning
- **Bruno** — API testing during development

---

## Configuration

The widget is configured via `config.json` alongside the executable:

```json
{
    "cats": [
        { "name": "CatName", "img": "assets/cat.png" }
    ],
    "icon": "assets/favicon-32x32.png"
}


```

HA credentials go in a `.env` file:

```
HA_URL=http://your-home-assistant-url
HA_TOKEN=your_long_lived_access_token
```

---

## Known limitations / future improvements

- Feed buttons have no loading state — response is just a timestamp label below the button, no visual feedback during the request
- UI layout and spacing is functional but not polished — suggestions welcome
- Not at all configurable or adjustable but that would be too much work for something that no one cares about
