__all__ = ["CALIB_OPTIONS", "calibs_to_do"]

CALIB_OPTIONS = ["all", "bias", "dark", "flat"]

def calibs_to_do(calibs):
    do_bias = False
    do_dark = False
    do_flat = False

    if calibs == "all":
        do_bias = True
        do_dark = True
        do_flat = True
    if calibs == "bias":
        do_bias = True
    if calibs == "dark":
        do_dark = True
    if calibs == "flat":
        do_flat = True

    return do_bias, do_dark, do_flat
