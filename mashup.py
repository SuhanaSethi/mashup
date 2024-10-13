import os
import time
import tkinter as tk
from tkinter import messagebox, filedialog
import yt_dlp
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

class MashupCreator:
    def __init__(self, master):
        self.master = master
        self.master.title("YouTube Mashup Creator")


        tk.Label(master, text="Enter Singer Name:").pack()
        self.singer_name_entry = tk.Entry(master)
        self.singer_name_entry.pack()


        tk.Label(master, text="Number of Videos to Download:").pack()
        self.num_videos_entry = tk.Entry(master)
        self.num_videos_entry.pack()


        tk.Label(master, text="Duration of Each Clip (seconds):").pack()
        self.clip_duration_entry = tk.Entry(master)
        self.clip_duration_entry.pack()


        tk.Label(master, text="Select Save Directory:").pack()
        self.save_dir_entry = tk.Entry(master)
        self.save_dir_entry.pack()
        tk.Button(master, text="Browse", command=self.browse_directory).pack()


        self.create_button = tk.Button(master, text="Create Mashup", command=self.create_mashup)
        self.create_button.pack()

        self.status_label = tk.Label(master, text="", fg="green")
        self.status_label.pack()

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(0, directory)

    def download_videos(self, singer, number_of_videos):
        download_path = self.save_dir_entry.get()
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'quiet': True,
            'ffmpeg_location': r'C:\ffmpeg\bin',  
        }

        search_url = f"ytsearch{number_of_videos}:{singer}"
        print(f"Downloading videos for: {search_url}")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(search_url, download=True)
                return [entry['title'] + ".mp4" for entry in result.get('entries', [])]
        except Exception as e:
            messagebox.showerror("Error", f"Error downloading videos: {str(e)}")
            return []

    def convert_video_to_audio(self, video_file_path):
        """Convert video to audio and handle errors."""
        if not os.path.exists(video_file_path):
            raise FileNotFoundError(f"Video file not found: {video_file_path}")

        audio_file_path = os.path.splitext(video_file_path)[0] + ".mp3"
        try:
            video_clip = VideoFileClip(video_file_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_file_path)
            audio_clip.close()
            video_clip.close()
            os.remove(video_file_path) 
            return audio_file_path
        except Exception as e:
            messagebox.showerror("Error", f"Error converting video to audio: {str(e)}")
            return None

    def cut_audio_segment(self, audio_file_path, duration):
        """Cut audio to the specified duration."""
        try:
            audio = AudioSegment.from_file(audio_file_path)
            cut_audio = audio[:duration * 1000] 
            cut_audio.export(audio_file_path, format="mp3")
            return audio_file_path
        except Exception as e:
            messagebox.showerror("Error", f"Error cutting audio: {str(e)}")
            return None

    def merge_audio_files(self, audio_file_paths):
        """Merge multiple audio files into one."""
        combined = AudioSegment.empty()
        for file_path in audio_file_paths:
            try:
                audio = AudioSegment.from_file(file_path)
                combined += audio
            except Exception as e:
                messagebox.showerror("Error", f"Error merging audio files: {str(e)}")
        return combined

    def create_mashup(self):
        """Main function to create the mashup."""
        singer = self.singer_name_entry.get()
        number_of_videos = self.num_videos_entry.get()
        duration = self.clip_duration_entry.get()

        if not singer or not number_of_videos or not duration:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        try:
            number_of_videos = int(number_of_videos)
            duration = int(duration)
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter valid numbers.")
            return

        self.status_label.config(text="Downloading videos...")
        self.master.update()

      
        video_files = self.download_videos(singer, number_of_videos)
        if not video_files:
            messagebox.showerror("Error", "No videos downloaded. Check the singer name or try again.")
            return

        audio_file_paths = []
        download_path = self.save_dir_entry.get()


        for file_name in video_files:
            video_file_path = os.path.join(download_path, file_name)
            print(f"Processing: {video_file_path}")

            audio_file_path = self.convert_video_to_audio(video_file_path)
            if audio_file_path:
                cut_audio_path = self.cut_audio_segment(audio_file_path, duration)
                if cut_audio_path:
                    audio_file_paths.append(cut_audio_path)


        if audio_file_paths:
            merged_audio = self.merge_audio_files(audio_file_paths)
            output_file = os.path.join(download_path, "mashup_audio.mp3")
            merged_audio.export(output_file, format="mp3")
            messagebox.showinfo("Success", f"Mashup created and saved as {output_file}")
        else:
            messagebox.showerror("Error", "No audio clips to merge.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MashupCreator(root)
    root.mainloop()
