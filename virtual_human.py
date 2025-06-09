import pyttsx3
import pygame
import cv2
import mediapipe as mp
import numpy as np
import time

class VirtualHuman:
    def __init__(self):
        # 音声エンジンの初期化
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
        # 日本語音声の設定
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'japanese' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # カメラの初期化
        self.cap = cv2.VideoCapture(0)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Pygameの初期化
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("仮想デジタルヒューマン")
        
    def speak(self, text):
        """テキストを音声に変換して再生"""
        self.engine.say(text)
        self.engine.runAndWait()
    
    def process_face(self):
        """カメラからの顔検出と処理"""
        success, image = self.cap.read()
        if not success:
            return None
        
        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]
        return None
    
    def run(self):
        """メインループ"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.speak("こんにちは、私は仮想デジタルヒューマンです。")
            
            # 画面のクリア
            self.screen.fill((255, 255, 255))
            
            # 顔の検出と処理
            face_landmarks = self.process_face()
            if face_landmarks:
                # ここで顔の動きに応じた処理を追加できます
                pass
            
            # 画面の更新
            pygame.display.flip()
            time.sleep(0.01)
        
        # クリーンアップ
        self.cap.release()
        pygame.quit()

if __name__ == "__main__":
    virtual_human = VirtualHuman()
    virtual_human.run() 