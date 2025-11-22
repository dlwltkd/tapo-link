import asyncio
from kasa import Discover

async def main():
    print("Scanning for devices...")
    devices = await Discover.discover()
    
    if not devices:
        print("No devices found. Make sure your computer is on the same Wi-Fi as the light.")
        return

    print(f"\nFound {len(devices)} device(s):")
    for ip, device in devices.items():
        await device.update()
        print(f"\n--- {device.alias} ---")
        print(f"  Model: {device.model}")
        print(f"  IP Address: {ip}")
        print(f"  MAC Address: {device.mac}")
        print(f"  Type: {device.device_type}")

if __name__ == "__main__":
    asyncio.run(main())
