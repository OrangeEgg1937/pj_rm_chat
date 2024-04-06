import sounddevice as sd
import numpy
assert numpy
# import pyaudio
import threading


class Audio:
    _num_channels = 1
    # _sample_format = pyaudio.paInt16
    _bit_per_sample = 16
    _sample_rate = 44100
    # _audio = pyaudio.PyAudio()
    _stream = None
    _raw_byte = b''
    _is_recording = False
    _is_paused = False

    @property
    def num_channels(self):
        return self._num_channels

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def bits_per_sample(self):
        return self._bit_per_sample

    @property
    def bytes_rate(self):
        return self.sample_rate * self.num_channels * self.bits_per_sample / 8

    @property
    def block_align(self):
        return self.num_channels * self.bits_per_sample / 8

    def __init__(self,
                 num_channel: int = 1,
                 frame_rate: int = 44100):
        if type(num_channel) is int:
            self._num_channels = max(1, num_channel)
        if type(frame_rate) is int:
            self._sample_rate = max(1, frame_rate)

    def __del__(self):
        if type(self._stream) is sd.Stream:
            self._stream.stop()
            self._stream.close()

    def start_recording(self, device: int = None):
        # if the recording is started and paused, then continue recording
        if self._is_recording and self._is_paused is True:
            print("resumed recording")
            self._is_paused = False
        else:
            self._raw_data = []
            self._stream = sd.RawInputStream(device=device, channels=self.num_channels, samplerate=self.sample_rate,
                                             callback=self._start_recording, dtype='int16')
            self._stream.start()
            self._is_recording = True

    def _start_recording(self, indata, frames, time, status):
        if self._is_recording and self._is_paused is False:
            self._raw_byte += bytes(indata)
        else:
            pass

    def pause_recording(self):
        self._is_paused = True

    def stop_recording(self):
        self._is_recording = False
        self._stream.stop()

    def generate_wav(self):
        # ChunkID (RIFF)
        content = 0x52494646.to_bytes(4, 'big')
        # ChunkSize
        content += int(36 + len(self._raw_data)).to_bytes(4, 'little')
        # Format
        content += 0x57415645.to_bytes(4, 'big')

        # Subchunk1ID (fmt-chunk)
        content += 0x666d7420.to_bytes(4, 'big')
        # Subchunk1Size (16 for PCM)
        content += int(16).to_bytes(4, 'little')
        # AudioFormat (PCM)
        content += int(1).to_bytes(2, 'little')
        # NumChannels
        content += int(self.num_channels).to_bytes(2, 'little')
        # SampleRate
        content += int(self.sample_rate).to_bytes(4, 'little')
        # ByteRate
        content += int(self.bytes_rate).to_bytes(4, 'little')
        # BlockAlign
        content += int(self.block_align).to_bytes(2, 'little')
        # BitsPerSample
        content += int(self.bits_per_sample).to_bytes(2, 'little')

        # Subchunk2ID (data-chunk)
        content += 0x64617461.to_bytes(4, 'big')
        # Subchunk2Size
        # Subchunk2Size == size of "data" subchunk = Subchunk2ID + subchunk2Size + raw data in bytes
        subchunk2Size = len(self._raw_byte) + 8
        content += int(subchunk2Size).to_bytes(4, 'little')
        # Data
        content += self._raw_byte

        return content

    def write(self, file_path: str):
        with open(file_path, "wb") as file:
            file.write(self.generate_wav())
            file.close()
