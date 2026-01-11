import time

def decoder_init(target_sequence=None, hold_frames=1, timeout_sec=10):
    """
    Initialize decoder state (no classes).
    Returns a dict you should keep and pass to decoder_update/decoder_reset.
    """
    if target_sequence is None:
        target_sequence = ["CIRCLE", "TRIANGLE", "SQUARE", "RECTANGLE"]

    return {
        "target": target_sequence,
        "hold_frames": int(hold_frames),
        "timeout_sec": float(timeout_sec),
        "state": "LOCKED",
        "input_sequence": [],
        "message": "Show the sequence",
        "last_shape": None,
        "stable_count": 0,
        "last_seen_time": time.time(),
    }

def decoder_reset(dec):
    """Reset decoder to LOCKED and clear input."""
    dec["state"] = "LOCKED"
    dec["input_sequence"] = []
    dec["message"] = "Manual reset"
    dec["last_shape"] = None
    dec["stable_count"] = 0
    dec["last_seen_time"] = time.time()

def decoder_update(dec, shape_name):
    """
    Update decoder with the current detected shape_name (or None).
    Returns (state, input_sequence, message).
    """
    now = time.time()

    #delete the sequence when we take longer than we should
    if shape_name is None:
        if dec["state"] != "UNLOCKED" and (now - dec["last_seen_time"]) > dec["timeout_sec"]:
            dec["input_sequence"] = []
            dec["message"] = "Timeout -> reset"
        dec["last_shape"] = None
        dec["stable_count"] = 0
        return dec["state"], dec["input_sequence"], dec["message"]

    #if we detect a figure, we start the last_seen_time 
    dec["last_seen_time"] = now

    #we also require stability for N frames in order to confirm the figure 
    if shape_name == dec["last_shape"]:
        dec["stable_count"] += 1
    else:
        dec["last_shape"] = shape_name
        dec["stable_count"] = 1

    #when we reach stability, we add the figure to the input sequence 
    if dec["stable_count"] == dec["hold_frames"] and dec["state"] == "LOCKED":
        dec["input_sequence"].append(shape_name)
        dec["message"] = f"Added: {shape_name}"

        #checking prefix validity (if we have followed correctly the sequence)
        ok_prefix = True
        for i in range(len(dec["input_sequence"])):
            if i >= len(dec["target"]) or dec["input_sequence"][i] != dec["target"][i]:
                ok_prefix = False
                break

        if not ok_prefix:
            dec["input_sequence"] = []
            dec["message"] = "Wrong sequence -> reset"
        else:
            # Unlock if sequence completed
            if len(dec["input_sequence"]) == len(dec["target"]):
                dec["state"] = "UNLOCKED"
                dec["message"] = "ACCESS GRANTED"

    return dec["state"], dec["input_sequence"], dec["message"]
