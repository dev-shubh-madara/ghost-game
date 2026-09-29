# Wraith House

Single-player Three.js horror prototype, served as a static site on Vercel.

[Deploy with Vercel](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fdev-shubh-madara%2Fghost-game)

Import this repository, select **Other**, leave the build command empty, and serve the repository root (`.`). No environment variables or backend are required. Three.js 0.180.0 loads from jsDelivr, so internet access is required. A Vercel account and the final Deploy action are still required.

## Play

Run `python -m http.server 8000`, then open http://localhost:8000 in a desktop browser with WebGL2 and pointer lock. Click Enter the House to capture the mouse. Escape pauses; click Enter to resume.

| Control | Action |
| --- | --- |
| WASD / mouse | Move / look |
| Shift | Sprint |
| F | Flashlight |
| E | Stairs, doors, marked objects and seals |
| 1 / 2 / 3 | EMF / sleep dart / camera |
| Space | Use selected equipment |
| H / Q | Consume a healing injector / salt ward |
| Escape | Pause and release mouse |

## Implemented

- Two floors, interactive stair transfer, doors, furniture, architectural details, fog, shadows and bloom.
- Corrected movement with independent key defaults, wall/prop collision and cleared inputs on focus loss.
- Scene-attached flashlight and permanent torch upgrade.
- Ghost pursuit, sanity, fear, stamina, failure and retry. The supernatural entity can phase through walls.
- Real opening beneath rotten boards; collapsing boards and player fall with sanity damage.
- Five modes with 150 generated contract steps each. These reuse five objective mechanics, not 750 handcrafted missions. Modes change task sequences and chase speed.
- Marked EMF scans, cursed-object retrieval and seal restoration; aimed, unobstructed entity photographs; timed survival.
- Guarded +100-coin rewards. Separate mode progress, inventory and coins persist in browser localStorage. Invalid saved values are sanitized.
- EMF, camera and sleep dart as standard tools. Dart disables the ghost for 30 seconds with a 35-second cooldown.
- Working purchases: healing injector (200 coins), 12-second salt ward (250), permanent flashlight upgrade (400).
- Synthesized footstep, equipment and event sounds.

## Honest scope

This is a procedural browser prototype, not a finished AAA game. Investigator selections provide gameplay traits; there are no rigged human character models. Multiplayer, mobile touch controls, final audio, custom GLB characters and the remaining equipment concepts are not implemented. The store does not sell unimplemented concepts.

`blender/haunted_house_builder.py` remains a starter blockout script. Blender was not available during this update, and no Blender execution or finished Blender assets are claimed. Production assets require modelling, materials, rigging, animation and GLB integration.

Old coin balances migrate into the versioned save. Old generic objective progress is not migrated because the objective mechanics changed. Browser storage is local to the origin and is not a secure online economy. The explicit one-click Vercel link creates a project; it does not mean a deployment has already occurred.

## Verification

JavaScript syntax and the regression test passed during this update. The regression test initializes the game with actual Three.js math/geometry and stubbed browser/rendering APIs, then checks movement, collisions, flashlight attachment, mission count, reward guards and save recovery. It is not a visual or GPU test. The browser binary download failed in the development environment, so visual browser validation remains outstanding.

To repeat the regression test, obtain `three@0.180.0/build/three.core.js`, save it as `/tmp/three.core.mjs`, then run:

```bash
THREE_CORE=/tmp/three.core.mjs node tests/game-regression.mjs
```
