# Wraith House — Web 3D prototype

This project upgrades the earlier 2.5D demo into a real WebGL/Three.js first-person ghost-hunt prototype.

## Included
- Real 3D WebGL scene with a two-floor haunted building blockout.
- First-person mouse look + WASD + sprint.
- Dynamic flashlight, shadows, fog, ACES tone mapping and bloom.
- Second-floor rotten-board break sequence with falling board physics animation and ghost alert.
- Ghost AI chase/sleep behavior using the provided ghost image as a temporary 3D billboard.
- Male/female investigator selection using the supplied character images as UI portraits.
- 5 game modes, 120 generated contract steps each (600 total mission steps).
- 100-coin mission rewards, persistent localStorage economy.
- 52 tools in the equipment store; EMF, sleep dart and spirit camera have prototype gameplay behavior.
- Vercel-compatible static structure.
- `blender/haunted_house_builder.py`: Blender 4.x blockout-generation script with named breakable boards and export structure.

## Important production limitation
Blender itself is not installed in the execution environment that produced this project. Therefore the included Blender script was prepared but could not be executed here to generate final `.blend`/`.glb` assets. The browser currently uses procedural Three.js geometry for the building. The supplied character photos are not sufficient to create production-quality rigged 3D humans automatically; final characters require proper 3D models, UVs, materials, rigs and animations.

## Run locally
Because the code uses ES modules, serve it over HTTP instead of double-clicking index.html:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Deploy to Vercel
1. Put this folder in a GitHub repository.
2. Import that repository into Vercel.
3. Framework preset: `Other`.
4. Build command: leave empty.
5. Output directory: `.`
6. Deploy.

## Blender pipeline for the production version
1. Open Blender 4.x.
2. Run `blender/haunted_house_builder.py` from the Scripting workspace.
3. Replace the blockout with detailed meshes; use PBR materials and UVs.
4. Create/obtain properly licensed male/female 3D character models and a rigged ghost model.
5. Add walk/run/crouch/interaction/attack/hunt animations.
6. Export optimized GLB files into `models/`.
7. Integrate them through Three.js `GLTFLoader` and retain low-poly collision proxies.
8. For true multiplayer, add an authoritative WebSocket game server. Vercel can host the web frontend, but a continuously connected realtime game server is normally deployed separately.

## Controls
- WASD — move
- Mouse — look
- Shift — sprint
- F — flashlight
- E — interact / stairs / collect evidence
- 1/2/3 — select tool
- Space — use selected tool
