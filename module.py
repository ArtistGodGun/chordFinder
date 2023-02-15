import madmom
import pandas as pd
import subprocess
import csv
import numpy as np
import os
import noteToChord as nc

def getBeatTime(path):
    # 음원의 비트타임을 추출 후 튜플 형태로 반환합니다
    # madmom을 설치할때 madmom의 tests폴더가 필요할 수도 있습니다
    proc = madmom.features.DBNDownBeatTrackingProcessor(beats_per_bar=[3,4],fps=100)
    act = madmom.features.RNNDownBeatProcessor()(path)
    result = proc(act)
    return result

def saveBeatTimeToCSV(beat_time, save_path, pure_name):
    # 튜플 형태의 비트타임을 DataFrame형식으로 변경후 csv로 저장합니다
    # 굳이 저장을 안하고 DataFrame을 그대로 다음 프로세스 과정으로 넘겨도 됩니다
    # 다만 비트타임을 추출하는 시간이 꽤 걸리기 때문에 저장하고 사용합니다.
    csv_path = f'{save_path}/{pure_name}.csv'
    df = pd.DataFrame(beat_time, columns= ['time', 'beat'])
    df.to_csv(csv_path, index = False)
    read_csv = pd.read_csv(csv_path)
    return read_csv

def getAccomFile(input_path, output_path, audio_name):
    # spleeter 4stems으로 나눕니다.
    subprocess.run([
        'spleeter', 'separate',
        '-p', 'spleeter:4stems', 
        input_path,
        '-b','320k', '-B', 'tensorflow',
        '-o', output_path])

    spleeter_path = f'{output_path}/{audio_name}'
    # 필요없는 drums, vocals는 미리 제거 하고
    os.remove(f'{spleeter_path}/drums.wav')
    os.remove(f'{spleeter_path}/vocals.wav')
    # bass, other는 FFMPEG으로 합쳐줍니다
    bass = f'{spleeter_path}/bass.wav'
    other = f'{spleeter_path}/other.wav'
    accom_path = f'{output_path}/accom_{audio_name}.wav'

    subprocess.run([
        'ffmpeg',
        '-i', bass, '-i', other,
        '-filter_complex', 'amerge=inputs=2',
        accom_path, '-v', 'quiet' ,'-y'])
    # 합쳐준 후 bass, other을 지웁니다
    os.remove(bass)
    os.remove(other)
    return accom_path
def splitAudioBar(audio_path, info, output_path):
    # madmom으로 분해한 info로 오디오를 FFMPEG을 사용하여 나눕니다
    start_time = 0
    end_time = 0
    split_count = 0
    for i in range(0, len(info) - 1):
        start, end, beat = float(info['time'][i]), float(info['time'][i+1]), float(info['beat'][i])
        if beat == 1.0:
            start_time = start
        if beat == 4.0:
            end_time = end
            if split_count < 10:
                out_name = f'000{split_count}'
            elif split_count < 100:
                out_name = f'00{split_count}'
            elif split_count < 1000:
                out_name = f'0{split_count}'
            else:
                out_name = split_count
            if start_time == 0:
                out_name = f'{out_name}_0'

            subprocess.run(['ffmpeg', '-i', audio_path, '-ss', f"{start_time}", '-to', f'{end_time}', f'{output_path}/{out_name}.wav', '-v', 'quiet', '-y'])
            split_count +=1
    return 'success'

def exportMIDI(split_audio_path, midi_path):
    # basic-pitch로 오디오를 미디로 바꿉니다
    CMD = []
    CMD.append('basic-pitch')
    CMD.append(midi_path)
    l = sorted(os.listdir(split_audio_path))
    for audio_tmp in l:
        print(audio_tmp)
        CMD.append(f'{split_audio_path}/{audio_tmp}')

    # csv도 같이 뽑아줍니다
    CMD.append('--save-note-events')
    subprocess.run(CMD)
    return 'success'

def getChordName(midi_path):
    # 미디 파일을 읽어서 코드로 바꿔줍니다
    return_value = []
    midi_list = os.listdir(midi_path)
    midi_list.sort()
    bar = 0
    for midi_csv in midi_list:
        f_name, f_ext = os.path.splitext(midi_csv)
        if f_ext == '.csv':
            # 데이터 전처리
            df = getCSVData(f'{midi_path}/{f_name}')
            # 데이터가 없는 경우 = 분석할 음원이 없음
            if len(df) == 0:
                chord_name = f'{bar}_N'
            elif len(f_name.split('_')) != 3:
                chord_name = f'{bar}_N'
            else:                
                end_length = np.max(df['end_time_s'])

                # 근음 뽑기
                root = getRoot(df, end_length)
                # 미디 구성 노트로 코드 성격 뽑기
                symbol = getSymbol(df, root)
                # chord_name = nc.getChord(symbol)
                # print(chord_name)

                # 근음 숫자를 문자로 바꿈
                root_note = list(basic_note_number.keys())[root]
                # 루트음과 코드 tried를 합침
                chord_name = f'{bar}_{root_note}:{symbol}'
                # chord_name = f'{bar}_{root_note}'
                # print(chord_name)
            bar += 1
            return_value.append(chord_name)
    return return_value


def changeIntPandas(value):
    # csv로 불러온 pandas value를 int로 바꿈
    return int(value)
