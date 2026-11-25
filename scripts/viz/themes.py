"""Colour themes shared by the Commit Run and Commit Exchange cards.

Pick one with --theme (or the CARD_THEME environment variable). Every theme
defines the same keys, so any card can be drawn in any theme.
"""

THEMES = {
    # the profile's own deep navy, with GitHub greens
    "midnight": {
        "bg": "#0A0C1C", "panel": "#131733", "line": "#272C50", "text": "#EEF0F7", "muted": "#9097B8",
        "accent": "#7EE787", "accent2": "#A9B8FF", "up": "#3FB950", "down": "#F85149",
        "levels": ["#1B1F3B", "#0E4429", "#006D32", "#26A641", "#39D353"],
    },
    "aurora": {
        "bg": "#06161C", "panel": "#0C2229", "line": "#173A43", "text": "#E6FFFB", "muted": "#7FB5B0",
        "accent": "#5EF2C9", "accent2": "#B794F6", "up": "#5EF2C9", "down": "#FF6B9A",
        "levels": ["#10272E", "#14524F", "#1F8A7A", "#46C9A8", "#B794F6"],
    },
    "ocean": {
        "bg": "#061226", "panel": "#0B1D3A", "line": "#163160", "text": "#E7F1FF", "muted": "#8AA6CF",
        "accent": "#4FC3F7", "accent2": "#82AAFF", "up": "#4FC3F7", "down": "#FF7A90",
        "levels": ["#0F2445", "#0D3B73", "#1565C0", "#2196F3", "#80D8FF"],
    },
    "sunset": {
        "bg": "#1A0B14", "panel": "#26111D", "line": "#45203A", "text": "#FFF0E8", "muted": "#C99AA8",
        "accent": "#FFB86B", "accent2": "#FF7AA2", "up": "#FFB86B", "down": "#FF5C7A",
        "levels": ["#2E1524", "#6B2342", "#B23A48", "#F26B3A", "#FFC45C"],
    },
    "forest": {
        "bg": "#08140D", "panel": "#0F2016", "line": "#1D3A27", "text": "#EAF7EE", "muted": "#8DB59A",
        "accent": "#9BE564", "accent2": "#D4C27A", "up": "#9BE564", "down": "#E5735C",
        "levels": ["#13251A", "#1E4D2B", "#2F7D3B", "#56B04F", "#A6E36A"],
    },
    "mono": {
        "bg": "#0D0D0F", "panel": "#17171A", "line": "#2A2A30", "text": "#F2F2F2", "muted": "#9A9AA2",
        "accent": "#FFFFFF", "accent2": "#BDBDC4", "up": "#E6E6E6", "down": "#7A7A80",
        "levels": ["#1E1E22", "#3A3A40", "#66666E", "#A3A3AB", "#F2F2F2"],
    },
}

DEFAULT = "midnight"


def get(name):
    return THEMES.get((name or DEFAULT).lower(), THEMES[DEFAULT])
