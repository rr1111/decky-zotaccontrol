from pathlib import Path
from typing import Literal

# files constants
ROOT_PATH = Path("zotac:rgb:spectra_zone_")
BRIGHTNESS_FILE = "brightness"
COLORS_FILE = "multi_intensity"

# max brightness from max_brightness file
MAX_BRIGHTNESS = 255

Side = Literal["left", "right"]

class RgbZone:
  # model of one of the two RGB zones

  # 10 leds per zone
  LEDS_AMNT = 10

  def __init__(self, side: Side) -> None:
    self.side: Side = side
    self.path = self._build_zone_path(side)

    # instance state
    self.leds: dict[int, dict[str, int]] = {
      i: {"red": 0, "green": 0, "blue": 0}
      # one zone has 10 leds
      for i in range(self.LEDS_AMNT)
    }
    self.brightness = 0

  # build base path for respective zone
  @staticmethod
  def _build_zone_path(side: Side) -> Path:
    zone_side = "0/" if side == "left" else "1/"
    return ROOT_PATH.with_name(f"{ROOT_PATH.name}{zone_side}")

  # path for colors file
  @property
  def colors_path(self) -> Path:
    return self.path / COLORS_FILE

  # path for brigthnes file
  @property
  def brightness_path(self) -> Path:
    return self.path / BRIGHTNESS_FILE

  def set_brightness(self, brightness_value: int) -> None:
    if brightness_value < 0 or brightness_value > MAX_BRIGHTNESS:
      raise ValueError("Brightness must be 0-255")
    self.brightness = brightness_value

  def set_led_color(self, index: int, red: int, green: int, blue: int) -> None:
    if index < 0 or index >= self.LEDS_AMNT:
      raise ValueError("Led index must be 0-9")
    self.leds[index] = {"red": red, "green": green, "blue": blue}

  def set_led_color_all(self, red: int, green: int, blue: int) -> None:
    for i in range(self.LEDS_AMNT):
      self.set_led_color(i, red, green, blue)

  # convert RGB to decimal format hardware expects
  @staticmethod
  def _rgb_to_int(red: int, green: int, blue: int) -> int:
    return (red << 16) | (green << 8) | blue

  # convert decimal to RGB I expect because im not insane
  @staticmethod
  def _int_to_rgb(value: int) -> tuple[int, int, int]:
    r = (value >> 16) & 0xFF
    g = (value >> 8) & 0xFF
    b = value & 0xFF
    return r, g, b

  # get current colors from hardware
  def load_led_colors(self) -> None:
    colors = self.colors_path.read_text().strip()
    if not colors:
      return

    tokens = colors.split()
  
    for i, token in enumerate(tokens[:self.LEDS_AMNT]):
      try:
        value = int(token)
        r, g, b = self._int_to_rgb(value)
      except ValueError:
        r = 0
        g = 0
        b = 0
      self.set_led_color(i, r, g, b)

  # write local color to hardware
  def write_led_colors(self) -> None:
    vals: list[str] = []
    for i in range(self.LEDS_AMNT):
      led = self.leds[i]
      val = self._rgb_to_int(led["red"], led["green"], led["blue"])
      vals.append(str(val))
    colors = " ".join(vals)
    self.colors_path.write_text(colors)

  # get current brightness from hardware
  def load_led_brightness(self) -> None:
    val = self.brightness_path.read_text().strip()
    if not val:
      return
    brightness = int(val)
    self.set_brightness(brightness)

  # write local brightness to hardware
  def write_led_brightness(self) -> None:
    self.brightness_path.write_text(str(self.brightness))


  # get hardware values
  def get_from_hardware(self) -> None:
    self.load_led_brightness()
    self.load_led_colors()

  # write to hardware
  def write_to_hardware(self) -> None:
    self.save_led_brightness()
    self.save_led_colors()

  