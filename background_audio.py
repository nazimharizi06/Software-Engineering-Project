import pygame
import board
from pathlib import Path

MUSIC_DIR = Path(__file__).parent / "audio" / "music"

TRACKS = {
    "campus": MUSIC_DIR / "upbeat.mp3",
    "kunsela": MUSIC_DIR / "scifi.mp3",
    "menu": MUSIC_DIR / "suspense.mp3",
}

class BackgroundAudio:
    def __init__(self):
        self.current_track = None
        
    def play_for(self, stage):
        track = TRACKS[stage]
        if track == self.current_track:
            return
        
        pygame.mixer.music.load(str(track))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.current_track = track
        