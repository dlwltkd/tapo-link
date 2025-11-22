import asyncio
import argparse
from kasa import Discover, Credentials

async def fade_brightness(ip, email, password, target_brightness, duration):
    try:
        print(f"Connecting to {ip}...")
        
        # Create credentials
        creds = Credentials(email, password)
        
        # Discover the device directly
        device = await Discover.discover_single(ip, credentials=creds)
        
        if device is None:
            print(f"Could not find device at {ip}")
            return

        await device.update()
        
        print(f"Connected to {ascii(device.alias)} ({device.model})")
        
        if not device.is_bulb and not device.is_dimmable:
             # Some strips are dimmable but maybe not "is_bulb"
             # is_dimmable is a better check if available, but let's stick to basic checks or just try.
             pass

        if not device.is_on:
            print("Turning light on...")
            await device.turn_on()
            await device.update()

        start_brightness = device.brightness
        print(f"Current Brightness: {start_brightness}%")
        print(f"Target Brightness: {target_brightness}%")
        print(f"Duration: {duration} seconds")

        if start_brightness == target_brightness:
            print("Already at target brightness.")
            return

        # Calculate steps
        step_interval = 0.5 # seconds
        total_steps = int(duration / step_interval)
        
        if total_steps == 0:
            total_steps = 1
            
        brightness_diff = target_brightness - start_brightness
        step_size = brightness_diff / total_steps

        print("Starting fade...")
        
        current_b = float(start_brightness)
        
        for i in range(total_steps):
            current_b += step_size
            new_brightness = int(round(current_b))
            
            # Clamp values
            new_brightness = max(1, min(100, new_brightness))
            
            try:
                await device.set_brightness(new_brightness)
            except Exception as e:
                print(f"Minor error setting brightness: {e}")

            await asyncio.sleep(step_interval)

        # Ensure we hit the exact target at the end
        await device.set_brightness(target_brightness)
        print("Fade complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fade Tapo light brightness.')
    parser.add_argument('--ip', required=True, help='IP address of the light')
    parser.add_argument('--email', required=True, help='TP-Link email address')
    parser.add_argument('--password', required=True, help='TP-Link password')
    parser.add_argument('--brightness', type=int, required=True, help='Target brightness (1-100)')
    parser.add_argument('--duration', type=int, required=True, help='Duration in seconds')

    args = parser.parse_args()

    asyncio.run(fade_brightness(args.ip, args.email, args.password, args.brightness, args.duration))
