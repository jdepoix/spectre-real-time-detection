import sys

import json

from random import shuffle

from sklearn.preprocessing import StandardScaler

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import SGD

import numpy


class SpectreDetectionNeuralNetworkTrainer():
    def __init__(self, dataset_path, save_model_path):
        self._dataset_path = dataset_path
        self._save_model_path = save_model_path

    def _load_dataset(self):
        with open(self._dataset_path) as dataset_file:
            dataset = json.loads(dataset_file.read())

        return dataset

    def _preprocess_dataset(self):
        data = []
        labels = []

        for process_data in self._load_dataset()['processes'].values():
            data += process_data['data']
            labels += [process_data['label']] * len(process_data['data'])

        data = StandardScaler().fit_transform(data)

        shuffled_data = []
        shuffled_labels = []
        indexes = list(range(len(data)))
        shuffle(indexes)

        for index in indexes:
            shuffled_data.append(data[index])
            shuffled_labels.append(labels[index])

        return shuffled_data, shuffled_labels

    def train(self):
        data, labels = self._preprocess_dataset()

        model = Sequential()
        model.add(Dense(32, activation='relu', input_dim=3))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['binary_accuracy'])
        model.fit(numpy.array(data), numpy.array(labels), validation_split=.1, epochs=1000)
        model.save(self._save_model_path)


if __name__ == '__main__':
    SpectreDetectionNeuralNetworkTrainer(sys.argv[1], sys.argv[2]).train()
