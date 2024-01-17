import tkinter as tk
from tkinter import filedialog
import threading
import pyaudio
import wave
from pydub import AudioSegment
from pydub.playback import play
from PIL import Image,ImageTk,ImageSequence

class MusicApp:
    def __init__(self, master):
        self.master = master
        self.master.title("The Rhythm")
        self.master.configure(bg="#030637")
        self.is_recording = False
        self.is_playing = False
        self.recorded_frames = []
        self.autotuned_audio = None
        self.original_audio = None
        self.audio_stream = None
        self.playback_thread = None 
        self.animation_interval = 50 #milisecond
        self.animation_object = []
        
        self.create_widgets()

    def create_widgets(self):
        # Canvas for visual representation or screen
        self.canvas = tk.Canvas(self.master, bg="#3c0753", height=200, width=500,highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Recording Frame
        recording_frame = tk.Frame(self.master, padx=10, pady=10,bg="#720455")
        recording_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Record Button
        self.record_button = tk.Button(recording_frame, text="Record", command=self.toggle_recording,bg="#910A67")
        self.record_button.pack(side=tk.LEFT, padx=10)

        # Stop Recording Button
        self.stop_button = tk.Button(recording_frame, text="Stop", command=self.stop_recording, state=tk.DISABLED,bg="#910A67")
        self.stop_button.pack(side=tk.LEFT)

        # Autotune Frame
        autotune_frame = tk.Frame(self.master, padx=10, pady=10,bg="#720455")
        autotune_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Autotune Display Button
        autotune_display_button = tk.Button(autotune_frame, text="Autotune Pitch", command=self.display_autotune_pitch,bg="#910A67")
        autotune_display_button.pack(side=tk.LEFT, padx=10)

        # Original Pitch Display Button
        original_pitch_button = tk.Button(autotune_frame, text="Original Pitch", command=self.display_original_pitch,bg="#910A67")
        original_pitch_button.pack(side=tk.LEFT)

        # Playback Frame
        playback_frame = tk.Frame(self.master, padx=10, pady=10,bg="#720455")
        playback_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        # Play Autotune Button
        play_autotune_button = tk.Button(playback_frame, text="Play Autotune", command=self.play_autotune,bg="#910A67")
        play_autotune_button.pack(side=tk.LEFT, padx=10)

        # Play Original Button
        play_original_button = tk.Button(playback_frame, text="Play Original", command=self.play_original,bg="#910A67")
        play_original_button.pack(side=tk.LEFT)

        # Load GIF
        self.gif_path = "./pic.gif"  # Replace with the path to your GIF file
        self.gif = Image.open(self.gif_path)
        self.gif_frames = [ImageTk.PhotoImage(self.gif_frame) for self.gif_frame in ImageSequence.Iterator(self.gif)]

        # Display GIF on canvas
        self.gif_index = 0
        self.gif_object = self.canvas.create_image(100, 100, image=self.gif_frames[self.gif_index])
        self.animate_gif()
    
    def animate_gif(self):
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
        self.canvas.itemconfig(self.gif_object, image=self.gif_frames[self.gif_index])
        self.master.after(self.animation_interval, self.animate_gif)
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.config(text="Recording...", state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.recorded_frames = []
        self.audio_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                                    channels=1,
                                                    rate=44100,
                                                    input=True,
                                                    frames_per_buffer=1024)
        threading.Thread(target=self.record_audio).start()
        self.check_recording_status()

    def record_audio(self):
        while self.is_recording:
            data = self.audio_stream.read(1024)
            self.recorded_frames.append(data)

    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Record", state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()

        self.save_recording()

    def save_recording(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Wave files", "*.wav")])
        if file_path:
            wf = wave.open(file_path, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b"".join(self.recorded_frames))
            wf.close()

            self.original_audio = AudioSegment.from_wav(file_path)
            self.play_original()  

    def display_autotune_pitch(self):
        if self.original_audio is not None:
            
            self.autotuned_audio = self.autotune_audio(self.original_audio)
           

    def display_original_pitch(self):
       
        pass

    def play_autotune(self):
        if self.autotuned_audio is not None:
            self.stop_playback() 
            self.playback_thread = threading.Thread(target=self.play_audio, args=(self.autotuned_audio,))
            self.playback_thread.start()

    def play_original(self):
        if self.original_audio is not None:
            self.stop_playback() 
            self.playback_thread = threading.Thread(target=self.play_audio, args=(self.original_audio,))
            self.playback_thread.start()

    def stop_playback(self):
        
        if self.is_playing and self.playback_thread.is_alive():
            self.playback_thread.join()  
            self.is_playing = False

    def play_audio(self, audio):
        self.is_playing = True
        play(audio)

    def autotune_audio(self, audio):
        #Add the code for autotuning audeo here, below is just sample code
        autotuned_audio = audio.speedup(playback_speed=1.5)  
        return autotuned_audio

    def check_recording_status(self):
       
        if self.is_recording:
            self.master.after(100, self.check_recording_status)
        else:
            self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicApp(root)
    root.mainloop()