def changeFloatPandas(value):
    # csv로 불러온 pandas value를 float으로 바꿈
    return float(value)


def getCSVData(path):
    f = open(f'{path}.csv')
    f_read = csv.reader(f)
    csv_list = []
    for c in f_read:
        if len(c) != 0:
            csv_list.append(c[:3])
    f.close()
    # 사용하는 파라미터는 스타트타임, 엔드타임, 음표 입니다
    df = pd.DataFrame(csv_list[1:], columns = csv_list[0])
    df['start_time_s'] = df['start_time_s'].apply(changeFloatPandas)
    df['end_time_s'] = df['end_time_s'].apply(changeFloatPandas)
    df['pitch_midi'] = df['pitch_midi'].apply(changeIntPandas)
    return df
import time
def getRoot(df, end_length):
    # 루트음을 뽑아줌
    # 이것은 근음을 추출하는 룰이며 언제든지 바뀔수 있습니다
    check = (df['start_time_s'] < end_length / 2) & (df['end_time_s'] - df['start_time_s'] > 0.3)    
    # check = (df['start_time_s'] < end_length / 2)

    # 룰에 의해 뽑힌 음중 가장 낮은 음을 루트로 함
    root = np.min(df[check]['pitch_midi'])
    
    if str(root) == 'nan':
        root = np.min(df['pitch_midi'])

    # 루트 음을 최저로 만듬
    repeat = True
    while repeat:
        if root > 11:
            root -=12
        else:
            repeat = False
    return root
aa = 0
def getSymbol(df, root):
    note_list = [] # basic note가 저장될 곳
    len_list = [] # 각각의 노트의 길이가 저장될 곳
    # 모든 미디노트를 basic note로 만듬
    full_df = df.copy()
    half = df['end_time_s'].max() /2


    df = df[(df['start_time_s'] <= half)]
    for i in range(0, len(full_df)):
        try:
            row = df.loc[i].to_list()
            start_time = float(row[0])
            end_time = float(row[1])
            note = int(row[2])
            # print(note, start_time, end_time)
            repeat = True
            while repeat:
                if note > 11:
                    note -=12
                else:
                    if note < root:
                        note += 12
                    repeat = False
            note_list.append(note)
            len_list.append(end_time - start_time)
        except:
            pass

    df = full_df.copy()
    if len(note_list) == 0:
        for i in range(0, len(df)):
            row = df.loc[i].to_list()
            start_time = float(row[0])
            end_time = float(row[1])
            note = int(row[2])
            repeat = True
            while repeat:
                if note > 11:
                    note -=12
                else:
                    if note < root:
                        note += 12
                    repeat = False
            note_list.append(note)
            len_list.append(end_time - start_time)
    # 저장된 노트와 길이를 array로 바꿔줌
    note_list = np.array(note_list)
    len_list = np.array(len_list)
    # 중복 노트 제거
    note_arg = np.unique(note_list)
    # print(note_arg)
    # 현재 마디에 각각의 노트가 차지하는 비율을 계산
    max_note = []
    for i in note_arg:
        temp_length = 0
        for j in np.where(note_list == i)[0]:
            temp_length += len_list[j]
        max_note.append([note_list[j], temp_length])
    # 등장 빈도가 많은 노트부터 차례대로 정렬
    max_note.sort(key=lambda x:x[1], reverse = True)
    # print(max_note)
    # 등장 빈도가 많은 노트를 저장. 상위 몇개의 노트만 사용하기도 가능
    chord_note = sorted(list(np.array(max_note, dtype=int)[:, 0]))
    return chord_note


basic_chord_structure = {
    'M' : [0, 4, 7],
    'm' : [0, 3, 7],
    'aug' : [0, 4, 8],
    'dim' : [0, 3, 6],
    '7': [0, 4, 7, 10],
    'M7': [0, 4, 7, 11],
    'm7': [0, 3, 7, 10],
    'm7b5': [0, 3, 6, 10],
    'sus4': [0, 5, 7],
    '6' : [0, 4, 7, 9],
    '7b5': [0, 4, 6, 10],
    '7#5': [0, 4, 8, 10],
    '7sus4': [0, 5, 7, 10],
    'm6' : [0, 3, 7, 9],
    'dim6': [0, 3, 6, 9],
    'M7#5': [0, 4, 8, 11],
    'mM7': [0, 3, 7, 11],
    'add9': [0, 2, 4, 7],
    'madd9': [0, 2, 3, 7],
    'add11': [0, 4, 5, 7, 11],
    'm69': [0, 2, 3, 7, 9],
    '69': [0, 2, 4, 7, 9],
    '9': [0, 2, 4, 7, 10],
    'm9': [0, 2, 3, 7, 10],
    'M9': [0, 2, 4, 7, 11], 
    'sus49': [0, 2, 5, 7, 10],
    'Mb9': [0, 1, 4, 7],
    '7b9': [0, 1, 4, 7, 10],
    'M7b9': [0, 1, 4, 7, 11],
    '7#11': [0, 4, 6, 7, 10],
    'm9': [0, 2, 3, 7]
}

basic_note_number = {
    'C': 0, 'C#':1, 'D':2, 'D#':3,
    'E':4, 'F':5, 'F#':6, 'G':7,
    'G#':8, 'A':9, 'A#':10, 'B':11
}