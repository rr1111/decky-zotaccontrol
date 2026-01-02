from pathlib import Path
from decky_plugin import logger

# Sysfs paths for both zones
LEDS_PATH = Path("/sys/class/leds/")


        1) ID=5; NAME="Static" ;;
        2) ID=2; NAME="Breathe" ;;
        3) ID=3; NAME="Cycle" ;;
        4) ID=0; NAME="Wave" ;;
        5) ID=240; NAME="Off" ;;


# File that accepts "R G B" (adjust if needed)
SETTINGS_FILES = {
    "brightness_file" = "brightness",
    "color_file" = "multi_intensity",



}

# 5 preset colors
RGB_PRESETS = {
    "red":    (255, 0,   0),
    "green":  (0,   255, 0),
    "blue":   (0,   0,   255),
    "white":  (255, 255, 255),
    "orange": (255, 128, 0),
}

def _write_zone_color(zone_path: Path, rgb: tuple[int, int, int]) -> None:
    r, g, b = rgb
    intensity_path = zone_path / INTENSITY_FILE
    if not intensity_path.exists():
        raise FileNotFoundError(f"{intensity_path} does not exist")

    intensity_path.write_text(f"{r} {g} {b}\n")

def set_rgb_preset(name: str):
    """
    Set both spectra zones to one of: red, green, blue, white, orange.
    Returns 'ok' or 'error: ...'
    """
    name = name.lower()
    if name not in RGB_PRESETS:
        return f"error: unknown preset '{name}'"

    rgb = RGB_PRESETS[name]
    logger.info(f"Setting Zotac RGB zones to preset '{name}' -> {rgb}")

    try:
        for z in ZONE_PATHS:
            _write_zone_color(z, rgb)
        return "ok"
    except Exception as e:
        logger.error(f"set_rgb_preset failed: {e}")
        return f"error: {e}"
