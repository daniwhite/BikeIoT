"""SVM HOG detector, based on opencv digits.py example."""

import os
import sys
import cv2

import numpy as np
from numpy.linalg import norm

DEBUG = False

CLASS_N = 10
NEG_SCALE_FACTOR = 1

imgs_dir = './'

svm_params = dict(kernel_type=cv2.SVM_RBF,
                  svm_type=cv2.SVM_C_SVC,
                  C=1000, gamma=60)  # Previously tuned
knn_k = 3


def load_imgs(path, label):
    """Load data from file."""
    imgs = []
    samples = []
    labels = []
    counter = 0
    total = len(os.listdir(path))
    for i in os.listdir(path):
        percent = 100*(counter/float(total))
        if DEBUG:
            print '%.2f%% done with %s, currently %s\r' % (percent, path, i)
        sys.stdout.flush()
        img = cv2.imread(path + i)
        samples.append(preprocess_hog(img))
        counter += 1
        imgs.append(img)
        labels.append(label)
    if DEBUG:
        print '100%% done with %s\r' % path
    sys.stdout.flush()
    return samples, imgs, labels


def preprocess_hog(img):
    """
    Calculate HOG value.

    Almost unchanged from digits.py, except it's called on each img on its own.
    """
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
    mag, ang = cv2.cartToPolar(gx, gy)
    bin_n = 16
    bin = np.int32(bin_n*ang/(2*np.pi))
    bin_cells = bin[:10, :10], bin[10:, :10], bin[:10, 10:], bin[10:, 10:]
    mag_cells = mag[:10, :10], mag[10:, :10], mag[:10, 10:], mag[10:, 10:]
    hists = [np.bincount(
            b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
    hist = np.hstack(hists)

    # transform to Hellinger kernel
    eps = 1e-7
    hist /= hist.sum() + eps
    hist = np.sqrt(hist)
    hist /= norm(hist) + eps

    return hist


if __name__ == '__main__':
    # Preprocess
    pos_imgs_hog, pos_imgs, pos_labels = load_imgs(imgs_dir + 'Pos/', 1)
    neg_imgs_hog, neg_imgs, neg_labels = load_imgs(imgs_dir + 'Neg/', -1)

    imgs = pos_imgs + neg_imgs
    labels = pos_labels + neg_labels

    imgs, labels = np.asarray(imgs), np.asarray(labels)

    samples = pos_imgs_hog + neg_imgs_hog
    samples = np.float32(samples)

    train_n = int(0.9*len(samples))

    # Shuffle data
    rand = np.random.RandomState()
    shuffle = rand.permutation(len(imgs))
    imgs, labels, samples = imgs[shuffle], labels[shuffle], samples[shuffle]

    # Separate training data from testing data
    samples_train, samples_test = np.split(samples, [train_n])
    labels_train, labels_test = np.split(labels, [train_n])
    imgs = imgs[train_n:]



    # Initialize models
    svm_model = cv2.SVM(samples_train, labels_train, params=svm_params)
    svm_resp = svm_model.predict_all(samples_test)
    # knn_model = cv2.KNearest()
    # knnmodel()

    # Count total number of positives and negatives
    test_pos = svm_resp.flatten().tolist().count(1)
    test_neg = svm_resp.flatten().tolist().count(-1)
    labels_pos = labels_test.tolist().count(1)
    labels_neg = labels_test.flatten().tolist().count(-1)
    # Calculate false positives vs false negatives
    false_pos = 0
    false_neg = 0
    correct = 0
    for i in range(0, len(svm_resp)):
        if svm_resp.flatten()[i] > labels_test[i]:
            resp_text="!False!"
            false_pos += 1
        elif svm_resp.flatten()[i] < labels_test[i]:
            false_neg += 1
            resp_text="!False!"
        elif svm_resp.flatten()[i] == labels_test[i]:
            correct += 1
            resp_text="|Correct|"
        if labels_test[i] == -1:
            resp_text += ' --Negative--'
        else:
            resp_text += ' ++Positive++'
        if DEBUG:
            cv2.putText(imgs[i], resp_text, (0,0), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
            cv2.imshow(resp_text, imgs[i])
            cv2.waitKey(0)

    print 'Test data: pos=%s, neg=%s' % (test_pos, test_neg)
    print 'Actual data: pos=%s, neg=%s' % (labels_pos, labels_neg)
    print 'Comparison data: -pos=%s, -neg=%s, correct=%s' % (false_pos, false_neg, correct)

    # Save model
    svm_model.save('svm.dat')
