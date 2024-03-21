#!/usr/bin/env python

from itertools import product
from lib.oscillator import SineOscillator
from scipy.io import wavfile
import numpy as np
import math

from random import uniform, choice

def main():
    rate = 44100
    samples = []
    # US RINGING TONE
    osc = SineOscillator(440) + SineOscillator(480)
    for i in range(10):
        for t in range(rate * 2):
            samples.append(next(osc))
        for t in range(rate * 4):
            samples.append(0)
    samples = np.array(samples)
    samples = np.int16(samples / np.max(np.abs(samples)) * 32767)

    wavfile.write('US_ringing_synth.wav', rate, np.array(samples, dtype=np.int16))

    # ESTI RINGING TONE
    samples = []
    osc = SineOscillator(425)
    for i in range(10):
        for t in range(rate * 1):
            samples.append(next(osc))
        for t in range(rate * 3):
            samples.append(0)
    samples = np.array(samples)
    samples = np.int16(samples / np.max(np.abs(samples)) * 32767)

    wavfile.write('ETSI_Ringing_synth.wav', rate, np.array(samples, dtype=np.int16))

    # GPO RINGING TONE
    samples = []
    osc = SineOscillator(400) + SineOscillator(450)
    for i in range(10):
        for t in range(math.floor(rate * 0.4)):
            samples.append(next(osc))
        for t in range(math.floor(rate * 0.2)):
            samples.append(0)
        for t in range(math.floor(rate * 0.4)):
            samples.append(next(osc))
        for t in range(math.floor(rate * 2)):
            samples.append(0)
    samples = np.array(samples)
    samples = np.int16(samples / np.max(np.abs(samples)) * 32767)

    wavfile.write('GPO_ringing_synth.wav', rate, np.array(samples, dtype=np.int16))

    # NA DIAL TONE
    samples = []
    osc = SineOscillator(350) + SineOscillator(450)
    for i in range(20 * rate):
        samples.append(next(osc))
    samples = np.array(samples)
    samples = np.int16(samples / np.max(np.abs(samples)) * 32767)

    wavfile.write('NA_dial_synth.wav', rate, np.array(samples, dtype=np.int16))

    # ETSI DIAL TONE
    samples = []
    osc = SineOscillator(425)
    for i in range(20 * rate):
        samples.append(next(osc))
    samples = np.array(samples)
    samples = np.int16(samples / np.max(np.abs(samples)) * 32767)

    wavfile.write('ESTI_dial_synth.wav', rate, np.array(samples, dtype=np.int16))

    # GPO DIAL TONE
    samples = []
    osc = SineOscillator(350) + SineOscillator(450)
    for i in range(20 * rate):
        samples.append(next(osc))
    samples = np.array(samples)
    samples = np.int16(samples / np.max(np.abs(samples)) * 32767)

    wavfile.write('GPO_dial_synth.wav', rate, np.array(samples, dtype=np.int16))

    # DTMF
    # X axis
    oa = SineOscillator(1209)
    ob = SineOscillator(1336)
    oc = SineOscillator(1477)
    # Y axis
    o1 = SineOscillator(697)
    o2 = SineOscillator(770)
    o3 = SineOscillator(852)
    o4 = SineOscillator(941)

    osc_prod = product([oa, ob, oc], [o1, o2, o3, o4])
    dtones = list(map(lambda t: t[0] + t[1], osc_prod))
    samples = []
    for i in range(120):
        osc = choice(dtones)
        for t in range(math.floor(rate * uniform(0.2, 0.4))):
            samples.append(next(osc))
        for t in range(math.floor(rate * uniform(0.05, 0.2))):
            samples.append(0)
    samples = np.array(samples)
    samples = np.int16(samples / np.max(np.abs(samples)) * 32767)

    wavfile.write('DTMF.wav', rate, np.array(samples, dtype=np.int16))


if __name__ == "__main__":
    main()
