# Wraith House

A Three.js horror game with Blender-built interiors and one Torch Survival mode. Solo play runs on static Vercel hosting. The new two-player co-op integration uses Supabase Auth, PostgreSQL and private Realtime channels. Online activation is pending a connected Supabase project; the committed configuration deliberately contains no credentials.

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
- One mode, **Torch Survival**, with 150 clue/item/ritual contracts. Player movement is 3× the previous base (15.6 m/s Ethan, 15 m/s Maya; sprint multiplier 1.7). Ghost speed is 5× the previous Investigation base (7.5 m/s), not literal light speed.
- Ghost contact within 0.85 m kills instantly, even if frozen. A stylized detached head falls and tumbles while the body collapses, followed by **“You are dead, dear.”**
- Aimed torch light is the only way to freeze the ghost. The light must reach it without a wall in between; the ghost itself can pass through walls. Every 10-second cycle has 9 seconds on and 1 second forcibly off. F cannot bypass the blackout. Sleep darts and wards are disabled.
- Email/password authentication, generated UUID player IDs, friend requests with accept/decline, private two-seat invitations, remote avatars, shared ghost, synchronized torch cycle and host mission/door state. Both players can freeze the same ghost. Online service setup is required below.
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
| 1 / 2 / 3 | EMF / torch switch / camera |
| F | Flashlight |
| V | First-person / third-person view |
| Escape | Release mouse; pauses solo, **does not pause co-op** |

Pick up the note on the sanctuary desk first. Find the named item in its room, then return to the pedestal outside the sanctuary. Use EMF (1 + R) at the pedestal to finish the ritual. In co-op the host carries/interacts with mission items and doors; the partner protects the team with their torch. The host starts/restarts rounds and continues contracts. Either player can die independently; returning to the foyer restarts both players. Host disconnection ends the session (no host migration). Progress/rewards remain local to the host browser, not a cloud-saved economy. Mobile touch controls are not implemented.

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

## Activate accounts and co-op

1. Connect the Supabase plugin to the account/project you want to use. Apply `online/schema.sql` once to that project. It creates game-specific tables and policies without changing unrelated tables.
2. In Supabase Authentication enable email/password sign-in, email confirmation, an appropriate email delivery service and rate limits; set the production Site URL and allowed confirmation redirect URL. Set the password minimum to 12 characters. The UI never stores or logs passwords; Supabase manages sessions/password hashing.
3. In Realtime settings disable **Allow public access**, so all channels require authorization. The migration supplies participant-only receive policies and per-sender write policies.
4. Fill `online/config.json` with the project URL and **publishable/anon** key. Never use a secret/service-role key. Browser-readable public keys rely on the included RLS policies.
5. Deploy the static site. Create and confirm two accounts, exchange the full player IDs, send/accept a friend request, invite the friend and join. Once both clients connect, the host enters the house; the guest then enters.

The host simulates the ghost and publishes world snapshots at 10 Hz; the guest publishes position, aim and torch state at 10 Hz. Private per-player channels prevent the guest from publishing on the host channel. This is cooperative, host-authoritative gameplay, not a competitive anti-cheat server. Latency can affect torch/contact timing. Rooms expire after 24 hours; leaving closes the room. Disconnects return players to the lobby. Do not advertise online availability until the actual configured deployment passes the two-account smoke test.

`tests/online-security.mjs` executes the migration in real embedded PostgreSQL (PGlite), testing consent, RLS, room limits, channel sender identity, anonymous rejection and packet validation:

```bash
npm install --prefix /tmp/wraith-qa three@0.180.0 @electric-sql/pglite@0.3.10
QA_DEPS=/tmp/wraith-qa/node_modules node tests/online-security.mjs
```

Local database and browser simulation tests do not verify production Supabase email delivery, WebSocket policy deployment or Vercel deployment. Those require the connected project.

`tests/online-client.cjs` drives two browser clients through login, ID exchange, friend acceptance, room invitation/join, snapshot exchange and leaving, using an explicitly simulated backend. Run with the same `QA_DEPS` and `CHROMIUM_PATH` as the rendering test. `tests/browser-smoke.cjs` also checks the death message and retry.
