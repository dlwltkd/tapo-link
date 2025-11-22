import asyncio
import time
import math
from kasa import Discover, Credentials
from config import EMAIL, PASSWORD, IP_ADDRESS

# ==========================================
# CONFIGURATION SECTION - EDIT THESE VALUES
# ==========================================

# Time-Lapse Settings
DURATION_MINUTES =   4 # How long the fade should take
START_BRIGHTNESS = 100   # Starting brightness (0-100)
END_BRIGHTNESS = 0     # Ending brightness (0-100)

# Advanced Smoothness Settings
USE_TRANSITION = True  # Try to use hardware interpolation
HUMAN_EYE_CORRECTION = True # Use a curve for brightness

# Sun Mode (Sunrise/Sunset)
# Automatically changes color from Red <-> Warm White based on brightness direction.
# Helps mask low-light choppiness.
SUN_MODE = True 

# ==========================================

async def run_timelapse():
    try:
        print(f"Connecting to {IP_ADDRESS}...")
        creds = Credentials(EMAIL, PASSWORD)
        device = await Discover.discover_single(IP_ADDRESS, credentials=creds)

        if device is None:
            print(f"Error: Could not find device at {IP_ADDRESS}")
            return

        await device.update()
        print(f"Connected to {ascii(device.alias)} ({device.model})")

        # Calculate timing
        duration_seconds = DURATION_MINUTES * 60
        
        # Determine Mode (Sunrise or Sunset)
        is_sunrise = END_BRIGHTNESS > START_BRIGHTNESS
        
        # Handle 0 brightness for calculations (clamp to 1)
        calc_start_b = max(1, START_BRIGHTNESS)
        calc_end_b = max(1, END_BRIGHTNESS)
        
        # Setup Initial State
        if SUN_MODE:
            # Define Color Points
            # Deep Red (H=0, S=100) <-> Warm White (H=40, S=10)
            red_h, red_s = 0, 100
            white_h, white_s = 40, 10
            
            if is_sunrise:
                start_h, start_s = red_h, red_s
                end_h, end_s = white_h, white_s
                print("Initializing Sunrise Mode (Deep Red -> Warm White)...")
            else:
                start_h, start_s = white_h, white_s
                end_h, end_s = red_h, red_s
                print("Initializing Sunset Mode (Warm White -> Deep Red)...")

            # Handle Starting from OFF
            if START_BRIGHTNESS == 0:
                print("Ensuring light is OFF before start...")
                if device.is_on:
                    await device.turn_off()
                    await asyncio.sleep(1) # Wait for it to actually turn off
                
                # Try to set the initial state while OFF (to avoid flash)
                # Some bulbs accept this, some don't.
                try:
                    await device.set_hsv(start_h, start_s, calc_start_b)
                except:
                    pass
                
                print("Turning ON to 1%...")
                await device.turn_on()
                # Enforce state again just in case
                await device.set_hsv(start_h, start_s, calc_start_b)
            
            else:
                # Start Brightness > 0 (e.g. Sunset starting at 100%)
                # Ensure it starts ON.
                if not device.is_on:
                    print("Turning light ON...")
                    # Try to preset state to avoid flash of previous brightness
                    try:
                        await device.set_hsv(start_h, start_s, calc_start_b)
                    except:
                        pass
                    await device.turn_on()
                
                # Enforce initial state
                await device.set_hsv(start_h, start_s, calc_start_b)
            
        else:
            # Standard Mode
            print(f"Initializing Standard Mode ({START_BRIGHTNESS}% -> {END_BRIGHTNESS}%)...")
            
            if START_BRIGHTNESS == 0:
                if device.is_on:
                    await device.turn_off()
                    await asyncio.sleep(1)
                
                try:
                    await device.set_brightness(calc_start_b)
                except:
                    pass
                    
                await device.turn_on()
                await device.set_brightness(calc_start_b)
            else:
                # Start Brightness > 0
                if not device.is_on:
                    print("Turning light ON...")
                    try:
                        await device.set_brightness(calc_start_b)
                    except:
                        pass
                    await device.turn_on()
                
                await device.set_brightness(calc_start_b)

        # Calculate Steps
        total_steps = 200 
        seconds_per_step = duration_seconds / total_steps
        
        print(f"--- Time-Lapse Started ---")
        print(f"Duration: {DURATION_MINUTES} minutes")
        print(f"Direction: {'Sunrise' if is_sunrise else 'Sunset'}")
        print(f"Time per step: {seconds_per_step:.2f} seconds")
        print("--------------------------")

        start_time = time.time()
        
        for i in range(total_steps + 1):
            # Calculate progress (0.0 to 1.0)
            progress = i / total_steps
            
            # --- Curve Calculation ---
            if HUMAN_EYE_CORRECTION:
                if is_sunrise:
                    # Sunrise: Slow start, fast end (Convex)
                    # Spend time at low brightness/red
                    curve_progress = progress * progress
                else:
                    # Sunset: Fast start, slow end (Concave)
                    # Drop quickly from white, spend time at low brightness/red
                    curve_progress = 1 - ((1 - progress) * (1 - progress))
            else:
                curve_progress = progress

            # --- Value Calculation ---
            # Brightness
            current_b_float = calc_start_b + ((calc_end_b - calc_start_b) * curve_progress)
            target_b = int(round(current_b_float))
            target_b = max(1, min(100, target_b))
            
            # Color (if Sun Mode)
            if SUN_MODE:
                target_h = int(start_h + ((end_h - start_h) * curve_progress))
                target_s = int(start_s + ((end_s - start_s) * curve_progress))

            # --- Command Execution ---
            try:
                transition_ms = int(seconds_per_step * 1000) - 100
                transition_ms = max(0, transition_ms)
                
                if SUN_MODE:
                    if USE_TRANSITION and transition_ms > 100:
                        await device.set_hsv(target_h, target_s, target_b, transition=transition_ms)
                    else:
                        await device.set_hsv(target_h, target_s, target_b)
                else:
                    if USE_TRANSITION and transition_ms > 100:
                        await device.set_brightness(target_b, transition=transition_ms)
                    else:
                        await device.set_brightness(target_b)
                    
            except Exception as e:
                pass

            # Drift correction sleep
            if i < total_steps:
                target_next_time = start_time + ((i + 1) * seconds_per_step)
                now = time.time()
                sleep_duration = target_next_time - now
                
                if sleep_duration > 0:
                    await asyncio.sleep(sleep_duration)

        # Final Cleanup
        if END_BRIGHTNESS == 0:
            print("Turning off...")
            await device.turn_off()

        print("--- Time-Lapse Complete ---")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_timelapse())
