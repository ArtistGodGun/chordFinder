import os, sys
import time
import module
import pandas as pd
import midiToNote as mn
# import noteToChord as nc

run_time = time.time()
re = int(sys.argv[1])
'''
폴더트리는 아래와 같습니다
root
- "test_audio.wav" < - 인풋 오디오 파일
- "test_audio.csv" < - 오디오에서 추출한 비트 타임 csv
- "test_audio" < - spleeter로 나뉜 음원이 저장되는 장소. bass + other + piano = accom.wav로 합친 후 전부 제거
- "accom.wav" < - bass, other, piano를 합친 음원. 이 음원에서 미디파일을 추출함
- "audio_temp" < - accom.wav를 test_audio.csv를 기준으로 잘라서 저장. 각각 한마디 길이
------0000.wav
------0001.wav
------0002.wav
------  ....
------xxxx.wav
- "midi_temp" < - audio_temp폴더 안에 있는 오디오 파일을 basic-pitch로 변경 후 저장. .mid파일과 .csv파일이 저장됨
------0000.mid, 0000.csv
------0001.mid, 0001.csv
------0002.mid, 0002.csv
------  ....
------xxxx.mid, xxxx.csv
'''

dir = 'root'
try:
    os.mkdir('root')
except:
    pass
audio_list = os.listdir('music')
song_chord = []
for music in audio_list[0:]:
    print('start!!')
    df = pd.DataFrame()
    audio_path = os.path.join('music', music)
    audio_name, audio_ext = os.path.splitext(music)

    song_chord.append(song_chord)
    '''
    madmom으로 오디오 분석 후, csv파일의 형태로 저장합니다

    RETURN : beat_time_info (DataFrame)
    - ['time', 'beat']
    - [ 0.xx ,   1.0]
    - [ 0.xx ,   2.0]
    - [ 0.xx ,   3.0]
    - [ 0.xx ,   4.0]
    -       .....
    '''
    if re == 0:
        print(audio_path)
        print('madmomStart!!')
        beat_time = module.getBeatTime(audio_path)
        beat_time_info = module.saveBeatTimeToCSV(beat_time, dir, audio_name)
        print('madmomEnd')
    '''
    spleeter 4stems으로 vocals, drums, bass, other로 추출한 다음
    vocals, drums는 지우고 bass, other를 FFMPEG으로 합칩니다.
    RETURN : accom.wav
    '''
    accom_start = time.time()
    if re == 0:
        print('spleeter Start')
        accom_path = module.getAccomFile(audio_path, dir, audio_name)

    print('spleeterEnd')
    '''
    accom.wav 파일을 FFMPEG을 사용해 beat_time_info의 정보를 기반으로 한마디씩 자릅니다
    자른 음원 파일은 Basic-Pitch를 이용해 Midi파일과 CSV파일로 각각 추출합니다
    '''

    midi_start = time.time()
    print('basic-pitch Start!')
    split_audio_path = os.path.join(dir, f'audio_{audio_name}')
    split_midi_path = os.path.join(dir, f'midi_{audio_name}')
    if re == 0:
        try:
            os.mkdir(split_audio_path)
        except:
            pass
        try:
            os.mkdir(split_midi_path)
        except:
            pass
        module.splitAudioBar(accom_path, beat_time_info, split_audio_path)
        module.exportMIDI(split_audio_path, split_midi_path)
    print('basic-pitch End!')

    '''
    자른 CSV파일의 정보를 기반으로 코드 네임을 뽑아냅니다.
    '''
    chord_list = mn.midiToNote(split_midi_path)
    print(chord_list)
    break
