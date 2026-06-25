#!/usr/bin/env python3
"""Generate Cooja .csc with attacker motes (selective forwarding, rank anomaly).

Usage:
  python3 gen_csc_attack.py --attack selective_forwarding --out csc_attack/aer-attack-25-selective_forwarding.csc
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_csc_hybrid25 import hybrid_positions, EEPROM_B64


def attacker_configs(n_total: int, attack_type: str) -> dict[int, dict]:
    attackers: dict[int, dict] = {}
    if attack_type == "selective_forwarding":
        for i in [2, 5]:
            attackers[i] = {"role": "attacker", "attack": "selective_drop",
                            "drop_ratio": 0.5, "note": "drops 50% of forwarded packets"}
    elif attack_type == "rank_anomaly":
        for i in [3, 7]:
            attackers[i] = {"role": "attacker", "attack": "rank_decrease",
                            "rank_delta": -256, "note": "advertises artificially low rank"}
    elif attack_type == "mixed":
        attackers[2] = {"role": "attacker", "attack": "selective_drop",
                        "drop_ratio": 0.5}
        attackers[3] = {"role": "attacker", "attack": "rank_decrease",
                        "rank_delta": -256}
        attackers[5] = {"role": "attacker", "attack": "selective_drop",
                        "drop_ratio": 0.3}
    return attackers


def build_attack_csc(out_path: str, seed: int, attack_type: str, n_motes: int = 25,
                     sim_timeout_ms: int = 1800000,
                     success_ratio_tx: float = 0.85,
                     success_ratio_rx: float = 0.85,
                     tx_range: float = 35.0,
                     rx_range: float = 70.0) -> None:
    rng = random.Random(seed)
    positions = hybrid_positions(n_motes, rng)  # returns list of (x, y, z)
    atk_cfgs = attacker_configs(n_motes, attack_type)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<!DOCTYPE simconf SYSTEM "https://github.com/contiki-ng/cooja/raw/master/apps/simconf/simconf.dtd">\n'
    xml += '<simconf>\n'
    xml += '    <simulation>\n'
    xml += f'      <title>AER-MQoS {attack_type} (N={n_motes}, seed={seed})</title>\n'
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
        cfg = atk_cfgs.get(mote_id, {})
        role = cfg.get("role", "normal")
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
        if role == "attacker":
            attack = cfg.get("attack", "")
            if attack == "selective_drop":
                xml += f'      <description>attacker (selective drop {cfg.get("drop_ratio", 0.5)})</description>\n'
            elif attack == "rank_decrease":
                xml += f'      <description>attacker (rank anomaly {cfg.get("rank_delta", -256)})</description>\n'
        else:
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
    print(f"Wrote {out} ({attack_type}, N={n_motes}, seed={seed})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--attack", choices=["selective_forwarding", "rank_anomaly", "mixed"], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-motes", type=int, default=25)
    ap.add_argument("--seed", type=int, default=20260601)
    ap.add_argument("--sim-timeout-ms", type=int, default=1800000)
    ap.add_argument("--success-ratio-tx", type=float, default=0.85)
    ap.add_argument("--success-ratio-rx", type=float, default=0.85)
    args = ap.parse_args()
    build_attack_csc(args.out, args.seed, args.attack, args.n_motes,
                     args.sim_timeout_ms, args.success_ratio_tx, args.success_ratio_rx)
