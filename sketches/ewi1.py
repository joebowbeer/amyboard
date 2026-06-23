# AMYboard Sketch
# DESCRIPTION: Expressive EWI patch - aftertouch (channel pressure) simultaneously controls amp swell, LPF brightness, and vibrato depth; 2-osc SAW+LFO voice with portamento
# PROMPT: Program an expressive EWI (Electronic Wind Instrument) patch, given a breath sensor that transmits Aftertouch.
# For a dynamic 2-oscillator setup, route this breath-to-aftertouch signal to simultaneously control the amplifier volume,
# a low-pass filter (for brightness), and oscillator pitch (for vibrato).

import amy, midi

# Monophonic, 2 oscs per voice: osc0 = SAW carrier with LPF, osc1 = silent sine LFO for vibrato
amy.send(synth=1, num_voices=1, oscs_per_voice=2)
amy.send(synth=1, grab_midi_notes=0)

# osc1: slow sine LFO for vibrato - no vel so it stays silent, amp sets LFO depth scale
amy.send(synth=1, osc=1, wave=amy.SINE, freq=5.5, amp=1)

# osc0: sawtooth carrier - warm reed-like tone
# freq tracks MIDI note (note coeff=1), LFO vibrato (mod coeff set dynamically), plus pitch bend
# filter_freq: base opens with eg1 on attack transient; const boosted by aftertouch dynamically
# amp: vel * breath_scale * eg0 (all nonzero entries multiply together)
# bp0 (eg0 -> amp): fast attack, held sustain, medium release
# bp1 (eg1 -> filter): quick filter sweep on attack for breath puff transient
amy.send(synth=1, osc=0, wave=amy.SAW_DOWN,
         filter_type=amy.FILTER_LPF24,
         filter_freq={'const': 600, 'eg1': 1800},
         resonance=2.2,
         freq={'const': 440, 'note': 1, 'mod': 0.0, 'bend': 1},
         mod_source=1,
         amp={'vel': 1.0, 'eg0': 1},
         bp0='8,1,0,1,150,0',
         bp1='0,0,60,1,400,0',
         portamento=55)

# Global ambience
amy.send(reverb="0.4,0.72,0.25")
amy.send(chorus="0.25,310,0.35,0.18")

# State
current_note = None
aftertouch_val = 0
breath_val = 0
expression_val = 127


def apply_expression():
    at = aftertouch_val / 127.0
    br = max(breath_val, expression_val) / 127.0

    # Amplitude swell: breath scales velocity contribution (vel * breath_scale * eg0)
    breath_scale = 0.1 + br * 0.9

    # Filter cutoff: brightens with aftertouch
    cutoff = 500.0 + at * 2200.0
    res = 2.0 + at * 1.5

    # Vibrato depth: deepens with aftertouch
    vib_depth = at * 0.010

    amy.send(synth=1, osc=0,
             amp={'vel': breath_scale, 'eg0': 1},
             filter_freq={'const': cutoff, 'eg1': 1800},
             resonance=res,
             freq={'const': 440, 'note': 1, 'mod': vib_depth, 'bend': 1})


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
        if cc == 2:
            breath_val = val
            apply_expression()
        elif cc == 11:
            expression_val = val
            apply_expression()
        elif cc == 1:
            aftertouch_val = val
            apply_expression()
        elif cc == 64:
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
i1iv1in2Z
i1v0w2F600.000,,,,1800.000R2.200m58L1G4A8,,,1.000,150,0.000B0,0.000,60,1.000,400,0.000Z
i1v1a,,0.000f5.500Z
i1V1.000x0.000,0.000,0.000M0.000,500.000,1365.333,0.000,0.000k0.250,310.000,0.350,0.180h0.400,0.720,0.250,3000.000Z
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
