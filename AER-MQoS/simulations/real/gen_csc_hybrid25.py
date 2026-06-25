#!/usr/bin/env python3
"""
Generate a Cooja .csc: hybrid topology (partial grid + controlled random
dispersion), N motes, single Contiki motetype (AER-MQoS-node.c).

Example:
  python3 gen_csc_hybrid25.py --out aer-real-25-hybrid-20260601.csc
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

# Same as other project templates (default Cooja EEPROM).
EEPROM_B64 = (
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=="
)

DEFAULT_SOURCE = (
    "[CONTIKI_DIR]/examples/AER-MQoS/AER-MQoS/code_source_AER_MQoS/AER-MQoS-node.c"
)
DEFAULT_MAKE = "$(MAKE) -j$(CPUS) AER-MQoS-node.cooja TARGET=cooja"


def dist2(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def hybrid_positions(n: int, rng: random.Random) -> list[tuple[float, float, float]]:
    if n < 3:
        raise SystemExit("need at least 3 motes")

    pts: dict[int, tuple[float, float]] = {}
    # 1: RPL root (Cooja node_id = 1), central zone for global connectivity.
    pts[1] = (175.0, 175.0)

    # 2..min(9,n): ring around the root.
    last_ring = min(9, n)
    ring_count = max(0, last_ring - 1)
    for i in range(2, last_ring + 1):
        k = i - 2
        ang = 2.0 * math.pi * k / max(1, ring_count) + rng.uniform(-0.18, 0.18)
        rad = 36.0 + rng.uniform(-3.0, 10.0)
        pts[i] = (175.0 + rad * math.cos(ang), 175.0 + rad * math.sin(ang))

    remaining = [i for i in range(1, n + 1) if i not in pts]
    # 3x3 grid with jitter (bottom-left corner), up to 9 nodes.
    grid_ids = remaining[: min(9, len(remaining))]
    gi = 0
    for row in range(3):
        for col in range(3):
            if gi >= len(grid_ids):
                break
            nid = grid_ids[gi]
            x = 28.0 + col * 50.0 + rng.uniform(-9.0, 9.0)
            y = 22.0 + row * 46.0 + rng.uniform(-9.0, 9.0)
            pts[nid] = (x, y)
            gi += 1
        if gi >= len(grid_ids):
            break

    placed = list(pts.values())
    min_sep = 20.0
    for nid in range(1, n + 1):
        if nid in pts:
            continue
        for _ in range(400):
            x = rng.uniform(15.0, 310.0)
            y = rng.uniform(15.0, 310.0)
            if all(dist2((x, y), q) >= min_sep for q in placed):
                pts[nid] = (x, y)
                placed.append((x, y))
                break
        else:
            x = 15.0 + (nid % 11) * 27.0
            y = 260.0 + (nid % 5) * 12.0
            pts[nid] = (x, y)
            placed.append((x, y))

    return [(pts[i][0], pts[i][1], 0.0) for i in range(1, n + 1)]


def emit_csc(
    nodes: int,
    seed: int,
    source_rel: str,
    make_cmd: str,
    out: Path,
    mtype_id: str,
    sim_timeout_ms: int,
    success_ratio_tx: float = 1.0,
    success_ratio_rx: float = 1.0,
    tx_range: float = 35.0,
    rx_range: float = 70.0,
) -> None:
    rng = random.Random(seed)
    coords = hybrid_positions(nodes, rng)

    mote_blocks = []
    for i, (x, y, z) in enumerate(coords):
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
    <title>Hybrid Cooja campaign — {nodes} motes hybrid seed={seed} sr_tx={success_ratio_tx} sr_rx={success_ratio_rx} | ScriptRunner TIMEOUT={sim_timeout_ms} ms sim time</title>
    <randomseed>{seed}</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>{tx_range}</transmitting_range>
      <interference_range>{rx_range}</interference_range>
      <success_ratio_tx>{success_ratio_tx}</success_ratio_tx>
      <success_ratio_rx>{success_ratio_rx}</success_ratio_rx>
    </radiomedium>
    <events>
      <logoutput>40000</logoutput>
    </events>
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <identifier>{mtype_id}</identifier>
      <description>Multi-protocol RPL campaign node (AER_PROTOCOL_VARIANT in Makefile)</description>
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
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <script>TIMEOUT({sim_timeout_ms}, log.testOK());
while(true){{if(typeof msg===&apos;string&apos;&amp;&amp;msg.indexOf(&apos;METRIC,&apos;)===0){{log.append(&apos;@@METRICS_PATH@@&apos;,msg+&apos;\\n&apos;);}}YIELD();}}</script>
      <active>true</active>
    </plugin_config>
    <width>600</width>
    <z>5</z>
    <height>200</height>
    <location_x>420</location_x>
    <location_y>420</location_y>
  </plugin>
</simconf>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(xml, encoding="utf-8")
    print("Wrote", out.resolve())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--nodes", type=int, default=25, help="Nombre de motes (25–49)")
    p.add_argument("--seed", type=int, default=20260601)
    p.add_argument("--source", default=DEFAULT_SOURCE)
    p.add_argument("--commands", default=DEFAULT_MAKE)
    p.add_argument("--mtype", default="mtype_aer_real_hybrid")
    p.add_argument("--sim-timeout-ms", type=int, default=1_800_000, help="ScriptRunner TIMEOUT() in ms of simulation time (default 1800000 = 1800 s)")
    p.add_argument(
        "--success-ratio-tx",
        type=float,
        default=1.0,
        help="UDGM success_ratio_tx (1.0 = lossless; 0.85 typical lossy stress)",
    )
    p.add_argument(
        "--success-ratio-rx",
        type=float,
        default=None,
        help="UDGM success_ratio_rx (defaults to --success-ratio-tx)",
    )
    p.add_argument("--tx-range", type=float, default=35.0, help="UDGM transmitting_range in meters (default 35)")
    p.add_argument("--rx-range", type=float, default=70.0, help="UDGM interference_range in meters (default 70)")
    p.add_argument("--out", type=Path, default=Path("aer-real-25-hybrid-20260601.csc"))
    args = p.parse_args()
    sr_rx = args.success_ratio_rx if args.success_ratio_rx is not None else args.success_ratio_tx
    if not (25 <= args.nodes <= 49):
        print("Warning: expected 25–49 nodes for publication template", file=sys.stderr)
    emit_csc(
        args.nodes,
        args.seed,
        args.source,
        args.commands,
        args.out,
        args.mtype,
        args.sim_timeout_ms,
        args.success_ratio_tx,
        sr_rx,
        args.tx_range,
        args.rx_range,
    )


if __name__ == "__main__":
    main()
