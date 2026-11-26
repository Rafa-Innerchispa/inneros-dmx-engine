# Explicit control and physical verification

The local API rejects malformed JSON, arrays, null and oversized bodies. Color
requests require an explicit known target, supported color and integer brightness
(0–255). Scene requests require a named scene and finite bounded speed. Unknown
natural-language intents return 422 without selecting a default color or effect.
Do not send hand-escaped JSON through nested SSH shells: use a structured HTTP
client with `json={...}`.

Validation tests run against an ephemeral HTTP server with a mocked effects
runner; they never send Art-Net frames. HTTP success proves only acceptance of
the command. Art-Net UDP delivery does not establish that a luminaire lit or that
its physical address and channel mode match the profile.

The owner-observed November 26 test was partial: Peces green confirmed, Plantas
reported purple, Pulpos not illuminated. The Pulpos have fixture profiles but no
verified Home Assistant mains-switch mapping. Do not label these fixtures fully
operational, guess another relay, change physical addressing or scan raw channels.
Verify mains supply and each fixture's displayed DMX start address/channel mode
before correcting its profile. The four identified Kasa test outlets were restored
off and tested DMX targets received zero brightness after the observation.

Deployment must preserve the runtime checkout and current scene registry, back up
the previous API file, compare it to the approved base, install the reviewed main
file and restart only `inneros-dmx-engine.service`. Verify health and rejection of
an invalid command; do not use a valid lighting command as a deployment probe.
