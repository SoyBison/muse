from abc import ABC, abstractmethod
import math

class Oscillator(ABC):
    def __init__(self, freq=440, phase=0, amp=1, sample_rate=44100, wave_range=(-1, 1)):
        self._freq = freq
        self._amp = amp
        self._phase = phase
        self._sample_rate = sample_rate
        self._wave_range = wave_range

        self._f = freq
        self._a = amp
        self._p = phase
        self._initialize_osc()
        self.freq = self._freq
        self.phase = self._phase
        self.amp = self._amp

    @property
    def init_freq(self):
        return self._freq

    @property
    def init_amp(self):
        return self._amp

    @property
    def init_phase(self):
        return self._phase
    
    @property
    def freq(self):
        return self._f
    
    @freq.setter
    def freq(self, value):
        self._f = value
        self._post_freq_set()
        
    @property
    def amp(self):
        return self._a
    
    @amp.setter
    def amp(self, value):
        self._a = value
        self._post_amp_set()
        
    @property
    def phase(self):
        return self._p
    
    @phase.setter
    def phase(self, value):
        self._p = value
        self._post_phase_set()
    
    def _post_freq_set(self):
        pass
    
    def _post_amp_set(self):
        pass
    
    def _post_phase_set(self):
        pass
    
    @abstractmethod
    def _initialize_osc(self):
        raise NotImplemented
    
    @staticmethod
    def squish_val(val, min_val=0, max_val=1):
        return (((val + 1) / 2 ) * (max_val - min_val)) + min_val

    @abstractmethod
    def __next__(self):
        return None
    
    def __iter__(self):
        self.freq = self._freq
        self.phase = self._phase
        self.amp = self._amp
        return self

    def __add__(self, other):
        return CombinedOscillator(self, other)

class CombinedOscillator(Oscillator):
    def __init__(self, oa: Oscillator, ob: Oscillator):
        self._oa = oa
        self._ob = ob
        self._oa._initialize_osc()
        self._ob._initialize_osc()
        self._freq = None
        self._phase = None
        self._amp = None
        self._f = None
        self._p = None
        self._a = None

        wave_ranges = list(self._oa._wave_range) + list(self._ob._wave_range)
        self._wave_range = (min(wave_ranges), max(wave_ranges))
        self._a_range = self._oa._wave_range[1] - self._oa._wave_range[0]
        self._b_range = self._ob._wave_range[1] - self._ob._wave_range[0]
        self._new_range = self._wave_range[1] - self._wave_range[0]
        self.n_children = 2
        if isinstance(self._oa, CombinedOscillator):
            self.n_children -= 1
            self.n_children += self._oa.n_children
        if isinstance(self._ob, CombinedOscillator):
            self.n_children -= 1
            self.n_children += self._ob.n_children

    def _initialize_osc(self):
        self._oa._initialize_osc()
        self._ob._initialize_osc()

    def __next__(self):
        adj_a = (((next(self._oa) - self._oa._wave_range[0]) * self._new_range) / self._a_range) + self._wave_range[0]
        adj_b = (((next(self._ob) - self._ob._wave_range[0]) * self._new_range) / self._b_range) + self._wave_range[0]
        if isinstance(self._oa, CombinedOscillator):
            adj_a *= self._oa.n_children
        if isinstance(self._ob, CombinedOscillator):
            adj_b *= self._ob.n_children
        return (adj_a + adj_b) / self.n_children
        

class SineOscillator(Oscillator):
    def _post_freq_set(self):
        self._step = (2 * math.pi * self._f) / self._sample_rate
        
    def _post_phase_set(self):
        self._p = (self._p / 360) * 2 * math.pi
        
    def _initialize_osc(self):
        self._i = 0
        
    def __next__(self):
        val = math.sin(self._i + self._p)
        self._i = self._i + self._step
        if self._wave_range is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a

class SquareOscillator(SineOscillator):
    def __init__(self, freq=440, phase=0, amp=1, \
                 sample_rate=44_100, wave_range=(-1, 1), threshold=0):
        super().__init__(freq, phase, amp, sample_rate, wave_range)
        self.threshold = threshold
    
    def __next__(self):
        val = math.sin(self._i + self._p)
        self._i = self._i + self._step
        if val < self.threshold:
            val = self._wave_range[0]
        else:
            val = self._wave_range[1]
        return val * self._a

class SawtoothOscillator(Oscillator):
    def _post_freq_set(self):
        self._period = self._sample_rate / self._f
        self._post_phase_set
        
    def _post_phase_set(self):
        self._p = ((self._p + 90)/ 360) * self._period
    
    def _initialize_osc(self):
        self._i = 0
    
    def __next__(self):
        div = (self._i + self._p )/self._period
        val = 2 * (div - math.floor(0.5 + div))
        self._i = self._i + 1
        if self._wave_range is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a

class TriangleOscillator(SawtoothOscillator):
    def __next__(self):
        div = (self._i + self._p)/self._period
        val = 2 * (div - math.floor(0.5 + div))
        val = (abs(val) - 0.5) * 2
        self._i = self._i + 1
        if self._wave_range is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a
