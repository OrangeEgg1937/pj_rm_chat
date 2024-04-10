class VocalSeperator():

    def __init__(self):
        from spleeter.separator import Separator
        self.separator = Separator('spleeter:2stems')
        self.filename = ""
        self.raw_data = []
        self.has_file_open = False
        self.is_seperating = False
        self.pointer = 0

    def seperate_file(self, file_path):
        import numpy as np
        from os.path import basename
        from spleeter.audio.adapter import AudioAdapter
        # set is seperating
        self.is_seperating = True
        # Load file
        audio_adapter = AudioAdapter.default()
        waveform, _ = audio_adapter.load(file_path, sample_rate=44100)
        # Run seperation
        prediction = self.separator.separate(waveform)
        raw_data = prediction["accompaniment"]
        # Turn stereo to mono
        if len(raw_data[0]) == 2:
            raw_data = (raw_data[:,0] + raw_data[:,1]) / 2
        # Map float to int
        raw_data = raw_data * (2 ** 15)
        raw_data = raw_data.astype(np.int16)
        # store to self property
        self.filename = basename(file_path)
        self.raw_data = raw_data
        # set has file open
        self.has_file_open = True
        # set is not seperating
        self.is_seperating = False

    def next_bytes(self, num_data: int):
        import numpy as np
        start = min(self.pointer, len(self.raw_data))
        end = min(self.pointer + num_data, len(self.raw_data))
        res = self.raw_data[start:end]
        if len(res) < num_data:
            res = np.append(res, np.zeros(num_data - len(res), dtype=np.int16))
        self.pointer += num_data
        return res.tobytes()

    def restart(self):
        self.pointer = 0

    @property
    def is_finished(self):
        return self.pointer >= len(self.raw_data)

    def DEBUG_output_to_file(self, file_path):
        import wave
        with wave.open(file_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            wav_file.writeframes(self.raw_data)

if __name__ == '__main__':
    separator = VocalSeperator()
    separator.seperate_file(".\raw_audio_file\song.mp3")
    separator.output_to_file(".\vocal_audio\song.wav")