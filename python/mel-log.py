#!/usr/bin/env python3
#

import wave
import numpy as np
from numpy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import matplotlib
#matplotlib.use('Agg')


def hz_to_mel(hz):
    return 2595 * np.log10(1 + hz / 700)

def mel_to_hz(mel):
    return 700 * (10**(mel / 2595) - 1)

def read_wav(file_path):
    wav_int = []
    with wave.open(file_path, 'rb') as wav_file:
        n_channels = wav_file.getnchannels()
        sampwidth = wav_file.getsampwidth()
        samplerate= wav_file.getframerate()
        n_frames = wav_file.getnframes()

        print(f"Channels: {n_channels}, Sample Width (bytes): {sampwidth}, Sampling Freq(Hz): {samplerate}, No Of Samples: {n_frames}")

        if sampwidth != 1:
            raise ValueError("This script only supports 8-bit PCM data.")

        ## Read the wav data as 
        wav_data = wav_file.readframes(n_frames)

    for byte in wav_data:
        wav_int.append(byte)

    return (samplerate, wav_int)


def premph(signal, alpha=1.0):
    '''
    Premphasis Filter (aka HPF): y(n) = x(n) - alpha * x(n-1)
    '''
    yn = np.zeros(len(signal))
    yn[0] = signal[0]
    for i in ((np.arange(len(signal)-1))+1):
        yn[i] = signal[i] - (alpha * signal[i-1])

    return yn

def running_fft(signal, framesize=64, overlap=32):
    '''
    '''
    spectogram = []
    stepsize = framesize - overlap
    signal_len = len(signal)
    total_steps = int(signal_len/stepsize) - 4
    #
    for i in np.arange(total_steps):
        #print(f"start:{i*stepsize} stop:{i*stepsize + framesize -1}")
        frame = signal[i*stepsize:(i*stepsize + framesize -1)]
        frame_win = np.hanning(len(frame)) * frame
        #frame_win = frame
        fft_vals = fft(frame_win)
        fft_mag  = np.abs(fft_vals)
        #print(f"{fft_mag[0:15]}")
        spectogram.append(fft_mag[0:int(0.5*framesize)])

    return spectogram

def get_mel_filter_bank(num_filters, NFFT, Fs):
    # Define the frequency range
    low_freq_mel = hz_to_mel(0)
    high_freq_mel = hz_to_mel(Fs / 2)
    
    # Compute the Mel frequencies
    mel_points = np.linspace(low_freq_mel, high_freq_mel, num_filters + 2)
    hz_points = mel_to_hz(mel_points)
    
    # Convert frequencies to FFT bin numbers
    bin_points = np.floor((NFFT + 1) * hz_points / Fs).astype(int)
    
    # Create the filter bank
    filter_bank = np.zeros((num_filters, int(NFFT / 2 + 1)))
    
    for i in range(1, num_filters + 1):
        left = bin_points[i - 1]
        center = bin_points[i]
        right = bin_points[i + 1]
        
        for j in range(left, center):
            filter_bank[i - 1, j] = (j - bin_points[i - 1]) / (bin_points[i] - bin_points[i - 1])
        for j in range(center, right):
            filter_bank[i - 1, j] = (bin_points[i + 1] - j) / (bin_points[i + 1] - bin_points[i])
    
    return filter_bank

if __name__ == "__main__":

   (fs, wav_int) = read_wav("hello_4K_8b.wav")
   #plt.plot(wav_int)
   #plt.show()
   wav_int = premph(wav_int)
   spectogram = running_fft(wav_int)
   spectogram_arr = np.array(spectogram)
   plt.imshow(spectogram_arr.T, aspect='auto', origin='lower', interpolation='nearest')
   plt.show()
#    test = np.arange(0, 100, 1)
#    plt.plot(test)
#    plt.show()
#    plt.savefig('plot.png')
#    print(f"Type = {type(wav_data)}")
#    plt.plot(wav_int)
#    plt.show()

#  x = np.ones(32)
#  xham = x * np.hamming(len(x))

#  plt.plot(xham)
#  plt.show()
