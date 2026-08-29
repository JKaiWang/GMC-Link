"""Expression keyword classifier shared by every eval / regroup script (A43, 2026-08-29).

One list, one function, two roles: (1) the two-alpha fusion router
(MOVING/STATIC -> alpha_mot, APPEARANCE -> alpha_app) and (2) the per-class
HOTA grouping the paper reports. The pre-A43 lists (moving, walking, running,
turning, faster, slower, braking, accelerat) lived as copies in each script;
"turning"/"faster" are no longer MOVING.
"""

MOVING_KW = [
    # explicit motion
    "moving", "in motion", "driving", "walking", "running", "jogging", "crossing",
    "riding", "travelling", "traveling",
    # velocity changes
    "braking", "brake", "accelerat", "decelerat", "slowing down", "speeding up",
    # relative motion
    "approaching", "overtaking", "receding",
]
STATIC_KW = ["parking", "parked", "stopped", "stop", "stand", "static", "stationary"]


def classify(text):
    """'MOVING' | 'STATIC' | 'APPEARANCE'. Slugs ("moving-cars") and sentences
    ("moving cars") classify identically. STATIC wins on a tie (none in Refer-KITTI)."""
    t = text.lower().replace("-", " ")
    if any(k in t for k in STATIC_KW):
        return "STATIC"
    if any(k in t for k in MOVING_KW):
        return "MOVING"
    return "APPEARANCE"


if __name__ == "__main__":  # self-check
    assert classify("moving-cars") == classify("moving cars") == "MOVING"
    assert classify("turning-cars") == "APPEARANCE"
    assert classify("cars-which-are-faster-than-ours") == "APPEARANCE"
    assert classify("left-cars-which-are-parking") == "STATIC"
    assert classify("standing-females") == "STATIC"
    assert classify("braked cars") == "MOVING"
    assert classify("women-carrying-a-bag") == "APPEARANCE"
    print("ok")
