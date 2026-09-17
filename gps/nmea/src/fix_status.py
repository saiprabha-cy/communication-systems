import pynmea2


def get_navigation_state(sentence: str) -> dict:
    """Validity gate function to prevent invalid GNSS data

    from reaching downstream flight control logic.
    """
    msg = pynmea2.parse(sentence)

    # Validity Gate: reject payload if RMC status is Void ('V')
    if msg.status != "A":
        return {
            "valid": False,
            "reason": "No valid navigation solution (Status: V)",
        }

    return {
        "valid": True,
        "latitude": msg.latitude,
        "longitude": msg.longitude,
        "speed_knots": float(msg.spd_over_grnd) if msg.spd_over_grnd else 0.0,
        "course_deg": float(msg.true_course) if msg.true_course else 0.0,
    }


valid_sentence = (
    "$GPRMC,184353.07,A,"
    "1929.045,S,02410.506,E,"
    "000.0,000.0,120926,,,A*44"
)

invalid_sentence = (
    "$GPRMC,184353.07,V,"
    "1929.045,S,02410.506,E,"
    "000.0,000.0,120926,,,A*53"
)

if __name__ == "__main__":
    for name, sentence in [
        ("VALID", valid_sentence),
        ("INVALID", invalid_sentence),
    ]:
        nav_state = get_navigation_state(sentence)

        print(f"\n=== {name} RMC GATE RESULT ===")
        if nav_state["valid"]:
            print(f"Status    : VALID (A)")
            print(f"Latitude  : {nav_state['latitude']:.6f}")
            print(f"Longitude : {nav_state['longitude']:.6f}")
            print(f"Speed     : {nav_state['speed_knots']} knots")
            print(f"Course    : {nav_state['course_deg']} deg")
        else:
            print(f"Status    : REJECTED")
            print(f"Reason    : {nav_state['reason']}")