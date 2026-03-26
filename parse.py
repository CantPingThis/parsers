#!/usr/bin/env python3
"""
Test script for cisco_9800_show_ap_uptime.textfsm
Paste your own 'show ap uptime' output between the triple quotes in SAMPLE_OUTPUT.
"""

import textfsm
import os

# ─────────────────────────────────────────────────────────────────────────────
# Paste your own "show ap uptime" output here
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_OUTPUT = """
Number of APs: 6

AP Name                          Ethernet MAC    Radio MAC       AP Up Time                              Association Up Time
----------------------------------------------------------------------------------------------------------------------
AP3800-r2sw1-te1-0-8             0042.68a0.fc4a  0062.ecf3.8310  26 days 0 hour 57 minutes 41 seconds    15 days 1 hour 50 minutes 4 seconds
9130i-r2sw1-te2015               04eb.409e.1724  04eb.409f.1f80  9 days 3 hours 26 minutes 48 seconds    9 days 3 hours 24 minutes 24 seconds
9120i-r4-sw2-te1-0-39            d4e8.8019.60e8  d4e8.801a.3340  8 days 1 hour 36 minutes 57 seconds     8 days 1 hour 33 minutes 49 seconds
SS-I-1                           7069.5a74.7a50  7069.5a78.7780  26 days 0 hour 54 minutes 57 seconds    22 minutes 15 seconds
9130i-r3-sw2-g1-0-10             04eb.409e.1d28  04eb.409f.4fa0  3 days 5 hours 12 minutes 30 seconds    1 hour 45 minutes 10 seconds
AP-recently-rebooted             aabb.ccdd.ee11  aabb.ccdd.ee22  2 hours 10 minutes 5 seconds            1 hour 55 minutes 3 seconds
"""

# ─────────────────────────────────────────────────────────────────────────────
# Locate the template file (same directory as this script by default)
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(SCRIPT_DIR, "cisco_9800_show_ap_uptime.textfsm")

def to_seconds(days, hours, minutes, seconds):
    """Convert uptime components to total seconds for easy comparison."""
    return (int(days or 0) * 86400 +
            int(hours or 0) * 3600 +
            int(minutes or 0) * 60 +
            int(seconds or 0))

def format_uptime(days, hours, minutes, seconds):
    """Format uptime components into a readable string."""
    parts = []
    if days:   parts.append(f"{days}d")
    if hours:  parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    if seconds: parts.append(f"{seconds}s")
    return " ".join(parts) if parts else "0s"


def main():
    # Parse
    with open(TEMPLATE_FILE) as f:
        template = textfsm.TextFSM(f)
    results = template.ParseTextToDicts(SAMPLE_OUTPUT)

    if not results:
        print("No APs parsed. Check that your output matches the expected format.")
        return

    print(f"{'AP Name':<40} {'Ethernet MAC':<18} {'AP Uptime':<22} {'Assoc Uptime':<22} {'Status'}")
    print("-" * 120)

    flapping = []
    for ap in results:
        ap_secs    = to_seconds(ap['AP_UP_DAYS'], ap['AP_UP_HOURS'], ap['AP_UP_MINUTES'], ap['AP_UP_SECONDS'])
        assoc_secs = to_seconds(ap['ASSOC_UP_DAYS'], ap['ASSOC_UP_HOURS'], ap['ASSOC_UP_MINUTES'], ap['ASSOC_UP_SECONDS'])

        ap_str    = format_uptime(ap['AP_UP_DAYS'], ap['AP_UP_HOURS'], ap['AP_UP_MINUTES'], ap['AP_UP_SECONDS'])
        assoc_str = format_uptime(ap['ASSOC_UP_DAYS'], ap['ASSOC_UP_HOURS'], ap['ASSOC_UP_MINUTES'], ap['ASSOC_UP_SECONDS'])

        # Flag if AP has been up > 1h but CAPWAP tunnel is < 1h old
        if ap_secs > 3600 and assoc_secs < 3600:
            status = "⚠️  CAPWAP FLAP"
            flapping.append(ap['AP_NAME'])
        else:
            status = "✅ OK"

        print(f"{ap['AP_NAME']:<40} {ap['ETHERNET_MAC']:<18} {ap_str:<22} {assoc_str:<22} {status}")

    print(f"\nTotal APs parsed: {len(results)}")

    if flapping:
        print(f"\n⚠️  {len(flapping)} AP(s) with recent CAPWAP tunnel flap:")
        for name in flapping:
            print(f"   - {name}")
    else:
        print("\n✅ All CAPWAP tunnels look stable.")


if __name__ == "__main__":
    main()
