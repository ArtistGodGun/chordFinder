import os, sys
import module
import pandas as pd
import midiToNote as mn

def tryMakePath(path):
    try:
        os.mkdir(path)
    except:
        pass

if __name__ == '__main__':
    dir = 'root'
    audio_path = 'test.wav'
    df = pd.DataFrame()
    tryMakePath(dir)
    audio_name, audio_ext = os.path.splitext(audio_path)

    print('madmom Start')
    beat_time = module.getBeatTime(audio_path)
    beat_time_info = module.saveBeatTimeToCSV(beat_time, dir, audio_name)
    
    print('spleeter Start')
    accom_path = module.getAccomFile(audio_path, dir, audio_name)
    split_audio_path = os.path.join(dir, f'audio_{audio_name}')
    split_midi_path = os.path.join(dir, f'midi_{audio_name}')
    tryMakePath(split_audio_path)
    tryMakePath(split_midi_path)
    module.splitAudioBar(accom_path, beat_time_info, split_audio_path)
    
    print('basic-pitch Start')
    module.exportMIDI(split_audio_path, split_midi_path)
    
    print('analisis start')
    chord_list = mn.midiToNote(split_midi_path)
    print(chord_list)
    