#!/usr/bin/env python3
"""
Simple console script to scan and connect to a Polar heart rate monitor.
Supports: Polar H10 and Polar Verity Sense
"""

import asyncio
import struct
import logging
from bleak import BleakClient, BleakScanner

# ── UUIDs ──────────────────────────────────────────────────────────────────────
HR_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
PMD_CONTROL_UUID    = "fb005c81-02e7-f387-1cad-8acd2d8df0c8"
PMD_DATA_UUID       = "fb005c82-02e7-f387-1cad-8acd2d8df0c8"

# ── Device name prefixes ───────────────────────────────────────────────────────
H10_PREFIX  = "Polar H10"
PVS_PREFIXES = ("Polar Sense", "Polar Verity Sense")

# ── SDK mode commands (PVS only) ───────────────────────────────────────────────
SDK_MODE_ENABLE  = bytearray([0x02, 0x09])
SDK_MODE_DISABLE = bytearray([0x03, 0x09])

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger("polar_connect")


# ── Callbacks ──────────────────────────────────────────────────────────────────

def on_hr(sender, data: bytearray):
    flags = data[0]
    hr = data[1] if not (flags & 0x01) else struct.unpack_from('<H', data, 1)[0]
    rr_present = (flags & 0x10) >> 4
    rr_list = []
    offset = 2 if not (flags & 0x01) else 3
    if flags & 0x08:
        offset += 2  # skip Energy Expended
    if rr_present:
        while offset + 1 < len(data):
            rr_raw = struct.unpack_from('<H', data, offset)[0]
            rr_list.append(round((rr_raw / 1024.0) * 1000.0, 1))
            offset += 2
    rr_str = f"  RR: {rr_list}" if rr_list else ""
    print(f"  ❤  HR: {hr} bpm{rr_str}")


def on_pmd_data(sender, data: bytearray):
    if len(data) < 1:
        return
    meas_type = data[0]
    type_names = {0x02: "ACC", 0x05: "GYR", 0x06: "MAG", 0x03: "PPI"}
    print(f"  📡 PMD data [{type_names.get(meas_type, f'0x{meas_type:02x}')}]"
          f"  {len(data)} bytes")


def on_disconnect(client):
    print("\n⚠️  Device disconnected.")


# ── H10 connect ────────────────────────────────────────────────────────────────

async def connect_h10():
    print("\nScanning for Polar H10 (up to 10 s)...")
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and d.name.startswith(H10_PREFIX),
        timeout=10.0,
    )
    if not device:
        print("❌  Polar H10 not found.")
        return

    print(f"✅  Found: {device.name}  ({device.address})")
    print("Connecting...")

    client = BleakClient(device, disconnected_callback=on_disconnect, timeout=30.0)
    await client.connect()

    if not client.is_connected:
        print("❌  Connection failed.")
        return

    # MTU negotiation (critical for PMD data frames)
    try:
        await client._backend._acquire_mtu()
        print(f"   MTU: {client.mtu_size}")
    except Exception as e:
        print(f"   MTU negotiation skipped: {e}")

    # Pair (required for PMD service)
    try:
        await client.pair()
        print("   Paired ✓")
    except Exception as e:
        print(f"   Pairing note: {e}")

    # Subscribe to HR
    await client.start_notify(HR_MEASUREMENT_UUID, on_hr)
    print("   HR notifications started ✓")

    # Subscribe to PMD (ACC + ECG available on H10)
    try:
        await client.start_notify(PMD_CONTROL_UUID, lambda s, d: None)
        await asyncio.sleep(0.3)
        await client.start_notify(
            PMD_DATA_UUID, on_pmd_data,
            bluez={"use_start_notify": True}
        )
        print("   PMD notifications started ✓")
    except Exception as e:
        print(f"   PMD subscribe note: {e}")

    print(f"\n🟢  Connected to {device.name} — streaming HR data.")
    print("    Press Ctrl+C to disconnect.\n")

    try:
        while client.is_connected:
            await asyncio.sleep(1.0)
    except asyncio.CancelledError:
        pass
    finally:
        print("\nDisconnecting...")
        try:
            await client.stop_notify(HR_MEASUREMENT_UUID)
        except Exception:
            pass
        try:
            await client.stop_notify(PMD_DATA_UUID)
        except Exception:
            pass
        try:
            await client.stop_notify(PMD_CONTROL_UUID)
        except Exception:
            pass
        await client.disconnect()
        print("Disconnected.")


