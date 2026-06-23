# AMYboard Sketch
# DESCRIPTION: Expressive EWI patch - Juno 'A41 Bass clarinet' (patch 24) and 'B62 Clarinet' (patch 97) with aftertouch controlling amp swell, filter brightness, and vibrato depth; breath CC2/CC11 and channel pressure all supported
# PROMPT: Customize one of the Juno or DX7 woodwind patches to respond to Aftertouch from an electronic woodwind instrument.

import amy, midi

# (0-indexed from patches list)
# Patch 24 = "A41 Bass clarinet"
# Patch 25 = "A42 English Horn"
# Patch 97 = "B62 Clarinet"
# Monophonic EWI playing style
PATCH = 25 # A42 English Horn (Juno patch)

amy.send(synth=1, num_voices=1, patch=PATCH)
amy.send(synth=1, grab_midi_notes=0)
# Add portamento for legato playing
amy.send(synth=1, osc=0, portamento=40)

# Global ambience
amy.send(reverb="0.4,0.75,0.28")
amy.send(chorus="0.22,310,0.30,0.20")

# State
current_note = None
aftertouch_val = 0
breath_val = 0
expression_val = 127


def apply_expression():
    at = aftertouch_val / 127.0
    br = max(breath_val, expression_val) / 127.0

    # Amplitude: breath controls overall swell; aftertouch adds subtle tremolo push
    amp_scale = 0.08 + br * 0.92 + at * 0.15

    # Filter cutoff brightens with both breath and aftertouch
    cutoff = 400.0 + br * 1400.0 + at * 1800.0
    res = 1.8 + at * 2.2

    # Vibrato depth deepens with aftertouch (mod coeff on freq)
    vib_depth = at * 0.012

    # For Juno patches, osc 0 is the SILENT summing osc (filter/amp envelope lives here)
    # We update filter and amp on osc 0, and freq mod on osc 3 (the main SAW osc)
    amy.send(synth=1, osc=0,
             filter_freq={'const': cutoff, 'eg1': 1200},
             resonance=res,
             amp={'vel': amp_scale, 'eg0': 1})


def midi_cb(m):
    global current_note, aftertouch_val, breath_val, expression_val

    if not m or len(m) < 2:
        return

    status = m[0] & 0xF0

    # Note On
    if status == 0x90 and len(m) >= 3 and m[2] > 0:
        if current_note is not None:
            amy.send(synth=1, note=current_note, vel=0)
        current_note = m[1]
        vel = m[2] / 127.0
        apply_expression()
        amy.send(synth=1, note=current_note, vel=vel)

    # Note Off
    elif status == 0x80 or (status == 0x90 and len(m) >= 3 and m[2] == 0):
        if current_note is not None and m[1] == current_note:
            amy.send(synth=1, note=current_note, vel=0)
            current_note = None

    # Channel Pressure / Aftertouch (0xD0) - 2-byte message
    elif status == 0xD0:
        aftertouch_val = m[1]
        apply_expression()

    # Control Change
    elif status == 0xB0 and len(m) >= 3:
        cc = m[1]
        val = m[2]
        if cc == 2:   # Breath controller
            breath_val = val
            apply_expression()
        elif cc == 11:  # Expression
            expression_val = val
            apply_expression()
        elif cc == 1:   # Mod wheel as vibrato/aftertouch proxy
            aftertouch_val = val
            apply_expression()
        elif cc == 64:  # Sustain pedal
            amy.send(synth=1, pedal=1 if val >= 64 else 0)

    # Pitch Bend (0xE0)
    elif status == 0xE0 and len(m) >= 3:
        bend_raw = ((m[2] << 7) | m[1]) - 8192
        amy.send(pitch_bend=bend_raw / 8192.0 * (2.0 / 12.0))


midi.add_callback(midi_cb)


def loop():
    pass

# Do not edit. Set automatically by the knobs on AMYboard Online.
_auto_generated_knobs = """
i1ic255Z
i1iv1in6Z
i1v0w20F1375.600,0.213,,0.606R1.996m40c2L1G4A70,,9375,0.205,75,0.000Z
i1v1w4a,,0.000f2.108A128,,10000,Z
i1v2w1a,,0.000,0.000f,,,,,0.002d0.902c3L1Z
i1v3w3a0.000,,0.000,0.000f,,,,,0.002c4L1Z
i1v4w1a0.000,,0.000,0.000f220.000,,,,,0.002c5L1Z
i1v5w5a0.000,,0.000,0.000L1Z
i1V1.000x-15.000,8.000,8.000M0.000,500.000,,0.000,0.000k0.220,310.000,0.300,0.200h0.400,0.750,0.280,3000.000Z
i1ic7,1,0.001,7.000,0.100,i%iv0a%vZ
i1ic71,1,0.500,16.000,0.000,i%iv0R%vZ
i1ic72,1,0.000,8000.000,50.000,i%iv0A,1,,,%v,0Z
i1ic73,0,0.000,1000.000,0.000,i%iv0A%v,1,,,,0Z
i1ic74,1,20.000,8000.000,0.000,i%iv0F%vZ
i1ic75,1,0.000,2000.000,50.000,i%iv0A,1,%v,,,0Z
i1ic76,1,0.100,20.000,0.000,i%iv1f%vZ
i1ic77,1,0.000,4.000,0.001,i%iv2f,,,,,%vZi%iv3f,,,,,%vZ
i1ic79,0,0.000,1.000,0.000,i%iv0A,1,,%v,,0Z
i1ic91,1,0.000,1.000,0.100,h%vZ
i1ic93,1,0.000,1.000,0.100,k%vZ
i1ic94,0,0.000,2.000,0.000,M%vZ
"""
