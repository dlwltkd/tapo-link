# Tapo Light Controller

Control your TP-Link Tapo smart lights with Python to create **complex brightness patterns** and **cinematic time-lapse effects**. The possibilities are endless!

## 🌟 What You Can Do

This project demonstrates the power of programmatic control over Tapo lights using the `python-kasa` library:

- **Smooth Time-Lapses**: Create realistic sunrise/sunset effects over custom durations (20 minutes, 3 hours, etc.)
- **Color Transitions**: Seamlessly fade between colors (Red → Orange → Warm White)
- **Precision Timing**: Drift-corrected timing ensures your effects run exactly as long as you specify
- **Hardware Smoothing**: Leverages hardware transition capabilities for buttery-smooth fades
- **Human Eye Correction**: Uses gamma curves to make brightness changes feel natural
- **Complex Patterns**: Build your own custom brightness/color sequences

### Why This Matters

Standard smart light apps are limited to simple on/off/dim controls. With this approach, you can:
- Simulate natural daylight cycles for photography/videography
- Create custom wake-up lighting routines
- Build theatrical lighting effects
- Automate complex lighting scenes
- Develop your own creative patterns

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install python-kasa
```

### 2. Configure Your Credentials

Copy the template and add your details:

```bash
cp config.template.py config.py
```

Edit `config.py`:
```python
EMAIL = "your-tapo-email@example.com"
PASSWORD = "your-tapo-password"
IP_ADDRESS = "192.168.1.XXX"  # Your light's IP
```

### 3. Find Your Light's IP

```bash
python discover_tapo.py
```

This will scan your network and show all Tapo devices.

### 4. Run a Time-Lapse

```bash
python smooth_timelapse.py
```

## 📜 Scripts

### `smooth_timelapse.py` - The Main Event

The most advanced script with **Sunrise** and **Sunset** modes.

**Configuration** (edit the top of the file):

```python
DURATION_MINUTES = 20      # How long the effect takes
START_BRIGHTNESS = 0       # 0 = OFF, 1-100 = brightness
END_BRIGHTNESS = 100       # Target brightness
SUN_MODE = True            # Enable color shifting
```

**Examples:**

**Sunrise** (OFF → Bright White over 30 minutes):
```python
DURATION_MINUTES = 30
START_BRIGHTNESS = 0
END_BRIGHTNESS = 100
```

**Sunset** (Bright → OFF over 20 minutes):
```python
DURATION_MINUTES = 20
START_BRIGHTNESS = 100
END_BRIGHTNESS = 0
```

**How It Works:**
- **Sunrise Mode**: Starts with deep red at 1%, gradually shifts through orange to warm white as brightness increases
- **Sunset Mode**: Starts at warm white, fades through orange to deep red, then turns off
- **Gamma Correction**: Uses quadratic curves so the fade feels linear to your eyes
- **Color Masking**: The color shift hides the hardware's low-brightness "choppiness" (1% → 2% jumps)

### `fade_light.py` - Simple Brightness Fade

Basic script for quick brightness changes.

```bash
python fade_light.py --ip 192.168.45.111 --email you@example.com --password YourPass --brightness 50 --duration 10
```

### `discover_tapo.py` - Device Discovery

Finds all Tapo/Kasa devices on your network.

## 🎨 Creating Custom Patterns

The core logic in `smooth_timelapse.py` can be adapted for endless possibilities:

### Example Ideas:

**1. Pulsing Effect**
```python
# Modify the curve_progress calculation
curve_progress = abs(math.sin(progress * math.pi * 3))  # 3 pulses
```

**2. Color Cycle**
```python
# Cycle through the full hue spectrum
target_h = int(360 * progress)
target_s = 100
```

**3. Strobe Effect**
```python
# Rapid on/off
if i % 2 == 0:
    await device.turn_on()
else:
    await device.turn_off()
```

**4. Random Flicker**
```python
import random
target_b = random.randint(20, 100)
```

## 🔧 Technical Details

### Smoothness Optimizations

1. **Hardware Transitions**: Uses the `transition` parameter to let the bulb interpolate between states
2. **Drift Correction**: Calculates sleep time relative to start time, not previous step
3. **High Step Count**: 200 steps for color transitions vs. 100 for brightness-only
4. **Gamma Curves**: Quadratic curves match human perception

### Supported Devices

Any Tapo light supported by `python-kasa`:
- L530, L510, L630 (Bulbs)
- L900, L920, L930 (Light Strips)

See the [python-kasa documentation](https://python-kasa.readthedocs.io/) for the full list.

## 🐛 Troubleshooting

**"Could not find device"**
- Ensure your computer and light are on the same Wi-Fi network
- Check if the IP address changed (run `discover_tapo.py` again)

**"Connection error"**
- Verify your email/password in `config.py`
- Make sure you're using your Tapo app credentials

**Choppy at low brightness**
- Enable `SUN_MODE = True` to use color masking
- The hardware limitation of 1% steps is unavoidable, but color helps hide it

**Deprecation warnings**
- These are harmless and can be ignored (the library is updating its API)

## 📝 License

MIT License - Feel free to use and modify for your projects!

## 🙏 Credits

Built with [python-kasa](https://github.com/python-kasa/python-kasa) - an excellent library for controlling TP-Link smart home devices.

---

**The possibilities are truly endless.** Fork this project and create your own lighting masterpieces! 🎬✨
