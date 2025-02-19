import numpy as np
import pandas as pd
from scipy.io import wavfile
import scipy.signal as signal

# Load the full data with X, Y, Z coordinates
data = pd.read_csv('/Users/dg/Documents/CODING/mold_wip/data_full.csv')

# Audio settings - exactly 10 minutes at 44.1kHz
sample_rate = 44100
duration_seconds = 600  # 10 minutes
total_samples = sample_rate * duration_seconds

# Create stereo audio array - shape: [samples, channels]
audio = np.zeros((total_samples, 2), dtype=np.float32)

# Function to generate a waveform that morphs between sine and sawtooth
def morph_wave(t, frequency, morph_factor):
    """
    Generate a wave that morphs between sine (morph_factor=0) and sawtooth (morph_factor=1)
    t: time array
    frequency: frequency of the wave
    morph_factor: 0.0 (pure sine) to 1.0 (pure sawtooth)
    """
    # Generate pure sine wave
    sine_wave = np.sin(2 * np.pi * frequency * t)
    
    # Generate sawtooth wave (normalized to same amplitude)
    saw_wave = signal.sawtooth(2 * np.pi * frequency * t)
    
    # Morphed wave is a weighted combination
    return sine_wave * (1 - morph_factor) + saw_wave * morph_factor

# Calculate data ranges once
z_min = data['z_coordinate'].min()
z_max = data['z_coordinate'].max()
z_range = z_max - z_min

x_min = data['x_coordinate'].min()
x_max = data['x_coordinate'].max()
x_range = x_max - x_min

y_min = data['y_coordinate'].min()
y_max = data['y_coordinate'].max()
y_range = y_max - y_min

# Map each frame to the correct audio position - adjusted for 14401 frames
for _, row in data.iterrows():
    frame = row['frame']
    z_value = row['z_coordinate']
    x_value = row['x_coordinate']
    y_value = row['y_coordinate']
    
    # Calculate exact position in audio timeline - updated for 14401 frames
    sample_position = int((frame-1) * total_samples / 14401)
    
    # Map Z value to frequency (55Hz to 880Hz) - with dynamic range
    normalized_z = (z_value - z_min) / z_range  # Normalize to 0-1
    frequency = 55 * (2 ** (normalized_z * 4))  # 4 octaves range
    
    # Use Y coordinate to control wave shape morphing
    # As Y goes from start to end (high to low), wave morphs from sine to sawtooth
    normalized_y = 1 - (y_value - y_min) / y_range  # Invert so it increases over time
    morph_factor = normalized_y  # 0.0 (sine) to 1.0 (sawtooth)
    
    # Calculate panning from X coordinates - with dynamic range
    pan_position = (x_value - x_min) / x_range
    
    # Ensure pan_position is within 0-1 range (handle outliers)
    pan_position = max(0, min(1, pan_position))
    
    # Calculate stereo gains using equal power panning law
    left_gain = np.cos(pan_position * np.pi/2)
    right_gain = np.sin(pan_position * np.pi/2)
    
    # Generate a short tone for this frame
    # Frame duration = 1/24 sec = ~1833 samples at 44.1kHz
    frame_samples = int(sample_rate / 24)
    
    # Generate time array for this frame
    t = np.linspace(0, 1/24, frame_samples, False)
    
    # Generate morphed waveform
    tone = 0.3 * morph_wave(t, frequency, morph_factor)
    
    # Apply envelope to avoid clicks
    envelope = np.hanning(frame_samples)
    tone = tone * envelope
    
    # Apply stereo panning
    end_pos = min(sample_position + frame_samples, total_samples)
    samples_to_add = end_pos - sample_position
    
    # Add to left and right channels with appropriate panning
    if samples_to_add > 0 and samples_to_add <= len(tone):
        audio[sample_position:end_pos, 0] += tone[:samples_to_add] * left_gain
        audio[sample_position:end_pos, 1] += tone[:samples_to_add] * right_gain

# Add secondary tone based on X coordinate changes - now with triangle wave
for _, row in data.iterrows():
    frame = row['frame']
    x_value = row['x_coordinate']
    z_value = row['z_coordinate']
    
    # Calculate sample position - updated for 14401 frames
    sample_position = int((frame-1) * total_samples / 14401)
    
    # Map X to a higher frequency range (more "tinkly" sound)
    normalized_x = (x_value - x_min) / x_range
    x_frequency = 1200 + normalized_x * 1200
    
    # Make X-based sound quieter than main Z sound
    x_amplitude = 0.1 * abs(x_value - np.mean([x_min, x_max])) / (x_range/2)
    
    # Generate a shorter sound for X (more percussive)
    frame_samples = int(sample_rate / 48)  # Half frame duration
    t = np.linspace(0, 1/48, frame_samples, False)
    
    # Use triangle wave for secondary tone for contrast
    x_tone = x_amplitude * signal.sawtooth(2 * np.pi * x_frequency * t, 0.5)  # 0.5 duty cycle = triangle
    
    # Apply quick envelope (percussive attack)
    x_envelope = np.exp(-5 * np.linspace(0, 1, frame_samples))
    x_tone = x_tone * x_envelope
    
    # Pan opposite to the main sound for interesting stereo field
    inverse_pan = 1 - ((x_value - x_min) / x_range)
    inverse_pan = max(0, min(1, inverse_pan))
    x_left_gain = np.cos(inverse_pan * np.pi/2) 
    x_right_gain = np.sin(inverse_pan * np.pi/2)
    
    # Add to audio
    end_pos = min(sample_position + frame_samples, total_samples)
    samples_to_add = end_pos - sample_position
    
    if samples_to_add > 0 and samples_to_add <= len(x_tone):
        audio[sample_position:end_pos, 0] += x_tone[:samples_to_add] * x_left_gain
        audio[sample_position:end_pos, 1] += x_tone[:samples_to_add] * x_right_gain

