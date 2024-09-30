import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt

# print(sd.query_devices(kind='output'))

# dl = sd.query_devices(kind='output')

# print(f'len(dl) is {len(dl)}')

# print(sd.query_devices())

# dl = sd.query_devices()

# print(f'len(dl) is {len(dl)}')

n_channels = 2
sample_rate = 48000
try:
    sd.check_output_settings(channels=n_channels, samplerate=sample_rate)
except Exception as E:
    print('Not found')
    exit(-1)

print(f'Device with n_channels: {n_channels} and sample_rate: {sample_rate}')


tone_frequency_hz = 1000
noise_type = 'white'
n_output_channels = 2

signal_duration = 1
pre_delay = 0.2
post_delay = 0.2
fade_duration = 0.1

fixed_noise_pow_db = -20
target_snr_db = 3

sig_len = np.round(signal_duration * sample_rate).astype(int)
pre_pad_len = np.round(pre_delay * sample_rate).astype(int)
post_pad_len = np.round(post_delay * sample_rate).astype(int)
stimulus_len = pre_pad_len + sig_len + post_pad_len
win_len = np.floor(fade_duration * sample_rate).astype(int)

win = 1/2 * (1-np.cos(2 * np.pi * np.arange(win_len) / (2*win_len)))


# Generate noise
rng = np.random.default_rng()
noise = rng.standard_normal(size=(stimulus_len,))
noise_pow = 10*np.log10(np.mean(np.square(noise)))
print(f'As generated noise pow [dB]: {noise_pow}')

noise_gain = np.power(10,(fixed_noise_pow_db - noise_pow)/20)
noise *= noise_gain

noise_pow = 10*np.log10(np.mean(np.square(noise)))
print(f'Scaled noise pow [dB]: {noise_pow}')

noise[0:win_len] *= win
noise[-win_len:] *= win[::-1]

# Generate signal
t_sig = np.arange(sig_len) / sample_rate
signal = np.sin(2 * np.pi * tone_frequency_hz * t_sig)
signal_pow = 10*np.log10(np.mean(np.square(signal)))

print(f'As generated signal pow [dB]: {signal_pow}')
signal_gain = np.power(10,(noise_pow + target_snr_db - signal_pow)/20)
signal *= signal_gain

signal_pow = 10*np.log10(np.mean(np.square(signal)))
print(f'Scaled signal pow [dB]: {signal_pow}')

signal[0:win_len] *= win
signal[-win_len:] *= win[::-1]

padded_signal = np.zeros((stimulus_len,))
padded_signal[pre_pad_len:(pre_pad_len+sig_len)] += signal
mix = padded_signal + noise




# sd.default.device = 46 #  46 Analog (9+10) (RME Fireface 800), Windows DirectSound (0 in, 2 out)
# sd.default.device = 116 #  46 Analog (9+10) (RME Fireface 800), Windows DirectSound (0 in, 2 out)

#sd.default.blocksize = 1024
sd.play(mix, sample_rate)
sd.wait()


fig,ax = plt.subplots(2,2)
ax[0,0].plot(win)
ax[0,1].plot(mix)
ax[1,0].plot(signal)
ax[1,1].plot(noise)


fig.show()

print('Hit any key to exit.')
input()
