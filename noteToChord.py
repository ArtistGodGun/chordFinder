import numpy as np
from numpy import dot
from numpy.linalg import norm
import warnings
warnings.filterwarnings('ignore')


basic_chord_structure = {
    'M' : [0, 4, 7],
    'm' : [0, 3, 7],
    'aug' : [0, 4, 8],
    'dim' : [0, 3, 6],
    '7': [0, 4, 7, 10],
    'M7': [0, 4, 7, 11],
    'm7': [0, 3, 7, 10],
    'm7b5': [0, 3, 6, 10],
    'add2': [0, 2, 7],
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
import time
def getChord(arr, bass_root, bar_duration):
    bar_duration = bar_duration / 2
    bass_root, bass_root_length = bass_root
    ar1 = arr[:,1]
    # bass_root = getBassRoot(arr[:,0])
    note = zeroScaling(arr[:,0])
    # chord_root = arr[0][0]
    chord_root, note = getChordRoot(note, arr[:,1], bar_duration)
    # print(note)

    # print(note)
    # print(chord_root, bass_root, note)
    b = 0
    rank = []
    # print(note)
    for k, v in basic_chord_structure.items():
        for i in range(len(note)):
            # n = rolling(note, i)
            length = np.roll(ar1, 0)
            c= cos_sim(getMetrics(v, bar_duration), getMetrics(note, length))
            if b <= c:
                rank.append([v, c, k, i])
                b = c
    rank = np.array(rank, dtype=object)
    chord_quality = rankSet(rank)[2]
    chord_root = chord_root + bass_root - 12 if chord_root + bass_root > 11 else chord_root + bass_root
    bass_root_symbol = list(basic_note_number.keys())[int(bass_root)]
    chord_root_symbol = list(basic_note_number.keys())[int(chord_root)]
    if chord_root_symbol == bass_root_symbol:
        return_value = f'{chord_root_symbol}{chord_quality}'
    else:
        return_value = f'{chord_root_symbol}{chord_quality} root {bass_root_symbol}'
    return return_value
def getBassRoot(arr):
    root = arr[0]
    while True:
        if root >11 :
            root -=12
        else:
            break
    return root

def zeroScaling(arr):
    while arr[0] != 0:
        arr -= 1
    return np.where(arr <0, arr +12, arr)

def getChordRoot(arr, length, duration):
    rank = []
    for k, v in basic_chord_structure.items():

        if k == 'sus4' and 5 not in arr:
            pass
        else:
            b = 0
            for i in range(len(arr)):
                # n = rolling(arr, i)
                l = np.roll(length, 0)
                c= cos_sim(getMetrics(v, duration), getMetrics(arr, l))
                if b <= c:
                    if len(rank) != 0:
                        rank.append([arr, c, k, i])
                    else:
                        rank.append([arr, c, k, i])
                    b = c
    rank = np.array(rank,dtype=object)
    return_root = arr[rankSet(rank)[3]]
    arr = rankSet(rank)[0]
    return return_root, arr

def rolling(sample, roll):
    sample = np.roll(sample, shift=-roll)
    sample = sample - sample[0]
    sample = np.where(sample < 0, sample +12, sample)
    sample = np.where(sample > 11, sample -12, sample)
    return sample

def cos_sim(A, B):
    return dot(A, B)/(norm(A)*norm(B))

def getMetrics(target, value):
    if type(value) == np.float64:
        va = np.full(shape= (12), fill_value=value)
    else:
        va = value
    ma = np.zeros(shape = (12))
    va_idx = 0
    for idx, i in enumerate(ma):
        if idx in target:
            ma[idx] = va[va_idx]
            va_idx +=1
            # if idx == 3 or idx == 4:
            #     ma[idx] = 2
            # elif idx == 1 or idx == 2:
            #     ma[idx] = 1
            # elif idx == 5:
            #     ma[idx] = 0.5
            # else:
            #     ma[idx] = 1
        else:
            ma[idx] = 0
    # print(va)
    # time.sleep(123123)
    return ma

def rankSet(arr):
    best_value = arr[np.argmax(arr[:,1])][1]
    chord_quality = np.where(arr[:,1] == best_value)[0]
    # return arr[chord_quality][np.argmin(arr[chord_quality][:,3])]
    return arr[chord_quality][np.argmin(arr[chord_quality][:,3])]

def scaling(arr):
    while len(np.where(arr > 11)[0]) != 0:
        arr = np.where(arr > 11, arr - 12, arr)
    return np.sort(arr)

note_role = {
    0: 'root', 1: 'b9', 2: 'add2', 3: 'm', 4: 'M', 5: 'sus4', 6: '#11', 7: '5',
    8: 'b13', 9: '6', 10 : 'b7', 11:'7', 12: 'root', 13: 'b9', 14 : 'add9', 15 : 'm',
    16: 'M', 17: '11', 18: '#11', 19: '5', 20: 'b13', 21 : '13', 22: 'b7', 23 : '7'
}

def rolling2(arr:np, roll):
    sample = np.copy(arr)
    if roll != 0:
        for i in range(0,roll):
            sample[i] +=12
    sample = np.roll(sample, shift= -roll)
    if np.max(sample) > 23:
        sample -=12
    return sample
def getChordData(arr, bar, level):
    arr = arr[:,0]
    # if bar == 82:
    #     print(bar, arr)

    bass_root = arr[0]
    tried_list = []
    tension_list = []
    
    for i in range(0, len(arr)):
        note = rolling2(arr, i)
        
        temp_root = note[0]
        tried = []
        tension = []
        for i in note:
            check = i - temp_root
            if check == 0:
                if temp_root >11:
                    temp_root -=12
                tried.append(list(basic_note_number.keys())[temp_root])
            else:
                if check in [3, 4, 7, 10, 11, 12, 15, 16, 19, 22, 23]: 
                    tried.append(list(note_role.values())[check])
                else:
                    tension.append(list(note_role.values())[check])
        # print(temp_root, note, tried_list)

        quality_list = []
        if 'M' in tried:
            if '5' in tried:
                if 'b7' in tried:
                    quality_list.append('7')
                elif '7' in tried:
                    quality_list.append('M7')
                else:
                    quality_list.append('M')
            elif 'b13' in tension:
                quality_list.append('aug')
            else:
                quality_list.append('M')
        elif 'm' in tried:
            if '5' in tried:
                if 'b7' in tried:
                    quality_list.append('m7')
                elif '7' in tried:
                    quality_list.append('mM7')
                else:
                    quality_list.append('m')
            elif '#11' in tension:
                if '6' in tension:
                    quality_list.append('dim7')
                    tension.remove('#11')
                    tension.remove('6')
                elif 'b7' in tried:
                    quality_list.append('m7b5')
                    tension.remove('#11')
                    tried.remove('b7')
                else:
                    quality_list.append('dim')
                    tension.remove('#11')
            elif 'b7' in tried:
                if 'sus4' in tension:
                    tension.remove('sus4')
                quality_list.append('m7')
            elif '7' in tried:
                quality_list.append('mM7')
            else:
                quality_list.append('m')
        # elif '5' in tried and 'b7' in tried:
        #     quality_list.append('7')
        if 'sus4' in tension and '5' in tried:
            quality_list.append('sus4')
            tension.remove('sus4')
        if 'add2' in tension and '5' in tried:
            quality_list.append('add2')
            tension.remove('add2')

        if 'M7' in quality_list:
            if '11' in quality_list:
                quality_list.remove('11')
            if 'b9' in quality_list:
                quality_list.remove('b9')
        if 'm7' in quality_list:
            if '#11' in quality_list:
                quality_list.remove('#11')
        if 'sus4' in quality_list and 'add2' in quality_list:
            quality_list.remove('sus4')
        tried_list.append([tried[0], quality_list])
          
        tension_list.append(tension)

    #     print(tried, tension)
    #     print(tried[0], quality_list)
    # print('result : ', tried_list)
    # print('tension : ', tension_list)
    
    try:
        best = np.argmin(tension_list)
    except:
        best = 0

    # print(tried_list[best][0], tried_list[best][1], tension_list[best], list(basic_note_number.keys())[bass_root])
    # print(bar, tried_list[best], tension, best)

    result_chord_root = tried_list[best][0]
    if len(tried_list[best][1]) == 0:
        result_easy_quality = tried_list[best][1]
    else:
        result_easy_quality = tried_list[best][1][0]

    # result_high_quality = tried_list[best][1][1]
    # result_best_quality = tension_list[best]
    result_bass_root = list(basic_note_number.keys())[bass_root]

    if level == 1:
        if result_chord_root == result_bass_root:
            # print(f'{result_chord_root}{result_easy_quality}')
            return_value = f'{result_chord_root}{result_easy_quality}'
        else:
            # print(f'{result_chord_root}{result_easy_quality}/{result_bass_root}')
            return_value = f'{result_chord_root}{result_easy_quality}/{result_bass_root}'
    # elif level == 2:
    #     if result_chord_root == result_bass_root:
    #         print(f'{result_chord_root}{result_easy_quality}{result_high_quality}')
    #     else:
    #         print(f'{result_chord_root}{result_easy_quality}{result_high_quality}/{result_bass_root}')
    # elif level == 3:
    #     if result_chord_root == result_bass_root:
    #         print(f'{result_chord_root}{result_easy_quality}{result_high_quality}{result_best_quality}')
    #     else:
    #         print(f'{result_chord_root}{result_easy_quality}{result_high_quality}{result_best_quality}/{result_bass_root}')
    return return_value