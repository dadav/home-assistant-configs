"""Build the "Floor plan" view JSON for the home-main dashboard (storage mode).

Usage: python3 tools/floorplan/view.py > tools/floorplan/view.json
Apply via the HA MCP: ha_config_set_dashboard(url_path="home-main", patch=[{"op": "add",
"path": "/views/2", "value": <view.json>}]) or replace the existing view at that index.

Element positions use the same pixel coordinates as generate.py, converted to percent.
"""

import json

from generate import VIEW_H, VIEW_W, VIEW_X, VIEW_Y

IMAGE_LIGHT = "/local/floorplan/floorplan-light.svg"
IMAGE_DARK = "/local/floorplan/floorplan-dark.svg"

PILL_BACKGROUND = "color-mix(in srgb, var(--card-background-color) 88%, transparent)"
PILL_SHADOW = "0 1px 6px rgba(0, 0, 0, 0.18)"

# Temperature pill per room. fallback is used while the primary sensor is unavailable.
ROOM_READINGS = [
    {
        "room": "Zimmer 1",
        "at": (450, 215),
        "temperature": "sensor.buro_1_temperature",
        "fallback": None,
        "secondary": [],
    },
    {
        "room": "DU/WC",
        "at": (715, 190),
        "temperature": "sensor.bath2_temp_temperature",
        "fallback": "sensor.bath2_waterdetector_temperature",
        "secondary": ["sensor.bath2_temp_humidity"],
    },
    {
        "room": "Wohnen",
        "at": (500, 670),
        "temperature": "sensor.living_temp_temperature",
        "fallback": "sensor.wohnzimmer_temperature",
        "secondary": ["sensor.living_temp_humidity"],
    },
    {
        "room": "Essen",
        "at": (895, 960),
        "temperature": "sensor.lunch_co2meter_temperature",
        "fallback": None,
        "secondary": ["sensor.lunch_co2meter_humidity", "sensor.lunch_co2meter_co2"],
    },
    {
        "room": "Kueche",
        "at": (1210, 1040),
        "temperature": "sensor.kitchen_temp_temperature",
        "fallback": None,
        "secondary": ["sensor.kitchen_temp_humidity"],
    },
    {
        "room": "Zimmer 2",
        "at": (500, 1050),
        "temperature": "sensor.office2_temp_temperature",
        "fallback": "sensor.buro_2_temperature",
        "secondary": ["sensor.office2_temp_humidity"],
    },
    {
        "room": "Bad",
        "at": (1600, 850),
        "temperature": "sensor.bath1_temp_temperature",
        "fallback": None,
        "secondary": ["sensor.bath1_temp_humidity"],
    },
    {
        "room": "Schlafen",
        "at": (1545, 1200),
        "temperature": "sensor.bedroom_temp_temperature",
        "fallback": "sensor.schlafzimmer_1_temperature",
        "secondary": ["sensor.bedroom_temp_humidity"],
    },
    {
        "room": "Wintergarten",
        "at": (165, 670),
        "temperature": "sensor.wintergarden_temp_temperature",
        "fallback": None,
        "secondary": ["sensor.wintergarden_temp_humidity"],
    },
    {
        "room": "Keller 2",
        "at": (1835, 530),
        "temperature": "sensor.storage_temp_temperature",
        "fallback": None,
        "secondary": ["sensor.storage_temp_humidity"],
    },
]

# Icons placed on the plan: contacts sit on their door/window, controls sit in the room.
# toggle: tap toggles instead of opening more-info. alert_only: shown only while "on".
ICONS = [
    # Contacts
    {"entity": "binary_sensor.office1_window_contact", "at": (290, 300)},
    {"entity": "binary_sensor.office2_door_contact", "at": (390, 1230)},
    {"entity": "binary_sensor.lunch_door_contact", "at": (892, 1230)},
    {"entity": "binary_sensor.kitchen_door_contact", "at": (1220, 1230)},
    {"entity": "binary_sensor.bedroom_door_contact", "at": (1580, 1450)},
    {"entity": "binary_sensor.bedroom_window_contact", "at": (1750, 1130)},
    {"entity": "binary_sensor.bath1_window_contact", "at": (1750, 835)},
    {"entity": "binary_sensor.wintergarden_door_contact", "at": (165, 870)},
    {"entity": "binary_sensor.wintergarden_window_contact", "at": (40, 670)},
    {"entity": "binary_sensor.entrance_door_contact", "at": (1025, 470)},
    {"entity": "binary_sensor.storage_door1_contact", "at": (1920, 690)},
    {"entity": "binary_sensor.storage_door2_contact", "at": (1685, 637)},
    # Thermostats
    {"entity": "climate.buro_1", "at": (400, 330)},
    {"entity": "climate.buro_2", "at": (450, 1160)},
    {"entity": "climate.wohnzimmer", "at": (450, 790)},
    {"entity": "climate.esszimmer_1", "at": (845, 1110)},
    {"entity": "climate.esszimmer_2", "at": (945, 1110)},
    {"entity": "climate.schlafzimmer_1", "at": (1495, 1330)},
    {"entity": "climate.schlafzimmer_2", "at": (1595, 1330)},
    {"entity": "climate.bad", "at": (1550, 950)},
    # Lights and switches
    {"entity": "light.office1_light2", "at": (500, 330), "toggle": True},
    {"entity": "light.office2_light", "at": (550, 1160), "toggle": True},
    {
        "entity": "switch.kitchen_powerplug",
        "at": (1210, 1160),
        "toggle": True,
        "icon": "mdi:stove",
    },
    {
        "entity": "switch.bath1_powerplug",
        "at": (1650, 950),
        "toggle": True,
        "icon": "mdi:radiator",
    },
    # Entrance
    {"entity": "lock.vordereingang_lock", "at": (960, 590)},
    {
        "entity": "binary_sensor.vordereingang_ding_2",
        "at": (1060, 590),
        "icon": "mdi:doorbell",
    },
    # Alerts
    {
        "entity": "binary_sensor.is_showering",
        "at": (1700, 760),
        "alert_only": True,
        "icon": "mdi:shower-head",
    },
    {
        "entity": "binary_sensor.bath2_waterdetector_water_leak",
        "at": (715, 290),
        "alert_only": True,
    },
]

