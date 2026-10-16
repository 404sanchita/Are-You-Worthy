# Are You Worthy?

Are You Worthy? is a collection of small Python adventure/game scripts and prototypes that explore maze navigation, mountain-climbing challenges, and dragon encounters. The repository contains multiple versions and experimental files as the project evolved.

## Features

- Maze navigation and generation
- Mountain-climbing scenarios
- Dragon encounter / shooting mechanics
- Multiple project versions (progressing features and refinements)
- Background and visual helper scripts

## Repository layout

- background.py           — Background/visual helper logic
- maze.py                 — Maze related gameplay or utilities
- mountain.py             — Mountain-related gameplay or utilities
- maze,mountain,dragon.py — Combined/experimental file combining maze, mountain, and dragon features
- maze & moun.py          — Another variant of maze/mountain code (note: filename contains spaces & ampersand)
- mount&maze(delete_later).py — Temporary/older variant (marked for deletion)
- project_template.py     — Template and helper functions used across versions
- project2.0.py           — Older project version
- project2.5.py           — Intermediate project version
- project3.0.py           — Later project version
- project4.0.py           — Latest project version (recommended entrypoint)
- shoot_dragon.py         — Dragon shooting mechanics
- stars.py                — Starfield or visual element utilities
- template                — Additional template or resource file

## Requirements

- Python 3.8+ recommended
- No external dependencies are required by default (pure Python). If any specific library is needed by a script it will state so in its header comments.

## How to run

1. Clone the repository:

   git clone https://github.com/404sanchita/Are-You-Worthy.git
   cd Are-You-Worthy

2. Run the latest project version (recommended):

   python project4.0.py

   If you prefer an earlier version or a single feature, run one of the other scripts:

   - python maze.py
   - python mountain.py
   - python shoot_dragon.py

3. If a script requires input or shows an in-console UI, follow the on-screen prompts.

## Notes and Tips

- Many files are experimental and represent iterative versions; review the comments at the top of each file for details about usage and known limitations.
- Filenames with special characters or spaces (for example `maze & moun.py`) may be harder to run directly from some shells — rename them locally if needed.
- If you encounter errors, check the top of the script for any required imports or configuration values.

## Contributing

Contributions are welcome. Suggested ways to contribute:

- Open an issue describing a bug or enhancement
- Create a PR with a small, focused change
- Add a LICENSE file (if you want this project to be open source, consider MIT or similar)
- Add unit tests or README improvements

When submitting a PR, include a short description of what changed, why, and any testing steps.

## License

No license file is included in this repository. If you want others to reuse your code, add a LICENSE file (MIT is a common choice).

## Contact

Repository owner: 404sanchita

If you want help completing or reorganizing this project (adding a CLI, packaging, or tests), tell me what you want and I can add it or draft PR content.
