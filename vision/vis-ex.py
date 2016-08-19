#!/usr/bin/env python

'''
SVM and KNearest digit recognition.

Sample loads a dataset of handwritten digits from '../data/digits.png'.
Then it trains a SVM and KNearest classifiers on it and evaluates
their accuracy.

Following preprocessing is applied to the dataset:
 - Moment-based image deskew (see deskew())
 - Digit images are split into 4 10x10 cells and 16-bin
   histogram of oriented gradients is computed for each
   cell
 - Transform histograms to space with Hellinger metric (see [1] (RootSIFT))


[1] R. Arandjelovic, A. Zisserman
    "Three things everyone should know to improve object retrieval"
    http://www.robots.ox.ac.uk/~vgg/publications/2012/Arandjelovic12/arandjelovic12.pdf

Usage:
   digits.py
'''


# Python 2/3 compatibility

# built-in modules
from multiprocessing.pool import ThreadPool
import os

import cv2

import numpy as np
from numpy.linalg import norm

CLASS_N = 10
NEG_SCALE_FACTOR = 0.2

imgs_dir = './'

svm_params = dict( kernel_type = cv2.SVM_LINEAR,
                    svm_type = cv2.SVM_C_SVC,
                    C=2.67, gamma=5.383 )

def load_imgs(path, scale_factor=1):
    samples = []
    counter = 0
    for i in os.listdir(path):
        print i
        print counter
        img = cv2.imread(path + i)
        if scale_factor != 1:
            img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
        samples.append(preprocess_hog(img))
        counter += 1
    return samples

def split2d(img, cell_size, flatten=True):
    h, w = img.shape[:2]
    sx, sy = cell_size
    cells = [np.hsplit(row, w//sx) for row in np.vsplit(img, h//sy)]
    cells = np.array(cells)
    if flatten:
        cells = cells.reshape(-1, sy, sx)
    return cells

class StatModel(object):
    def load(self, fn):
        self.model.load(fn)  # Known bug: https://github.com/opencv/opencv/issues/4969
    def save(self, fn):
        self.model.save(fn)

'''
class SVM(StatModel):
    def __init__(self, C = 1, gamma = 0.5):
        self.model = cv2.ml.SVM_create()
        self.model.setGamma(gamma)
        self.model.setC(C)
        self.model.setKernel(cv2.ml.SVM_RBF)
        self.model.setType(cv2.ml.SVM_C_SVC)

    def train(self, samples, responses):
        self.model.train(samples, cv2.ml.ROW_SAMPLE, responses)

    def predict(self, samples):
        return self.model.predict(samples)[1].ravel()
        '''

def preprocess_hog(img):
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
    mag, ang = cv2.cartToPolar(gx, gy)
    bin_n = 16
    bin = np.int32(bin_n*ang/(2*np.pi))
    bin_cells = bin[:10,:10], bin[10:,:10], bin[:10,10:], bin[10:,10:]
    mag_cells = mag[:10,:10], mag[10:,:10], mag[:10,10:], mag[10:,10:]
    hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
    hist = np.hstack(hists)

    # transform to Hellinger kernel
    eps = 1e-7
    hist /= hist.sum() + eps
    hist = np.sqrt(hist)
    hist /= norm(hist) + eps

    return hist


if __name__ == '__main__':
    print(__doc__)

    print('preprocessing...')
    pos_imgs_hog = load_imgs(imgs_dir + 'Pos/')
    neg_imgs_hog = load_imgs(imgs_dir + 'Neg/', NEG_SCALE_FACTOR)
    labels = [1] * len(pos_imgs_hog) + [-1] * len(neg_imgs_hog)
    samples = pos_imgs_hog + neg_imgs_hog
    samples = np.float32(samples)

    # Shuffle tests
    rng_state = np.random.get_state()
    np.random.shuffle(samples)
    np.random.set_state(rng_state)
    np.random.shuffle(labels)

    train_n = int(0.9*len(samples))
    samples_train, samples_test = np.split(samples, [train_n])
    labels_train, labels_test = np.split(labels, [train_n])

    print('training SVM...')
    model = cv2.SVM(samples_train, labels_train, params=svm_params)

    resp = model.predict_all(samples_test)
    print 'Response:'
    print resp
    print 'Labels:'
    print labels_test
    err = (labels_test != resp).mean()
    print('error: %.2f %%' % (err*100))
    #cv2.imshow('SVM test', vis)
    print('saving SVM as "svm.dat"...')
    model.save('svm.dat')