HEADING_BADGES = [
    {"entity": "sensor.outside_temp_temperature", "name": "Outside"},
    {"entity": "sensor.garage_temp_temperature", "name": "Garage"},
    {"entity": "binary_sensor.garage_door_contact", "name": "Garage door"},
    {"entity": "binary_sensor.everything_closed", "name": "Closed"},
    {"entity": "alarm_control_panel.security_alarm", "name": "Alarm"},
]


def position(at):
    x, y = at
    left = round((x - VIEW_X) / VIEW_W * 100, 2)
    top = round((y - VIEW_Y) / VIEW_H * 100, 2)
    return {"left": f"{left}%", "top": f"{top}%"}


def temperature_label(entity, at):
    return {
        "type": "state-label",
        "entity": entity,
        "style": {
            **position(at),
            "font-size": "clamp(12px, 1.5vw, 28px)",
            "font-weight": "600",
            "color": "var(--primary-text-color)",
            "background": PILL_BACKGROUND,
            "box-shadow": PILL_SHADOW,
            "padding": "0.15em 0.6em",
            "border-radius": "999px",
            "white-space": "nowrap",
        },
    }


def secondary_label(entity, at, index):
    x, y = at
    return {
        "type": "state-label",
        "entity": entity,
        "style": {
            **position((x, y + 50 + index * 38)),
            "font-size": "clamp(9px, 0.95vw, 17px)",
            "color": "var(--secondary-text-color)",
            "white-space": "nowrap",
        },
    }


def unavailable_condition(entity):
    return [
        {"entity": entity, "state_not": "unavailable"},
        {"entity": entity, "state_not": "unknown"},
    ]


def room_elements(reading):
    elements = []
    primary = temperature_label(reading["temperature"], reading["at"])
    if reading["fallback"]:
        elements.append(
            {
                "type": "conditional",
                "conditions": unavailable_condition(reading["temperature"]),
                "elements": [primary],
            }
        )
        elements.append(
            {
                "type": "conditional",
                "conditions": [
                    {"entity": reading["temperature"], "state": "unavailable"}
                ],
                "elements": [temperature_label(reading["fallback"], reading["at"])],
            }
        )
    else:
        elements.append(
            {
                "type": "conditional",
                "conditions": unavailable_condition(reading["temperature"]),
                "elements": [primary],
            }
        )
    for index, entity in enumerate(reading["secondary"]):
        elements.append(
            {
                "type": "conditional",
                "conditions": unavailable_condition(entity),
                "elements": [secondary_label(entity, reading["at"], index)],
            }
        )
    return elements


def icon_element(spec):
    element = {
        "type": "state-icon",
        "entity": spec["entity"],
        "state_color": True,
        "style": {
            **position(spec["at"]),
            "--mdc-icon-size": "clamp(16px, 1.7vw, 30px)",
            "background": PILL_BACKGROUND,
            "box-shadow": PILL_SHADOW,
            "border-radius": "50%",
            "padding": "0.15em",
        },
    }
    if "icon" in spec:
        element["icon"] = spec["icon"]
    if spec.get("toggle"):
        element["tap_action"] = {"action": "toggle"}
        element["hold_action"] = {"action": "more-info"}
    if spec.get("alert_only"):
        element["style"]["color"] = "var(--error-color)"
        return {
            "type": "conditional",
            "conditions": [{"entity": spec["entity"], "state": "on"}],
            "elements": [element],
        }
    return element


def build_view():
    elements = []
    for reading in ROOM_READINGS:
        elements.extend(room_elements(reading))
    for spec in ICONS:
        elements.append(icon_element(spec))

    heading = {
        "type": "heading",
        "heading": "Floor plan",
        "heading_style": "title",
        "icon": "mdi:floor-plan",
        "badges": [
            {
                "type": "entity",
                "entity": badge["entity"],
                "name": badge["name"],
                "show_state": True,
                "show_icon": True,
            }
            for badge in HEADING_BADGES
        ],
    }
    card = {
        "type": "picture-elements",
        "image": IMAGE_LIGHT,
        "dark_mode_image": IMAGE_DARK,
        "elements": elements,
        "grid_options": {"columns": "full"},
    }
    return {
        "title": "Floor plan",
        "path": "floorplan",
        "icon": "mdi:floor-plan",
        "type": "sections",
        "max_columns": 4,
        "sections": [{"type": "grid", "column_span": 4, "cards": [heading, card]}],
    }


if __name__ == "__main__":
    print(json.dumps(build_view(), indent=2, ensure_ascii=False))
