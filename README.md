# Wraith House

A single-player browser horror prototype built with Three.js. Static Vercel hosting; no backend or environment variables required. Import the repository with preset **Other**, empty build command and root output directory (`.`). A previous automatic Vercel deployment was blocked; GitHub push success does not imply deployment success.

[Import into Vercel](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fdev-shubh-madara%2Fghost-game)

## Current game

- **Two 1,000 × 1,000 metre floors**, world coordinates -500 to +500 on X/Z. Nearby 40m sectors are streamed as instanced geometry, with at most 25 active sectors. This is a repeated procedural environment, not two square kilometres of individually authored scenery.
- Walk up/down the central stair flight. **Space jumps**. Stairs require no E interaction or teleportation. Gravity, landings, ceiling checks and collapsing rotten boards are implemented.
- **Safe start:** no ghost during the first 60 seconds of active gameplay. The sanctuary within 22m of the spawn remains protected on both floors forever. Returning hides/removes the threat; leaving after the grace period respawns it 20m farther from the sanctuary. Retry grants a fresh grace period.
- The ghost deliberately ignores walls and can move vertically between floors.
- Each contract requires **hint pickup → find named item → pick up item → use it for the objective**. Press E near the sanctuary desk to collect a note. The journal records the item name, floor, sector and coordinates; an objective marker and distance guide the search. Return the item to the ritual pedestal outside the sanctuary.
- Five modes, 150 generated contract steps per mode. Investigation uses an EMF scan; Nightmare requires a nearby apparition photo; Exorcism/Rescue consume the required item; Hardcore starts a timed hunt. These reuse mechanics and are not 750 handcrafted missions.
- Standard EMF, camera and 30-second sleep dart; healing, salt-ward and permanent torch-upgrade purchases. Coins/inventory/completed progress persist locally. The current note/item stage resets when the page reloads.
- Reward guards, failure/retry, sanity, stamina, flashlight, synthesized sounds and keyboard/mouse controls.

## Controls

| Control | Action |
| --- | --- |
| WASD / mouse | Move / look |
| Shift | Sprint |
| Space | Jump |
| E | Pick up notes/items, use an item at the pedestal, interact with doors |
| R or left mouse | Use selected equipment |
| 1 / 2 / 3 | EMF / sleep dart / camera |
| F | Flashlight |
| H / Q | Consume healing injector / salt ward |
| V | First-person / third-person view |
| Escape | Pause and release mouse |

## Characters and Blender — status

The supplied male/female reference images are the selection portraits. Runtime fallbacks include a pale long-haired ghost with a dress, olive-clothed investigator meshes and first-person sleeves/hands. **These are procedural stand-ins, not photoreal reconstructions of the references.** The third-person fallback has simple limb motion; it is not a professional rig.

Laptop access was not connected during this update. No laptop access, Blender execution, generated GLB files or completed photoreal models are claimed.

`blender/build_reference_characters.py` creates separate new Blender scenes and exports starter ghost/Ethan/Maya meshes. It does not delete the user's existing scene. It is a starting point for sculpting, UV work, materials and rigging, not an automatic photoreal reconstruction tool. Run from the repository root in an authorized Blender environment:

```bash
blender --background --python blender/build_reference_characters.py -- --output models
```

The script writes `ghost.glb`, `ethan.glb`, `maya.glb`, a `.blend` file and enables `models/manifest.json` only after all exports succeed. The browser loads these files through GLTFLoader when enabled, otherwise it keeps the fallbacks. Review the exported appearance before pushing enabled assets. The script passed Python syntax checks but has not been run in Blender here. The older house-builder script is retained as a historical small blockout and does not define the runtime kilometre-scale world.

## Local run and validation

```bash
python -m http.server 8000
```

Open http://localhost:8000 in a desktop browser with WebGL2 and pointer lock. Internet access is required for pinned Three.js 0.180.0 modules from jsDelivr. Mobile touch controls and multiplayer are not implemented.

The gameplay regression suite uses actual Three.js geometry/math with stubbed rendering/browser APIs. It checks initialization, WASD, kilometre boundaries, stairs up/down, jump/landing, objective sequencing and reward protection, grace period and sanctuary enforcement on both floors, bounded chunk streaming, and corrupt-save recovery. Obtain `three@0.180.0/build/three.core.js` and save it as `/tmp/three.core.mjs`:

```bash
THREE_CORE=/tmp/three.core.mjs node tests/game-regression.mjs
```

A headless Chromium WebGL smoke test also passed module initialization, pointer lock, note pickup, movement, jumping, view switching and a hidden ghost at spawn with no JavaScript errors. Screenshots were inspected; the test served the same pinned Three.js modules locally because the browser could not fetch the CDN from this environment. This does not certify performance on every GPU. World repetition, modest starter meshes and synthesized effects remain production limitations.
