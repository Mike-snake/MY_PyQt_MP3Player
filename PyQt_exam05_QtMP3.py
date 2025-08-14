import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import os

form_class = uic.loadUiType("QtMP3.ui")[0]

class ExampleApp(QWidget, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.mediaPlayer = QMediaPlayer() # QMediaPlayer 객체 생성
        self.current_media_path = None # 현재 재생 중인 미디어 파일 경로
        self.playlist = []  # 플레이리스트를 저장할 리스트
        self.current_index = -1  # 현재 재생 중인 미디어의 인덱스

        # --- UI 위젯 연결 (파이큐티의 UI와 서로 연결)
        self.fileNameLabel = self.findChild(QLabel, 'fileNameLabel')
        self.openFileButton = self.findChild(QPushButton, 'openFileButton')
        self.playMusicButton = self.findChild(QPushButton, 'playMusicButton')
        self.pauseplayButton = self.findChild(QPushButton, 'pauseplayButton')
        self.stopplayButton = self.findChild(QPushButton, 'stopplayButton')
        self.progressBar = self.findChild(QSlider, 'progressBar')
        self.currentTimeLabel = self.findChild(QLabel, 'currentTime')
        self.totalTimeLabel = self.findChild(QLabel, 'totalTime')
        self.listWidget = self.findChild(QListWidget, 'listWidget')

        # --- progressBar 관련 시그널 (읽기 전용) ---
        self.mediaPlayer.positionChanged.connect(self.position_changed)  # 재생 위치 변경 시
        self.mediaPlayer.durationChanged.connect(self.duration_changed)  # 총 재생 시간 변경 시
        self.progressBar.sliderMoved.connect(self.set_position)  # 슬라이더를 수동으로 움직였을 때

        # 실질적인 액션이 이루어 지는 코드부분
        self.openFileButton.clicked.connect(self.open_files)             # 파일오픈 버튼
        self.playMusicButton.clicked.connect(self.play_music)           # 플레이 버튼
        self.pauseplayButton.clicked.connect(self.toggle_play_pause)    # 일시정지 버튼
        self.stopplayButton.clicked.connect(self.stop_play_music)       # 스탑 버튼

        self.mediaPlayer.mediaStatusChanged.connect(self.media_status_changed)  # 미디어 상태 변화 감지
        self.mediaPlayer.stateChanged.connect(self.media_playback_state_changed)  # 재생 상태 변경 시

        # 플레이리스트 더블클릭 이벤트 연결
        self.listWidget.doubleClicked.connect(self.play_selected_from_playlist)

        # 초기 상태 설정
        self.progressBar.setDisabled(True) # 슬라이더를 비활성화하여 사용자가 조작할 수 없게 함
        self.playMusicButton.setText("▶")
        self.playMusicButton.setEnabled(False)
        self.pauseplayButton.setText("❚❚")
        self.pauseplayButton.setEnabled(False)
        self.stopplayButton.setText("■")
        self.stopplayButton.setEnabled(False)


    # --- Playlist Management ---
    def open_files(self):
        # 복수 MP3 파일 열기 다이얼로그
        file_paths, _ = QFileDialog.getOpenFileNames(self, "MP3 파일 선택", "", "MP3 Files (*.mp3);;All Files (*)")

        if file_paths:
            for file_path in file_paths:
                if file_path not in self.playlist: # 중복 추가 방지
                    self.playlist.append(file_path)
                    self.listWidget.addItem(os.path.basename(file_path))
            print(f"플레이리스트에 추가된 파일: {self.playlist}")
            self.playMusicButton.setEnabled(True) # 파일이 추가되면 재생 버튼 활성화

    def play_selected_from_playlist(self):
        selected_items = self.listWidget.selectedItems()
        print('아이템이 바뀌었습니다.')
        if selected_items:
            # Get the path of the selected item
            selected_file_name = selected_items[0].text()
            print(selected_file_name)
            # Find the full path in the playlist
            for i, file_path in enumerate(self.playlist):
                if os.path.basename(file_path) == selected_file_name:
                    self.current_index = i
                    self._play_media_at_index(self.current_index)
                    break

    def _play_media_at_index(self, index):
        if 0 <= index < len(self.playlist):
            self.current_media_path = self.playlist[index]
            self.fileNameLabel.setText(os.path.basename(self.current_media_path))
            content = QMediaContent(QUrl.fromLocalFile(self.current_media_path))
            self.mediaPlayer.setMedia(content)
            self.mediaPlayer.play()
            self.progressBar.setEnabled(True)
            self.listWidget.setCurrentRow(index) # 선택된 항목 강조

            # Reset progress bar and time labels
            self.progressBar.setValue(0)
            self.currentTimeLabel.setText("00:00")
            self.totalTimeLabel.setText("00:00") # Will be updated by duration_changed

            print(f"재생 중: {self.current_media_path}")
        else:
            print("플레이리스트 인덱스 벗어남 또는 플레이리스트 비어있음.")
            self.stop_play_music() # Reset controls if playlist is empty or index is out of bounds

    def play_next_in_playlist(self):
        if self.playlist:
            next_index = (self.current_index + 1) % len(self.playlist) # 순환 재생
            self.current_index = next_index
            self._play_media_at_index(self.current_index)
        else:
            self.stop_play_music() # No more items in playlist


    # 뮤직 플레이
    def play_music(self):
        # # 파일이 로드되어 있고, 현재 재생 중이 아니면 재생 시작
        # if self.current_media_path and self.mediaPlayer.state() != QMediaPlayer.PlayingState:
        #     self.mediaPlayer.play()
        #     self.playMusicButton.setText("재생 중...")  # 재생 시작을 알리는 텍스트
        #     print("음악 재생 시작")
        # elif self.mediaPlayer.state() == QMediaPlayer.PlayingState:
        #     print("이미 재생 중입니다.")
        # else:
        #     print("재생할 파일이 선택되지 않았습니다.")
        # if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
        #     print("이미 재생 중입니다.")
        #     return

        if self.mediaPlayer.state() == QMediaPlayer.PausedState:
            self.mediaPlayer.play()
            self.playMusicButton.setText("Playing...")  # 재생 시작을 알리는 텍스트
            return

        selected_items = self.listWidget.selectedItems()

        if selected_items:
            # 첫 번째 선택된 항목의 인덱스를 가져옵니다. (다중 선택 시 첫 번째 항목 기준)
            intended_play_index = self.listWidget.row(selected_items[0])

            # 현재 플레이어가 재생 중이고, 선택된 곡이 현재 재생 중인 곡과 같다면
            if (self.mediaPlayer.state() == QMediaPlayer.PlayingState and
                    self.current_index == intended_play_index):
                print(f"이미 '{os.path.basename(self.playlist[self.current_index])}'이(가) 재생 중입니다. 계속 재생합니다.")
                # 아무것도 하지 않고 함수를 종료합니다.
                return

            # 그렇지 않고 (플레이어가 멈췄거나 일시정지, 또는 다른 곡을 선택했다면)
            # 선택된 곡을 재생합니다.
            self.current_index = intended_play_index  # 현재 재생 인덱스 업데이트
            self._play_media_at_index(self.current_index)  # 선택된 곡 재생 함수 호출
            return  # 처리가 완료되었으므로 함수 종료


            # self.play_selected_from_playlist()
        elif self.playlist and self.current_index == -1:  # No song selected or played yet, play first in playlist
            self.current_index = 0
            self._play_media_at_index(self.current_index)
        elif self.current_media_path and self.mediaPlayer.state() == QMediaPlayer.StoppedState:  # If a file is already loaded but stopped
            self.mediaPlayer.play()

    # 일시 정지
    def toggle_play_pause(self):
        # 재생 중이면 일시정지, 일시정지 또는 정지 상태면 재생
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            print("음악 일시정지")
        else:
            self.mediaPlayer.play()
            print("음악 재생 시작 또는 재개")

    # 뮤직 종료
    def stop_play_music(self):
        self.mediaPlayer.stop()

    def position_changed(self, position):
        # 재생 위치가 변경될 때마다 progressBar와 currentTimeLabel 업데이트
        # progressBar의 maximum이 0이 아니어야 유효한 값 설정 가능
        if self.progressBar.maximum() > 0:
            self.progressBar.setValue(position)
        self.currentTimeLabel.setText(self.format_time(position))

    def duration_changed(self, duration):
        # 미디어의 총 길이가 변경될 때마다 progressBar의 최대값과 totalTimeLabel 업데이트
        self.progressBar.setRange(0, duration) # progressBar의 범위 설정
        self.totalTimeLabel.setText(self.format_time(duration))
        print(f"총 재생 시간: {self.format_time(duration)}")

    def set_position(self, position):
        # progressBar를 수동으로 움직였을 때 재생 위치 변경
        self.mediaPlayer.setPosition(position)
        print(f"재생 위치를 {self.format_time(position)}으로 변경")

    def format_time(self, milliseconds):
        # 밀리초를 "분:초" 형식으로 변환
        total_seconds = int(milliseconds / 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    # 현재 진행 상태에 따른 버튼의 변화들
    def media_status_changed(self, status):
        # 미디어 플레이어의 상태에 따라 재생 버튼의 활성화 여부와 텍스트를 제어
        if status == QMediaPlayer.MediaStatus.NoMedia:
            print('선택된 미디어가 존재하지 않습니다.')
        elif status == QMediaPlayer.MediaStatus.LoadedMedia:
            # 미디어가 로드되면 재생 버튼 활성화
            self.playMusicButton.setEnabled(True)
            self.pauseplayButton.setEnabled(False)
            self.stopplayButton.setEnabled(False)

        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            # 재생이 끝나면 버튼 텍스트를 '재생'으로 바꾸고 비활성화
            print("재생이 종료되었습니다.")
            self.play_next_in_playlist()
            self.mediaPlayer.play()

    def media_playback_state_changed(self, state):
        # 재생 상태(재생 중, 일시정지, 정지)에 따라 버튼 텍스트 변경
        if state == QMediaPlayer.PlayingState:
            self.playMusicButton.setText("Playing...")
            self.pauseplayButton.setEnabled(True)
            self.stopplayButton.setEnabled(True)
        elif state == QMediaPlayer.PausedState:
            self.playMusicButton.setText("▶❚") # 일시정지 시 버튼 텍스트 변경
            self.pauseplayButton.setEnabled(False)
        elif state == QMediaPlayer.StoppedState:
            self.playMusicButton.setText("▶") # 정지 시 버튼 텍스트 변경
            self.pauseplayButton.setEnabled(False)
            print("정지버턴이 눌렸습니다.")
            self.progressBar.setValue(0)
            self.currentTimeLabel.setText("00:00")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = ExampleApp()
    main_window.show()
    sys.exit(app.exec_())