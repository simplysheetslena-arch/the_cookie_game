# Cookie Wars 🍪

A collection of seven progressively more chaotic simulations built with **Python and Pygame**. Every phase is a standalone script that shares reusable game components.

## Requirements

- Python 3 with the `pygame` package installed
- A desktop environment that can open a Pygame window

Install the dependency:

```bash
python -m pip install pygame
```

## Run a phase

Open a terminal in the **inner `the_cookie_game/` directory** (the one containing `assets/`, `core/`, and `phases/`) and run:

```bash
python phases/phase_01.py
python phases/phase_02.py
python phases/phase_03.py
python phases/phase_04.py
python phases/phase_05.py
python phases/phase_06.py
python phases/phase_07.py
```

Each phase is launched separately; you only need to run the one you want to see.

## The seven phases

| Phase | Gameplay |
| --- | --- |
| **01 — One Ball** | A white ball moves toward a cookie, collects it, turns green, and displays a heart. |
| **02 — Two Balls** | Two balls race from opposite corners. The winner turns green; the other turns blue and looks sad. |
| **03 — The Conspiracy** | Four balls race; the top-right ball wins. The three losers gather and display a shared conversation bubble. |
| **04 — The Ambush** | The previous winner walks toward the cookie while the others coordinate an ambush; after the elimination, the attackers race for the cookie. |
| **05 — The Swarm** | A configurable number of balls spawn beyond a minimum cookie distance with random speeds. Collision handling discourages overlapping, allowing traffic jams. |
| **06 — Random Battles** | Balls race toward the cookie; close encounters randomly eliminate one contestant. |
| **07 — The Hunger Games** | Twenty-four numbered tributes in twelve color-coded pairs move through three rounds of randomly generated, invisible destinations. Collisions trigger paused fights with angry speech bubbles. The survivors then race toward a cookie that spawns at a random non-overlapping location. |

## Phase 7 — The Hunger Games

- **Starting layout:** 24 tributes arranged in a circle, numbered 1–24. Each pair belongs to the same district and shares a color.
- **Round 1:** 16 invisible destinations, including one in the center and 15 farther out.
- **Round 2:** 11 new destinations, including the center, closer to the arena center overall.
- **Round 3:** 5 new destinations, including the center, closer in again.
- **Progression:** Each living tribute picks a random destination for the round. A new round begins after the remaining living tributes reach their destinations and active fights finish.
- **Fights:** When living tributes get close, they stop briefly with angry speech bubbles. One is eliminated at random; the survivor continues.
- **Finale:** The cookie appears at a random position that avoids overlapping living tributes. The first survivor to reach it wins.
- **Scoreboard:** Displays living and eliminated counts, fights, survivor tokens, and fallen tokens with their original district colors and numbers.
- **Background:** Uses `assets/hunger_games.png` when available. The map is fitted without cropping, and the full simulation view is scaled to fit the monitor.

**Phase 7 controls:** `R` starts a fresh randomized game; `Space` pauses or resumes; `Esc` exits. Earlier phases support `R` to restart and `Esc` to quit.

## Customize the simulations

Edit the constants near the beginning of each phase script. For example:

- `NUMBER_OF_BALLS`, `MIN_SPEED`, and `MAX_SPEED` control participant count and randomized movement speeds where applicable.
- `COOKIE_SIZE` changes the displayed cookie size.
- In `phase_07.py`, `ROUND_MIN_CENTER_DISTANCES`, `ROUND_MAX_RADII`, and `MIN_DISTANCE_BETWEEN_POINTS` control the random destinations.
- `FIGHT_DURATION` controls how long phase 7 fight animations last.
- `ARENA_WIDTH`, `ARENA_HEIGHT`, and `SIDEBAR_WIDTH` define the phase 7 logical canvas and scoreboard geometry.

Keep the image filenames and paths consistent with the scripts:

```text
the_cookie_game/
├── assets/
│   ├── cookie.png
│   └── hunger_games.png
├── core/
│   ├── ball.py
│   ├── collisions.py
│   ├── cookie.py
│   ├── movement.py
│   └── speech_bubble.py
└── phases/
    ├── phase_01.py
    ├── ...
    └── phase_07.py
```

## Notes

- The `.png` assets are provided in `assets/`; replace them with your own artwork while keeping the expected filenames.
- The program is a **visual simulation**, not a player-controlled game.
- Random selections mean every replay may produce different winners, matchups, and destination layouts.
