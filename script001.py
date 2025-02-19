import numpy as np
import pandas as pd
from scipy.io import wavfile
import scipy.signal as signal

# Load your data
data = pd.read_csv('/Users/dg/Documents/CODING/mold_wip/data_z.csv')  # Using just Z coordinates
# Or data = pd.read_csv('data_full.csv')  # Using XZ coordinates

# Audio settings - exactly 3 minutes at 44.1kHz
sample_rate = 44100
duration_seconds = 180  # 3 minutes
total_samples = sample_rate * duration_seconds
audio = np.zeros(total_samples)

# Map each frame to the correct audio position
for _, row in data.iterrows():
    frame = row['frame']
    z_value = row['z_coordinate']
    
    # Calculate exact position in audio timeline
    sample_position = int((frame-1) * total_samples / 4321)
    
    # Map Z value to frequency (55Hz to 880Hz - two octaves)
    # -5.31 → 55Hz, 0.65 → 880Hz
    normalized_z = (z_value + 5.31) / 5.96  # Normalize to 0-1
    frequency = 55 * (2 ** (normalized_z * 4))  # 4 octaves range
    
    # Generate a short tone at this position
    # Frame duration = 1/24 sec = ~1833 samples at 44.1kHz
    frame_samples = int(sample_rate / 24)
    
    # Generate sine wave for this frame
    t = np.linspace(0, 1/24, frame_samples, False)
    tone = 0.3 * np.sin(2 * np.pi * frequency * t)
    
    # Apply envelope to avoid clicks
    envelope = np.hanning(frame_samples)
    tone = tone * envelope
    
    # Add to main audio at correct position
    end_pos = min(sample_position + frame_samples, total_samples)
    audio[sample_position:end_pos] += tone[:end_pos-sample_position]

# Normalize audio
audio = audio / np.max(np.abs(audio)) * 0.95

# Write to WAV file
wavfile.write('/Users/dg/Documents/CODING/mold_wip/audio001.wav', sample_rate, audio.astype(np.float32))