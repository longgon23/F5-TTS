import pygame
import pygame_gui
import cv2
import mediapipe as mp
import numpy as np
import requests
import json
import time
import threading
import queue
from transformers import pipeline
import torch
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class AdvancedVirtualHuman:
    def __init__(self):
        # Pygameの初期化
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("高度な仮想デジタルヒューマン")
        
        # GUIマネージャーの初期化
        self.manager = pygame_gui.UIManager((self.width, self.height))
        
        # チャットボックスの作成
        self.chat_box = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect((50, 50), (700, 400)),
            manager=self.manager
        )
        
        # 入力フィールドの作成
        self.input_field = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((50, 470), (600, 40)),
            manager=self.manager
        )
        
        # 送信ボタンの作成
        self.send_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((660, 470), (90, 40)),
            text="送信",
            manager=self.manager
        )
        
        # カメラの初期化
        self.cap = cv2.VideoCapture(0)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 感情分析モデルの初期化（簡易版）
        self.emotion_patterns = {
            'happy': ['嬉しい', '楽しい', '幸せ', '笑顔'],
            'sad': ['悲しい', '辛い', '寂しい', '泣く'],
            'angry': ['怒る', '腹立たしい', 'イライラ', '不満'],
            'neutral': ['普通', 'まあまあ', '特に']
        }
        
        # TTSワーカースレッドの初期化
        self.tts_queue = queue.Queue()
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()
        
        # 会話履歴
        self.conversation_history = []
        
    def _tts_worker(self):
        """音声合成ワーカースレッド"""
        while True:
            if not self.tts_queue.empty():
                text = self.tts_queue.get()
                self._synthesize_speech(text)
            time.sleep(0.1)
    
    def _synthesize_speech(self, text):
        """VOICEVOXを使用した音声合成"""
        try:
            # VOICEVOX APIのエンドポイント
            url = "http://localhost:50021/audio_query"
            params = {
                "text": text,
                "speaker": 1  # デフォルトの話者ID
            }
            
            # 音声合成リクエスト
            response = requests.post(url, params=params)
            if response.status_code == 200:
                # 音声データの取得と再生
                audio_data = response.content
                # ここで音声データを再生する処理を実装
                # （例：pygame.mixerを使用）
        except Exception as e:
            print(f"音声合成エラー: {e}")
    
    def analyze_emotion(self, text):
        """簡易的な感情分析"""
        for emotion, patterns in self.emotion_patterns.items():
            if any(pattern in text for pattern in patterns):
                return emotion
        return 'neutral'
        
    def generate_response(self, user_input, emotion):
        """感情に基づいた応答生成"""
        # 基本的な応答パターン
        responses = {
            'greeting': {
                'happy': 'こんにちは！今日も元気そうですね！',
                'sad': 'こんにちは...大丈夫ですか？',
                'angry': 'こんにちは。落ち着いて話しましょう。',
                'neutral': 'こんにちは。お話しましょう。'
            },
            'farewell': {
                'happy': 'さようなら！またお話しましょう！',
                'sad': 'さようなら...またお話しましょうね。',
                'angry': 'さようなら。また落ち着いた時に。',
                'neutral': 'さようなら。またお話しましょう。'
            },
            'thanks': {
                'happy': 'どういたしまして！お役に立てて嬉しいです！',
                'sad': 'どういたしまして...また何かあったら言ってください。',
                'angry': 'どういたしまして。落ち着いてください。',
                'neutral': 'どういたしまして。'
            },
            'apology': {
                'happy': '大丈夫ですよ！気にしないでください！',
                'sad': '大丈夫です...気にしないでください。',
                'angry': '大丈夫です。落ち着いてください。',
                'neutral': '大丈夫です。'
            }
        }
        
        # 入力に基づいて応答を選択
        if 'こんにちは' in user_input or 'はじめまして' in user_input:
            return responses['greeting'][emotion]
        elif 'さようなら' in user_input or 'バイバイ' in user_input:
            return responses['farewell'][emotion]
        elif 'ありがとう' in user_input or '感謝' in user_input:
            return responses['thanks'][emotion]
        elif 'ごめん' in user_input or 'すみません' in user_input:
            return responses['apology'][emotion]
        else:
            return f"なるほど、{emotion}な気持ちなのですね。"
    
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
        clock = pygame.time.Clock()
        running = True
        
        while running:
            time_delta = clock.tick(60)/1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.send_button:
                            user_input = self.input_field.get_text()
                            if user_input:
                                # ユーザー入力をチャットボックスに追加
                                self.chat_box.append_html_text(f"<br>あなた: {user_input}")
                                
                                # 感情分析
                                emotion = self.analyze_emotion(user_input)
                                
                                # 応答生成
                                response = self.generate_response(user_input, emotion)
                                
                                # 応答をチャットボックスに追加
                                self.chat_box.append_html_text(f"<br>仮想ヒューマン: {response}")
                                
                                # 音声合成キューに追加
                                self.tts_queue.put(response)
                                
                                # 入力フィールドをクリア
                                self.input_field.set_text("")
                
                self.manager.process_events(event)
            
            # 画面のクリア
            self.screen.fill((255, 255, 255))
            
            # 顔の検出と処理
            face_landmarks = self.process_face()
            if face_landmarks:
                # ここで顔の動きに応じた処理を追加
                pass
            
            # GUIの更新
            self.manager.update(time_delta)
            self.manager.draw_ui(self.screen)
            
            # 画面の更新
            pygame.display.flip()
        
        # クリーンアップ
        self.cap.release()
        pygame.quit()

if __name__ == "__main__":
    virtual_human = AdvancedVirtualHuman()
    virtual_human.run() 