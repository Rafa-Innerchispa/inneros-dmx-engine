# Persistent local DMX service

The Intel user unit `inneros-dmx-engine.service` serves the existing loopback API at port 18796 and sends Art-Net to the configured Pknight node. It is separate from the Home Assistant `flux_led` Zengge RGB integration and from Kasa outlet power control.

The November 24 inspection found the running process still using a deleted temporary execution worktree. HTTP status could remain healthy while a future restart would fail and file-backed scene lookup would lose its source. A persistent checkout under `/home/rlopez/inneros/inneros_core/workspaces/inneros-dmx-engine` replaces that path. The recovery used source commit `884c5c54ee3cf057e361211efe105f27f1ce2829`; 14 tests passed with Art-Net directed to loopback. The restart was performed only after the existing engine reported no effect running.

Install `infra/systemd/99-stable-source.conf` in the existing user unit's drop-in directory. It changes only WorkingDirectory; retain the installed loopback bind, port, node address and universe. Preserve the prior unit and a recoverable checkout of its prior source before restart. Rollback should point to the recovered prior checkout, not to the deleted path. Do not run a second controller or overwrite unrelated services using another port.

After restart, verify the process working directory exists and `/api/status` responds with the fixture count and scene catalog. This demonstrates API readiness, not physical light output. Perform a separately observed low-intensity color test with the intended Kasa outlets powered; a successful UDP send is not a fixture acknowledgment.
