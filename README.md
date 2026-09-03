# InnerOS DMX & Art-Net Engine (`inneros-dmx-engine`)

Módulo oficial de InnerOS para control, orquestación de iluminación escénica y domótica inteligente vía Art-Net / DMX, integrado con Home Assistant y la flota de agentes InnerOS.

---

## Especificaciones de Hardware y Red

* **Nodo Art-Net:** Pknight CR011R
* **IP del Nodo:** `192.168.1.10`
* **Puerto UDP:** `6454`
* **Universo:** `0` (Subnet: `0`, Net: `0`)
* **Home Assistant Server:** `http://192.168.1.4:8123`

---

## Mapeo de Luminarias (Universo 0)

| ID | Nombre | Canales Base | N° Canales | Tipo / Perfil |
|---|---|---|---|---|
| `pulpo_01` | Pulpo 1 (Eurolite EL-LMH1240WB) | 1 - 19 | 19 | Moving Head Spider 2-Bar RGBW |
| `beam_01` | Mini Beam 01 RGBW 12W | 20 - 25 | 6 | Dimmer + Strobe + RGBW Pinspot |
| `tacho_escalera` | Tacho Escalera (PAR 18x1W RGB) | 26 - 32 | 7 | Modo d (Dimmer + RGB + Strobe + Macro + Speed) |
| `tacho_peces` | Tacho Peces (PAR 18x1W RGB) | 33 - 39 | 7 | Modo d (Dimmer + RGB + Strobe + Macro + Speed) |
| `tacho_central` | Tacho Central (PAR RGBW + SMD) | 40 - 47 | 8 | Modo A (Dimmer + RGBW + Flash SMD Ring) |
| `tacho_plantas` | Tacho Plantas (PAR 18x1W RGB) | 48 - 54 | 7 | Modo d (Dimmer + RGB + Strobe + Macro + Speed) |
| `bola_disco` | Crystal Magic Ball Disco | 55 - 62 | 8 | Modo A (Dimmer + RGB + Strobe + Motor Rotación) |
| `beam_02` | Mini Beam 02 RGBW 12W | 63 - 68 | 6 | Dimmer + Strobe + RGBW Pinspot |
| `pulpo_02` | Pulpo 2 (Eurolite EL-LMH1240WB) | 69 - 87 | 19 | Moving Head Spider 2-Bar RGBW |

---

## Estructura del Proyecto

```
inneros-dmx-engine/
├── config/
│   └── fixtures.json
├── homeassistant/
│   ├── ha_artnet_configuration.yaml
│   ├── groups.yaml
│   └── automations.yaml
├── src/
│   ├── __init__.py
│   ├── artnet_controller.py
│   ├── fixture_profiles.py
│   ├── ha_bridge.py
│   └── cli.py
├── tests/
│   └── test_dmx.py
└── README.md
```

---

## Uso CLI Directo

```bash
# Listar luminarias registradas
python3 -m src.cli list

# Ejecutar escena Fiesta / Disco
python3 -m src.cli party

# Fijar color uniforme (RGBW)
python3 -m src.cli color --r 0 --g 255 --b 200 --brightness 255

# Blackout general
python3 -m src.cli blackout

# Probar luminaria individual
python3 -m src.cli test beam_01
```

---

## Integración con Home Assistant

1. Copiar `homeassistant/ha_artnet_configuration.yaml` al `/config/configuration.yaml` de tu Home Assistant en `192.168.1.4`.
2. Reiniciar Home Assistant.
3. Las entidades quedarán agrupadas en:
   * `light.grupo_tachos`
   * `light.grupo_beams`
   * `light.grupo_pulpos_led`
   * `light.todas_las_luces_disco`
