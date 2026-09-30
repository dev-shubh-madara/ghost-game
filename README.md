# Wraith House

A single-player Three.js horror game prototype with Blender-built interiors. Static Vercel hosting; no backend or environment variables required.

[Import into Vercel](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fdev-shubh-madara%2Fghost-game)

Use framework preset **Other**, empty build command, and root output directory (`.`). GitHub pushes trigger a deployment only if the connected Vercel project allows the commit. A prior deployment was blocked by Vercel; successful code delivery is not proof of a live deployment.

## Included in this update

- **Blender 4.3.2 was actually executed** to create/export the room kit and starter character meshes. Both editable `.blend` files and browser `.glb` assets are committed.
- Two 1,000 × 1,000 metre floors. Each has 625 sectors and four enclosed rooms per sector: **2,500 rooms per floor / 5,000 total**. These repeat six furnished templates, not 5,000 individually designed rooms.
- Bedroom, library, infirmary, dining room, nursery and ritual room templates with 1.9m entrances, walls, paneled ceilings, wood floors, trim, furniture, lamps and debris.
- Colour, roughness and normal maps, instanced room geometry, fog, bloom, screen-space ambient occlusion and flashlight shadows.
- Blender ghost and investigator models load by default. These are stylized starter models inspired by the references, not photoreal likenesses or professional animated rigs. Reference images remain the selection portraits.
- Walkable stairs, jumping, gravity and collapsing boards. No E teleport is used for stairs.
- A 60-second ghost-free introduction and a permanently protected sanctuary on both floors. The ghost can phase through walls outside the sanctuary.
- Hint pickup → named-item search → item pickup → objective completion. The journal gives the floor, room type, sector and coordinates. Items require the correct floor.
- Five modes with 150 generated contracts each, coins, three standard tools, consumable purchases, a torch upgrade, sanity/stamina and failure/retry.
- First/third-person views and synthesized footsteps/equipment sounds. Progress, coins and inventory persist in browser localStorage; the current contract's item stage resets on reload.

## Graphics presets

| Preset | Nearby sectors | Maximum loaded rooms | Ambient occlusion | Flashlight shadow |
| --- | ---: | ---: | --- | ---: |
| Balanced | 3 × 3 | 72 | Off | 1024 px |
| High | 5 × 5 | 200 | On | 2048 px |
| Ultra | 5 × 5 | 200 | On | 4096 px |

High is the default. Balanced disables bloom and reduces the pixel-ratio cap. Ultra raises the pixel-ratio cap and shadow resolution. There is **no measured RTX 3050 minimum specification or FPS guarantee**. Test on the target hardware before setting minimum requirements. This is not a commercial AAA production; the world repeats templates and character rigs/animations remain basic.

## Controls

| Control | Action |
| --- | --- |
| WASD / mouse | Move / look |
| Shift | Sprint |
| Space | Jump |
| E | Pick up hints/items; use an item at the ritual pedestal |
| R or left mouse | Use selected equipment |
| 1 / 2 / 3 | EMF / sleep dart / camera |
| F | Flashlight |
| H / Q | Consume healing injector / salt ward |
| V | First-person / third-person view |
| Escape | Pause and release mouse |

Pick up the note on the sanctuary desk first. Find the named item in its room, then return to the pedestal outside the sanctuary. Investigation requires an EMF scan; Nightmare requires a nearby apparition photo; Exorcism/Rescue use the item; Hardcore starts a timed hunt. Other equipment concepts are not sold as functioning tools. Multiplayer and mobile touch controls are not implemented.

## Run locally

```bash
python -m http.server 8000
```

Open http://localhost:8000 in a desktop WebGL2 browser. Three.js 0.180.0 modules load from jsDelivr, so internet access is required. No production npm install is necessary.

## Blender source and rebuild

- `models/haunted-rooms.blend`: editable six-template room kit. Templates intentionally overlap at the origin; isolate the named object to inspect one room.
- `models/wraith_character_starters.blend`: separate scenes for the three starter characters.
- `blender/build_room_kit.py`: room geometry and PBR-map generation.
- `blender/build_reference_characters.py`: character generation/export.
- `artifacts/blender-bedroom-preview.png`: a Blender Cycles render; lighting differs from the browser.

From the repository root:

```bash
blender --background --factory-startup --python blender/build_room_kit.py
blender --background --factory-startup --python blender/build_reference_characters.py -- --output models
```

The browser accepts the uncompressed Blender exports. The committed GLBs were additionally optimized with glTF-Transform 4.2.1 and Meshoptimizer 0.22.0. To repeat that optional optimization:

```bash
npm install --prefix blender
node blender/optimize_assets.mjs
```

The legacy `haunted_house_builder.py` remains a historical small blockout and does not define the runtime world.

## Validation

`tests/game-regression.mjs` uses actual Three.js geometry/math and stubbed rendering to check WASD, boundaries, room doors/walls, stairs in both directions, jumping/landing, mission ordering, reward guards, the sanctuary and bounded streaming. Set `THREE_CORE` to an installed `three@0.180.0/build/three.core.js`:

```bash
THREE_CORE=/path/to/three/build/three.core.js node tests/game-regression.mjs
```

`tests/browser-smoke.cjs` runs a headless Chromium WebGL check using the same pinned Three.js modules served locally. It checks Blender asset decoding, the six templates, character loading, pointer lock, hint pickup and Balanced/High rendering. It requires Playwright plus `QA_DEPS` pointing to a node_modules folder with three 0.180.0 and @sparticuz/chromium 133.0.0. `CHROMIUM_PATH` can override the browser executable. This is a functional rendering check, not a hardware performance benchmark.

`artifacts/asset-validation.json` records asset sizes and SHA-256 hashes. Browser captures are available in `artifacts/`.
