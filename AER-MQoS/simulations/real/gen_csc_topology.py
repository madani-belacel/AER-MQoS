#!/usr/bin/env python3
"""Generate Cooja .csc for N-node topologies (supports 50, 100, etc.).

Usage:
  python3 gen_csc_topology.py --n-motes 50 --out csc_topology/aer-topology-50.csc
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_csc_hybrid25 import hybrid_positions, EEPROM_B64


def build_topology_csc(out_path: str, seed: int, n_motes: int = 50,
                       sim_timeout_ms: int = 1800000,
                       success_ratio_tx: float = 0.85,
                       success_ratio_rx: float = 0.85,
                       tx_range: float = 35.0,
                       rx_range: float = 70.0) -> None:
    rng = random.Random(seed)
    positions = hybrid_positions(n_motes, rng)  # returns list of (x, y, z)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<!DOCTYPE simconf SYSTEM "https://github.com/contiki-ng/cooja/raw/master/apps/simconf/simconf.dtd">\n'
    xml += '<simconf>\n'
    xml += '    <simulation>\n'
    xml += f'      <title>AER-MQoS topology N={n_motes} (seed={seed})</title>\n'
    xml += f'      <randomseed>{seed}</randomseed>\n'
    xml += f'      <motedelay_us>1000000</motedelay_us>\n'
    xml += '      <radiomedium>\n'
    xml += '        org.contikios.cooja.radiomediums.UDGM\n'
    xml += f'        <transmitting_range>{tx_range}</transmitting_range>\n'
    xml += f'        <interference_range>{rx_range}</interference_range>\n'
    xml += f'        <success_ratio_tx>{success_ratio_tx}</success_ratio_tx>\n'
    xml += f'        <success_ratio_rx>{success_ratio_rx}</success_ratio_rx>\n'
    xml += '      </radiomedium>\n'
    xml += '      <events>\n'
    xml += f'        <logoutput>{sim_timeout_ms}</logoutput>\n'
    xml += '      </events>\n'
    xml += '      <motetype>\n'
    xml += '        org.contikios.cooja.contikimote.ContikiMoteType\n'
    xml += '        <identifier>mtype0</identifier>\n'
    xml += '        <description>AER-MQoS campaign node</description>\n'
    xml += '        <source>[CONTIKI_DIR]/examples/AER-MQoS/AER-MQoS/code_source_AER_MQoS/AER-MQoS-node.c</source>\n'
    xml += '        <commands>$(MAKE) -j$(CPUS) AER-MQoS-node.cooja TARGET=cooja</commands>\n'
    xml += '        <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>\n'
    xml += '        <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>\n'
    xml += '        <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>\n'
    xml += '        <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>\n'
    xml += '        <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiEEPROM</moteinterface>\n'
    xml += '        <moteinterface>org.contikios.cooja.mote.moteinterfaces.LogMinimal</moteinterface>\n'
    xml += '        <moteinterface>org.contikios.cooja.mote.moteinterfaces.IPAddress</moteinterface>\n'
    xml += '      </motetype>\n'

    for mote_id in range(1, n_motes + 1):
        x, y, z = positions[mote_id - 1]
        xml += '    <mote>\n'
        xml += '      <interface_config>\n'
        xml += '        org.contikios.cooja.interfaces.Position\n'
        xml += f'        <x>{x:.6f}</x>\n'
        xml += f'        <y>{y:.6f}</y>\n'
        xml += f'        <z>{z}</z>\n'
        xml += '      </interface_config>\n'
        xml += '      <interface_config>\n'
        xml += '        org.contikios.cooja.contikimote.interfaces.ContikiMoteID\n'
        xml += f'        <id>{mote_id}</id>\n'
        xml += '      </interface_config>\n'
        xml += '      <interface_config>\n'
        xml += '        org.contikios.cooja.contikimote.interfaces.ContikiRadio\n'
        xml += '        <bitrate>250.0</bitrate>\n'
        xml += '      </interface_config>\n'
        xml += '      <interface_config>\n'
        xml += '        org.contikios.cooja.contikimote.interfaces.ContikiEEPROM\n'
        xml += f'        <eeprom>{EEPROM_B64}</eeprom>\n'
        xml += '      </interface_config>\n'
        xml += f'      <motetype_identifier>mtype0</motetype_identifier>\n'
        xml += '      <description>sensor mote</description>\n'
        xml += '    </mote>\n'

    xml += '    <motetype>\n'
    xml += '      org.contikios.cooja.contikimote.ContikiMoteType\n'
    xml += '      <identifier>mtype0</identifier>\n'
    xml += '      <description>AER-MQoS campaign node</description>\n'
    xml += '      <source>[CONTIKI_DIR]/examples/AER-MQoS/AER-MQoS/code_source_AER_MQoS/AER-MQoS-node.c</source>\n'
    xml += '      <commands>$(MAKE) -j$(CPUS) AER-MQoS-node.cooja TARGET=cooja</commands>\n'
    xml += '      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>\n'
    xml += '      <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>\n'
    xml += '      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>\n'
    xml += '      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>\n'
    xml += '      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiEEPROM</moteinterface>\n'
    xml += '      <moteinterface>org.contikios.cooja.mote.moteinterfaces.LogMinimal</moteinterface>\n'
    xml += '      <moteinterface>org.contikios.cooja.mote.moteinterfaces.IPAddress</moteinterface>\n'
    xml += '    </motetype>\n'
    xml += '  </simulation>\n'
    xml += '</simconf>\n'

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(xml)
    print(f"Wrote {out} (N={n_motes}, seed={seed})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-motes", type=int, default=50, help="Number of motes (50, 100, ...)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260601)
    ap.add_argument("--sim-timeout-ms", type=int, default=1800000)
    ap.add_argument("--success-ratio-tx", type=float, default=0.85)
    ap.add_argument("--success-ratio-rx", type=float, default=0.85)
    args = ap.parse_args()
    build_topology_csc(args.out, args.seed, args.n_motes, args.sim_timeout_ms,
                       args.success_ratio_tx, args.success_ratio_rx)