# ── PVS connect ────────────────────────────────────────────────────────────────

async def connect_pvs():
    print("\nScanning for Polar Verity Sense (up to 10 s)...")
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name and any(d.name.startswith(p) for p in PVS_PREFIXES),
        timeout=10.0,
    )
    if not device:
        print("❌  Polar Verity Sense not found.")
        return

    print(f"✅  Found: {device.name}  ({device.address})")
    print("Connecting...")

    async with BleakClient(device, disconnected_callback=on_disconnect, timeout=20.0) as client:
        # MTU negotiation
        try:
            await client._backend._acquire_mtu()
            print(f"   MTU: {client.mtu_size}")
        except Exception as e:
            print(f"   MTU negotiation skipped: {e}")

        # Pair
        try:
            await client.pair()
            print("   Paired ✓")
        except Exception as e:
            print(f"   Pairing note: {e}")

        # Subscribe to Control Point and Data
        await client.start_notify(PMD_CONTROL_UUID, lambda s, d: None)
        await asyncio.sleep(0.5)
        await client.start_notify(PMD_DATA_UUID, on_pmd_data)
        await asyncio.sleep(0.3)

        # Subscribe to standard HR service
        try:
            await client.start_notify(HR_MEASUREMENT_UUID, on_hr)
            print("   HR notifications started ✓")
        except Exception as e:
            print(f"   HR subscribe note: {e}")

        # Enable SDK Mode for raw IMU streams
        print("   Enabling SDK Mode...")
        await client.write_gatt_char(PMD_CONTROL_UUID, SDK_MODE_ENABLE, response=True)
        await asyncio.sleep(0.5)

        # Start ACC: 52 Hz, 16-bit, 8G, 3ch
        # Command format: 0x02 <type> [<setting_type> <array_len> <value LE16>]...
        acc_cmd = bytearray([
            0x02, 0x02,          # START, ACC
            0x00, 0x01, 0x34, 0x00,  # sample rate = 52 Hz
            0x01, 0x01, 0x10, 0x00,  # resolution = 16 bit
            0x02, 0x01, 0x08, 0x00,  # range = 8 G
            0x04, 0x01, 0x03, 0x00,  # channels = 3
        ])
        await client.write_gatt_char(PMD_CONTROL_UUID, acc_cmd, response=True)
        await asyncio.sleep(0.3)
        print("   ACC stream started ✓")

        print(f"\n🟢  Connected to {device.name} — streaming HR + ACC data.")
        print("    Press Ctrl+C to disconnect.\n")

        try:
            while client.is_connected:
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            pass
        finally:
            print("\nDisconnecting...")
            # Stop ACC
            try:
                await client.write_gatt_char(
                    PMD_CONTROL_UUID, bytearray([0x03, 0x02]), response=True
                )
            except Exception:
                pass
            # Disable SDK Mode
            try:
                await client.write_gatt_char(PMD_CONTROL_UUID, SDK_MODE_DISABLE, response=True)
            except Exception:
                pass
            try:
                await client.stop_notify(PMD_DATA_UUID)
                await client.stop_notify(PMD_CONTROL_UUID)
                await client.stop_notify(HR_MEASUREMENT_UUID)
            except Exception:
                pass
            print("Disconnected.")


# ── Main ───────────────────────────────────────────────────────────────────────

async def main():
    print("=" * 50)
    print("  Polar Heart Rate Monitor — Connect Tool")
    print("=" * 50)
    print("\nWhich sensor do you want to connect to?")
    print("  1) Polar H10")
    print("  2) Polar Verity Sense")

    while True:
        choice = input("\nEnter 1 or 2: ").strip()
        if choice in ("1", "2"):
            break
        print("  Please enter 1 or 2.")

    if choice == "1":
        await connect_h10()
    else:
        await connect_pvs()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
