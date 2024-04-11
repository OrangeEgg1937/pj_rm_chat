import io
import sys
import queue
import json
import zlib
import sounddevice as sd
import threading
import time


from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtCore import Qt, QThread

from UI.Ui_mainWindow import Ui_MainWindow
from connection.data_definition import ChatHeader, ChatData
from ConnectionHandler import ConnectionHandler
from VocalSeperator import VocalSeperator

# define the sample rate
SAMPLE_RATE = 44100
swidth = 2


class SongPlayer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.audioBuffer = queue.Queue()
        self._audioOut = sd.OutputStream(channels=1, dtype='int16', samplerate=self.sample_rate, callback=None)
        self._audioOut.start()  # Start the OutputStream once
        self._audio_player_thread = threading.Thread(target=self.play_audio_from_buffer)
        self._audio_player_thread.start()

    def play_audio_from_buffer(self):
        while True:
            if not self.audioBuffer.empty():
                # get the audio data from the buffer
                audio = self.audioBuffer.get()

                # play the audio
                self._audioOut.write(audio)  # Write to the OutputStream continuously
            else:
                # if there is no audio data, wait for a short period of time
                time.sleep(0.1)


# define the Karaoke function class
class KaraokeHandler:
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, connectionHandler: ConnectionHandler):
        # initialize all the necessary objects
        self.mainWindow = mainWindow
        self.ui = ui
        self.connectionHandler = connectionHandler
        self.isPlayingSong = False
        self.single_audio_data = b''
        self.curr_file_name = "away_in_a_manger.mp3"

        # add the signal
        self.ui.karaoke_select_file.clicked.connect(self.__onUserClickSelectFile)
        self.ui.karaoke_upload_song.clicked.connect(self.__onUserUploadSong)
        self.ui.karaoke_play.clicked.connect(self.__onUserClickStartSong)
        self.ui.karaoke_stop_curr.clicked.connect(self.__onUserClickStopSong)
        self.ui.disconnect_btn.clicked.connect(self.transfer_song)

        # add the header callback
        self.connectionHandler.connect_header_callback(ChatHeader.KARAOKE_SONG_LIST, self.__onSongListReceived)
        self.connectionHandler.connect_header_callback(ChatHeader.KARAOKE_SONG, self.__onSongByteReceived)

        # start the song player thread
        self.song_player = SongPlayer(sample_rate=SAMPLE_RATE)

    def __onUserClickSelectFile(self):
        # get the user selected file path
        filePath = QFileDialog.getOpenFileName(self.mainWindow, "Select the song file", "./", "Audio Files (*.wav *.mp3)")[0]

        if filePath == "":
            return

        # set the file path to the UI
        self.ui.karaoke_path.setText(filePath)

    def __onUserUploadSong(self):
        # get the file path from user input
        file_path = self.ui.karaoke_path.text()
        # start a new thread to remove the vocal from the song
        threading.Thread(target=self.vocal_seperator_thread, args=(file_path,)).start()
        # set the tips to the UI
        self.ui.karaoke_tips.setText("Uploading, please wait...")
        # disable the upload button
        self.ui.karaoke_upload_song.setEnabled(False)
        # set the file name to server
        file_name = file_path.split("/")[-1]
        self.connectionHandler.send_data(file_name, ChatHeader.KARAOKE_SONG_NAME)

    def vocal_seperator_thread(self, file_path):
        # get the name of the file
        self.curr_file_name = file_path.split("/")[-1]
        vocal_seperator = VocalSeperator()
        vocal_seperator.seperate_file(file_path)
        vocal_seperator.output_to_file("vocal_audio/" + self.curr_file_name)
        print("Vocal removed")

    def transfer_song(self, file_path):
        # after the vocal is removed, transfer the file to the server
        with open("./vocal_audio/" + self.curr_file_name, "rb") as file:
            # flush the socket
            data = file.read()
            data = zlib.compress(data)
            # check the file size
            if sys.getsizeof(data) > 50000:
                num_of_chunks = len(data) // 50000
                self.connectionHandler.send_data(num_of_chunks, ChatHeader.KARAOKE_SONG_TRACKS)
                for i in range(0, len(data), 50000):
                    self.connectionHandler.send_data(data[i:i + 50000], ChatHeader.KARAOKE_SONG)
                    time.sleep(1)
            # enable the upload button
            self.ui.karaoke_upload_song.setEnabled(True)

    def __onSongListReceived(self, data: ChatData):
        # get the song list
        song_list = json.loads(data.data)
        # update the UI
        self.ui.karaoke_song_list.clear()

        for song in song_list:
            self.ui.karaoke_song_list.addItem(song)

    def __onSongByteReceived(self, data: ChatData):
        # disable the play button
        self.ui.karaoke_play.setEnabled(False)
        # enable the stop button
        self.ui.karaoke_stop_curr.setEnabled(True)
        # get the song data
        song_data = data.data
        # decompress the data
        decompressed_data = zlib.decompress(song_data)
        # play the song
        self.song_player.audioBuffer.put(decompressed_data)

    def __onUserClickStopSong(self):
        # stop the song
        self.song_player.audioBuffer.queue.clear()
        # enable the play button
        self.ui.karaoke_play.setEnabled(True)
        # disable the stop button
        self.ui.karaoke_stop_curr.setEnabled(False)
        # tell the server to stop the song
        self.connectionHandler.send_data("Stop the song", ChatHeader.KARAOKE_STOP)

    def __onUserClickStartSong(self):
        # get the selected song
        selected_song = self.ui.karaoke_song_list.currentItem().text()
        # send the song to the server
        self.connectionHandler.send_data(selected_song, ChatHeader.KARAOKE_START)
        # disable the play button
        self.ui.karaoke_play.setEnabled(False)

    def __onUserClickRefreshSongList(self):
        # send the request to the server
        self.connectionHandler.send_data("Request the song list", ChatHeader.KARAOKE_SONG_LIST)
        # clear the song list
        self.ui.karaoke_song_list.clear()

    def __onReceiveStopSongRequest(self, data: ChatData):
        # stop the song
        self.song_player.audioBuffer.queue.clear()
        # enable the play button
        self.ui.karaoke_play.setEnabled(True)
        # disable the stop button
        self.ui.karaoke_stop_curr.setEnabled(False)