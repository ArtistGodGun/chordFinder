from logging import root
from tracemalloc import start
import pandas as pd
import os
import time
import csv
import numpy as np
import noteToChord as nc
basic_note_number = {
    'C': 0, 'C#':1, 'D':2, 'D#':3,
    'E':4, 'F':5, 'F#':6, 'G':7,
    'G#':8, 'A':9, 'A#':10, 'B':11
}
def midiToNote(path):
    return_value = []
    csv_list = pickCSV(path)
    bar = 0
    for i in csv_list:
        csv_path = os.path.join(path, i)
        df = getCSVData(csv_path)
        
        if len(df) ==1: # 이부분 수정해야함. 노트수가 부족할때 대비
            chord_name = f'{bar}_N'
        elif len(i.split('_')) != 3:
            chord_name = f'{bar}_N'
        else:
            bar_duration = np.max(df['end_time_s'])
            bass_root = getRoot(df, bar_duration, bar)

            
            note = getChordNote(df, bar_duration, bass_root, bar)
            
            # if bar == 82:
            #     print(bar, bass_root)
            #     print(bar, note)
            chord_name = f'{bar}_{nc.getChordData(note, bar, 1)}'
            
            # chord_name = f'{bar}_{nc.getChord(note, bass_root, bar_duration)}'
            # chord_name = f'{bar}_{list(basic_note_number.keys())[int(bass_root[0])]}'
        return_value.append(chord_name)
        bar +=1
        
    return return_value

def pickCSV(path):
    csv_list = []
    for i in os.listdir(path):
        _, ext = os.path.splitext(os.path.join(path, i))
        if ext == '.csv':
            csv_list.append(i)
    return csv_list

def getCSVData(path):
    f = open(path)
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

def changeFloatPandas(value):
    # csv로 불러온 pandas value를 float으로 바꿈
    return float(value)
def changeIntPandas(value):
    # csv로 불러온 pandas value를 int로 바꿈
    return int(value)

def getRoot(df, duration, bar):
    # 루트음을 뽑아줌
    # 이것은 근음을 추출하는 룰이며 언제든지 바뀔수 있습니다
    check = (df['start_time_s'] < duration / 2) & (df['end_time_s'] - df['start_time_s'] > 0.1)    
    # check = (df['start_time_s'] < duration / 2)

    # 룰에 의해 뽑힌 음중 가장 낮은 음을 루트로 함
    root = np.min(df[check]['pitch_midi'])

    # print(bar,root_arg)
    # print(root, root_arg, df['end_time_s'][root_arg] - df['start_time_s'][root_arg])
    if str(root) == 'nan':
        root = np.min(df['pitch_midi'])
        root_arg = np.argmin(df['pitch_midi'])
    else:
        root_arg = np.argmin(df[check]['pitch_midi'])

    # 루트 음을 최저로 만듬
    repeat = True
    while repeat:
        if root > 11:
            root -=12
        else:
            repeat = False
    return np.array([root, df['end_time_s'][root_arg] - df['start_time_s'][root_arg]])

def getChordNote(df: pd.DataFrame, duration, bass_root, bar):

    a = 2
    # df = df[df['start_time_s'] <= duration / 2]
    df = df[df['start_time_s'] <= duration / a]        
    start_time = df['start_time_s'].to_numpy()
    end_time = df['end_time_s'].to_numpy()

    pitch = df['pitch_midi'].to_numpy()
    pitch = np.unique(pitch)
    # 쓸데없는 노트 날리기
    delete_arg = 0
    for i in range(0, len(pitch)):
        if i + 1 == len(pitch):
            break
        if pitch[i + 1] - pitch[i] > 17 and i >2:
            delete_arg = i + 1
            break
    if delete_arg != 0:
        pitch = pitch[:delete_arg]
        start_time = start_time[:delete_arg]
        end_time = end_time[:delete_arg]  

    pitch_scaling = []
    for i in pitch:
        while True:
            if i > 11:
                i -=12
            else:
                if i < bass_root[0]:
                    i += 12
                break
        pitch_scaling.append(i)

    duration = end_time - start_time
    pitch_list = np.unique(pitch_scaling)
    pitch_info = []
    for i in pitch_list:
        temp_length = 0
        for j in np.where(pitch_scaling == i)[0]:
            temp_length += duration[j]
        
        pitch_info.append([int(i), temp_length])

    # note = np.sort(np.unique(df['pitch_midi'].to_numpy()))
    # delete_arg = 0
    # for i in range(0, len(note)):
    #     if i + 1 == len(note):
    #         break
    #     if note[i + 1] - note[i] >= 17 and i > 2:
    #         delete_arg = i + 1
    #         break
    # if delete_arg !=0:
    #     note = note[1:delete_arg]
    # # time.sleep(123123)
    # # print(note, 'hello')
    # # print(note, temp)
    # # target = np.median(note)
    # # print(note, target, target + 12)
    # new_note = []
    # for i in note:
    #     n = i
    #     while True:
    #         if n > 11:
    #             n -=12
    #         else:
    #             if n < bass_root:
    #                 n +=12
    #             break
    #     new_note.append([n, ])
    # # print(note, new_note)
    # # print(new_note)

    return np.array(pitch_info, dtype=object)
    # note_list = [] # basic note가 저장될 곳
    # len_list = [] # 각각의 노트의 길이가 저장될 곳
    # # 모든 미디노트를 basic note로 만듬
    # full_df = df.copy()
    # half = df['end_time_s'].max() /2


    # df = df[(df['start_time_s'] <= half)]
    # for i in range(0, len(full_df)):
    #     try:
    #         row = df.loc[i].to_list()
    #         start_time = float(row[0])
    #         end_time = float(row[1])
    #         note = int(row[2])
    #         # print(note, start_time, end_time)
    #         repeat = True
    #         while repeat:
    #             if note > 11:
    #                 note -=12
    #             else:
    #                 if note < bass_root:
    #                     note += 12
    #                 repeat = False
    #         note_list.append(note)
    #         len_list.append(end_time - start_time)
    #     except:
    #         pass

    # df = full_df.copy()
    # if len(note_list) == 0:
    #     for i in range(0, len(df)):
    #         row = df.loc[i].to_list()
    #         start_time = float(row[0])
    #         end_time = float(row[1])
    #         note = int(row[2])
    #         repeat = True
    #         while repeat:
    #             if note > 11:
    #                 note -=12
    #             else:
    #                 if note < bass_root:
    #                     note += 12
    #                 repeat = False
    #         note_list.append(note)
    #         len_list.append(end_time - start_time)
    # # 저장된 노트와 길이를 array로 바꿔줌
    # note_list = np.array(note_list)
    # len_list = np.array(len_list)
    # # 중복 노트 제거
    # note_arg = np.unique(note_list)
    # # print(note_arg)
    # # 현재 마디에 각각의 노트가 차지하는 비율을 계산
    # max_note = []
    # for i in note_arg:
    #     temp_length = 0
    #     for j in np.where(note_list == i)[0]:
    #         temp_length += len_list[j]
    #     max_note.append([note_list[j], temp_length])
    # # 등장 빈도가 많은 노트부터 차례대로 정렬
    # max_note.sort(key=lambda x:x[1], reverse = True)
    # # print(max_note)
    # # 등장 빈도가 많은 노트를 저장. 상위 몇개의 노트만 사용하기도 가능
    # chord_note = sorted(list(np.array(max_note, dtype=int)[:, 0]))
    # return np.array(chord_note)