# Find significant peaks and valleys in Z coordinates for percussion
z_values = data['z_coordinate'].values
# Adjust prominence based on Z range
z_prominence = z_range * 0.08  # Scale prominence to 8% of total range

peaks, _ = signal.find_peaks(z_values, prominence=z_prominence, distance=24)
valleys, _ = signal.find_peaks(-z_values, prominence=z_prominence, distance=24)

# Add percussive elements with varied timbres based on position
for peak in peaks:
    if peak < len(data):
        # High percussion at z peaks
        sample_pos = int(peak * total_samples / 14401)
        
        # Create a short "click" sound
        click_len = int(sample_rate * 0.01)
        t = np.linspace(0, 0.01, click_len, False)
        
        # Vary percussion timbre based on position in sequence
        position_factor = peak / len(data)
        
        # Morph percussion from sine to noise
        base_freq = 3000 + position_factor * 2000  # Increase frequency over time
        noise_factor = position_factor * 0.5  # Add more noise over time
        
        # Generate percussion sound
        pure_tone = np.sin(2 * np.pi * base_freq * t)
        noise = np.random.uniform(-1, 1, len(t))
        click = 0.2 * ((1-noise_factor) * pure_tone + noise_factor * noise)
        
        # Apply envelope
        env = np.exp(-20 * np.linspace(0, 1, click_len))
        click = click * env
        
        # Add click centered in stereo field
        end_click = min(sample_pos + click_len, total_samples)
        samples_to_add = end_click - sample_pos
        if samples_to_add > 0 and samples_to_add <= len(click):
            audio[sample_pos:end_click, 0] += click[:samples_to_add] * 0.7
            audio[sample_pos:end_click, 1] += click[:samples_to_add] * 0.7

for valley in valleys:
    if valley < len(data):
        # Low percussion at z valleys
        sample_pos = int(valley * total_samples / 14401)
        
        # Create a short "thump" sound
        thump_len = int(sample_rate * 0.03)
        t = np.linspace(0, 0.03, thump_len, False)
        
        # Vary percussion timbre based on position
        position_factor = valley / len(data)
        base_freq = 80 - position_factor * 30  # Lower frequency over time
        
        # Morph from pure sine to rich harmonic content
        fundamental = np.sin(2 * np.pi * base_freq * t)
        harmonic1 = 0.5 * np.sin(2 * np.pi * base_freq * 2 * t)
        harmonic2 = 0.25 * np.sin(2 * np.pi * base_freq * 3 * t)
        
        # Mix harmonics based on position
        thump = 0.3 * (fundamental + position_factor * (harmonic1 + harmonic2))
        
        # Apply envelope
        env = np.exp(-10 * np.linspace(0, 1, thump_len))
        thump = thump * env
        
        # Add thump centered in stereo field
        end_thump = min(sample_pos + thump_len, total_samples)
        samples_to_add = end_thump - sample_pos
        if samples_to_add > 0 and samples_to_add <= len(thump):
            audio[sample_pos:end_thump, 0] += thump[:samples_to_add] * 0.8
            audio[sample_pos:end_thump, 1] += thump[:samples_to_add] * 0.8

# Add subtle filter sweep based on overall progress
print("Applying filter sweep effect...")
for i in range(0, total_samples, sample_rate):  # Process in 1-second chunks
    chunk_end = min(i + sample_rate, total_samples)
    progress = i / total_samples
    
    # Simple lowpass filter simulation that opens up over time
    if progress < 0.1:  # First 10% - more filtered
        cutoff_freq = 500 + progress * 10 * 1000  # 500Hz to 1500Hz
    else:  # Rest - gradually open filter
        cutoff_freq = 1500 + (progress - 0.1) * (20000 - 1500) / 0.9
        
    # Apply filter (simple approximation)
    if i > 0:  # Skip first chunk to avoid startup issues
        chunk_size = chunk_end - i
        window = np.hamming(chunk_size)
        audio[i:chunk_end, 0] = audio[i:chunk_end, 0] * window
        audio[i:chunk_end, 1] = audio[i:chunk_end, 1] * window

# Normalize audio to avoid clipping
max_val = np.max(np.abs(audio))
if max_val > 0:
    audio = audio / max_val * 0.95

# Apply subtle reverb for more depth
def apply_simple_reverb(audio, decay=0.6, delay=int(44100 * 0.05)):
    # Very simple reverb implementation
    output = audio.copy()
    for i in range(delay, len(output)):
        output[i] += audio[i - delay] * decay
    return output

# Apply to both channels
print("Applying reverb to left channel...")
audio[:, 0] = apply_simple_reverb(audio[:, 0])
print("Applying reverb to right channel...")
audio[:, 1] = apply_simple_reverb(audio[:, 1])

# Normalize again after reverb
max_val = np.max(np.abs(audio))
if max_val > 0:
    audio = audio / max_val * 0.95

# Write to WAV file
output_path = '/Users/dg/Documents/CODING/mold_wip/audio003_morphing_10min.wav'
print(f"Saving audio to {output_path}...")
wavfile.write(output_path, sample_rate, audio)

print(f"Created 10-minute stereo audio file with {len(peaks)} peaks and {len(valleys)} valleys")
print(f"Wave morphing: Sine → Sawtooth based on Y-coordinate progression")
print(f"X-coordinate range used for panning: {x_min:.2f} to {x_max:.2f}")
print(f"Y-coordinate range used for morphing: {y_min:.2f} to {y_max:.2f}")
print(f"Z-coordinate range used for pitch: {z_min:.2f} to {z_max:.2f}")