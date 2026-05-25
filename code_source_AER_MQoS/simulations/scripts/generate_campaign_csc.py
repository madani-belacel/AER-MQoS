#!/usr/bin/env python3
"""
Generate a Cooja .csc with N Contiki motes (single firmware type) on a grid + jitter.
Edit <title>, <randomseed>, and simulation duration in Cooja UI (target 1800--3600 s).

Usage:
  python3 generate_campaign_csc.py --nodes 30 --seed 20260513 \\
    --out ../cooja/aer-campaign-grid-30.csc
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

EEPROM_B64 = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=="
)


def grid_positions(n: int, spacing: float, jitter: float, rng: random.Random):
    """Rough grid with optional jitter; first mote at center-ish (root)."""
    cols = max(1, int(math.ceil(math.sqrt(n))))
    rows = max(1, int(math.ceil(n / cols)))
    positions = []
    for i in range(n):
        row, col = divmod(i, cols)
        x = 20.0 + col * spacing + rng.uniform(-jitter, jitter)
        y = 20.0 + row * spacing + rng.uniform(-jitter, jitter)
        positions.append((x, y, 0.0))
    return positions


def emit_csc(nodes: int, seed: int, source_rel: str, make_cmd: str, out: Path):
    rng = random.Random(seed)
    positions = grid_positions(nodes, spacing=45.0, jitter=6.0, rng=rng)
    mtype_id = "mtype_aer_campaign"

    mote_blocks = []
    for i, (x, y, z) in enumerate(positions):
        mote_blocks.append(
            f"""    <mote>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>{x:.6f}</x>
        <y>{y:.6f}</y>
        <z>{z}</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>{i + 1}</id>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiRadio
        <bitrate>250.0</bitrate>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiEEPROM
        <eeprom>{EEPROM_B64}</eeprom>
      </interface_config>
      <motetype_identifier>{mtype_id}</motetype_identifier>
    </mote>"""
        )

    timeline_motes = "\n".join(f"      <mote>{i}</mote>" for i in range(nodes))

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<simconf>
  <simulation>
    <title>AER-MQoS campaign grid ({nodes} motes, seed={seed}) — set duration 1800--3600s in Cooja</title>
    <randomseed>{seed}</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>55.0</transmitting_range>
      <interference_range>110.0</interference_range>
      <success_ratio_tx>1.0</success_ratio_tx>
      <success_ratio_rx>1.0</success_ratio_rx>
    </radiomedium>
    <events>
      <logoutput>40000</logoutput>
    </events>
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <identifier>{mtype_id}</identifier>
      <description>AER-MQoS node (same firmware all motes)</description>
      <source>{source_rel}</source>
      <commands>{make_cmd}</commands>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiVib</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRS232</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiBeeper</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiIPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiButton</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiPIR</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiClock</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiLED</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiCFS</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiEEPROM</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
    </motetype>
{chr(10).join(mote_blocks)}
  </simulation>
  <plugin>
    org.contikios.cooja.plugins.SimControl
    <width>280</width>
    <z>4</z>
    <height>160</height>
    <location_x>400</location_x>
    <location_y>0</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.Visualizer
    <plugin_config>
      <moterelations>true</moterelations>
      <skin>org.contikios.cooja.plugins.skins.IDVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.UDGMVisualizerSkin</skin>
      <viewport>1.0 0.0 0.0 1.0 0.0 0.0</viewport>
    </plugin_config>
    <width>400</width>
    <z>3</z>
    <height>400</height>
    <location_x>1</location_x>
    <location_y>1</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
      <filter />
      <formatted_time />
      <coloring />
    </plugin_config>
    <width>1179</width>
    <z>1</z>
    <height>704</height>
    <location_x>679</location_x>
    <location_y>0</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.TimeLine
    <plugin_config>
{timeline_motes}
      <showRadioRXTX />
      <showRadioHW />
      <showLEDs />
      <zoomfactor>1.5</zoomfactor>
    </plugin_config>
    <width>1858</width>
    <z>0</z>
    <height>166</height>
    <location_x>9</location_x>
    <location_y>723</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.RadioLogger
    <plugin_config>
      <split>150</split>
      <formatted_time />
      <showdups>false</showdups>
      <hidenodests>false</hidenodests>
    </plugin_config>
    <width>500</width>
    <z>2</z>
    <height>300</height>
    <location_x>19</location_x>
    <location_y>409</location_y>
  </plugin>
</simconf>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(xml, encoding="utf-8")
    print("Wrote", out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--nodes", type=int, default=30, help="Number of motes (25--49 typical)")
    p.add_argument("--seed", type=int, default=20260513)
    p.add_argument(
        "--source",
        default="[CONTIKI_DIR]/examples/projet_madani/AER-MQoS/code_source_AER_MQoS/AER-MQoS-node.c",
    )
    p.add_argument(
        "--commands",
        default="$(MAKE) -j$(CPUS) AER-MQoS-node.cooja TARGET=cooja",
    )
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if not (25 <= args.nodes <= 49):
        print("Warning: expected 25--49 nodes for campaign; got", args.nodes, file=sys.stderr)
    emit_csc(args.nodes, args.seed, args.source, args.commands, args.out)


if __name__ == "__main__":
    main()
