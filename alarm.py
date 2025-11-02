import pygame

def play_alarm_sound():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("alarm.wav")
        pygame.mixer.music.play()
    except Exception as e:
        print("Error playing alarm:", e)
