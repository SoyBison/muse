#!/usr/bin/env python

from functools import reduce
from itertools import islice, chain
from operator import add
from typing import Iterator

from librosa import note_to_hz
from matplotlib import pyplot as plt
import numpy as np
import pyaudio

from lib.oscillator import *

SR = 44100
WIN = 256

def make_seq(osc: Oscillator, notes, lens):
    samples = []
    for note, note_len in zip(notes, lens):
        osc.freq = note_to_hz(note)
        for _ in range(int(SR * note_len)):
            samples.append(next(osc))
    return iter(samples)

def write_from_iter(it: Iterator, player: pyaudio.Stream, limit=None):
    i = 0 
    while True:
        chunk = list(islice(it, WIN))
        if not chunk: break
        player.write(np.array(chunk, dtype=np.float32), WIN)
        i += 1
        if limit and i > limit * SR / WIN:
            break

def combine_sequences(*sequences):
    return ((sum(s) / len(s) for s in zip(*sequences)))

def notes2seqdef(notes, repeats, tempo=1):
    l = [tempo/len(notes)] * len(notes)
    s = notes * repeats
    l *= repeats
    return s, l

def main():
    client = pyaudio.PyAudio()
    player = client.open(format=pyaudio.paFloat32, channels=1, rate=SR, output=True, frames_per_buffer=WIN)
    # Melody
    s1 = ["C4", "Eb4", "G4", "Bb4"]
    # Prog
    s2 = ["C2",  "Ab3", "Eb2", "Bb3"]
    s3 = ["Eb2", "C3",  "G2",  "D3"]
    s4 = ["G2",  "Eb3", "Bb3", "F3"]
    seq1a = make_seq(TriangleOscillator(), *notes2seqdef(s1, 4))
    seq1b  = make_seq(TriangleOscillator(), *notes2seqdef(list(reversed(s1)), 4))
    seq1 = chain(seq1a, seq1b)
    seq2 = make_seq(SineOscillator(), *notes2seqdef(s2, 2, tempo=4))
    seq3 = make_seq(SineOscillator(), *notes2seqdef(s3, 2, tempo=4))
    seq4 = make_seq(SineOscillator(), *notes2seqdef(s4, 2, tempo=4))
    seqf = combine_sequences(seq1, seq2, seq3, seq4)

    write_from_iter(seqf, player)

    client.terminate()



if __name__ == "__main__":
    main()
