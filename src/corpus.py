"""Module with code to handle the base. Extract data, rewrite and etc.
"""


import os, os.path
import shutil
import scipy.io.wavfile as wavf
import numpy as np
from common import CORPORA_DIR, FEATURES_DIR
from features import mfcc


def extract_mit_features(winlen, winstep, numcep, delta_order=0):
    """Extracts features from base MIT. The features are saved in a directory with
    name given by '../bases/features/mit_<numcep>_<delta_order>'.

    @param winlen: the length of the analysis window in seconds.
    @param winstep: the step between successive windows in seconds.
    @param numcep: the number of cepstrum to return.
    @param delta_order: number of delta calculations.
    """
    if not os.path.exists(FEATURES_DIR):
        os.mkdir(FEATURES_DIR)

    #Feature base: mit_<numcep>_<delta_order>
    PATH_FEATS = '%smit_%d_%d/' % (FEATURES_DIR, numcep, delta_order)
    print('CREATING %s' % PATH_FEATS)
    if os.path.exists(PATH_FEATS):
        shutil.rmtree(PATH_FEATS)
    os.mkdir(PATH_FEATS)

    PATH_DATASETS = '%smit/' % CORPORA_DIR
    datasets = os.listdir(PATH_DATASETS)
    datasets.sort()

    for dataset in datasets:
        print(dataset)
        os.mkdir('%s%s' % (PATH_FEATS, dataset))
        speakers = os.listdir('%s%s' % (PATH_DATASETS, dataset))
        speakers.sort()

        for speaker in speakers:
            print(speaker)
            #reading list of utterances from each speaker
            PATH_SPEAKER = '%s%s/%s' % (PATH_DATASETS, dataset, speaker)
            utterances = os.listdir(PATH_SPEAKER)
            utterances.sort()
            utterances = [utt for utt in utterances if utt.endswith('.wav')]

            #path to write in features
            PATH_SPEAKER_FEAT = '%s%s/%s' % (PATH_FEATS, dataset, speaker)
            os.mkdir('%s' % PATH_SPEAKER_FEAT)
            for utt in utterances:
                PATH_UTT = '%s/%s' % (PATH_SPEAKER, utt)
                (samplerate, signal) = wavf.read(PATH_UTT)
                feats = mfcc(signal, winlen, winstep, samplerate, numcep=numcep,
                             delta_order=delta_order)
                np.save('%s/%s' % (PATH_SPEAKER_FEAT, utt[6:8]), feats)

def read_mit_features(numcep, delta_order, dataset, speaker, uttnum):
    """Reads a feature from a speaker.

    @returns: The features from the utterance given by (dataset, speaker, uttnum).
    """
    feats = np.load('%smit_%d_%d/%s/%s/%02d.npy' % (FEATURES_DIR, numcep, delta_order,
                    dataset, speaker, uttnum))

    return feats


#TESTS
if __name__ == '__main__':
    import scipy.io.wavfile as wavf
    import os, os.path, shutil
    import pylab as pl

    from common import CORPORA_DIR


    winlen = 0.02
    winstep = 0.01
    numcep = 13
    extract_mit_features(winlen, winstep, numcep)

    # Reading speech signal
    (samplerate, signal) = wavf.read('%smit/enroll_1/f00/phrase02_16k.wav' %
                                     CORPORA_DIR)
    numsamples = len(signal)
    duration = numsamples/samplerate
    time = np.linspace(1/samplerate, duration, numsamples)

    # figure 1
    feats = mfcc(signal, winlen, winstep, samplerate)
    pl.subplot(211)
    pl.grid(True)
    pl.plot(feats)
    featsf = read_mit_features(numcep, 0, 'enroll_1', 'f00', 2)
    pl.subplot(212)
    pl.grid(True)
    pl.plot(featsf)

    equal = 'Yes' if np.array_equal(feats, featsf) else 'No'
    print('Equal? %s.' % equal)

    pl.show()