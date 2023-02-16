### madmom install
'''
pip install madmom
export PATH='path/to/scripts':$PATH
git clone --recursive https://github.com/CPJKU/madmom.git
cd madmom
git submodule update --init --remote
python setup.py develop --user
cd ..
'''
### spleeter install
pip install tensorflow-macos tensorflow-metal poetry
git clone https://github.com/Deezer/spleeter && cd spleeter

poetry update # warning이 뜰수도 있으나 무시해도 됨
poetry install
poetry build
pip install ./dist/spleeter-2.3.3-py3-none-any.whl
pip install pandas librosa protobuf
pip install numpy==1.23.5 scipy==1.6.0 numba
cd ..


### basic-pitch
git clone https://github.com/spotify/basic-pitch && cd basic-pitch
pip install pretty_midi mir_eval