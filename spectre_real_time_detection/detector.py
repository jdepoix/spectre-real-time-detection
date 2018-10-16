from keras.models import load_model
from sklearn.preprocessing import StandardScaler
import numpy as np
from bcolors import bcolors

class Detector(object):
    def __init__(self, recv_conn, send_conn):
        self.recv_conn = recv_conn
        self.send_conn = send_conn
        self.scaler = self._create_scaler()

    def _create_scaler(self):
        scaler = StandardScaler()
        scaler.mean_ = np.array([1.22685548e+08, 6.15609944e+05, 2.55416063e+06])
        scaler.scale_ = np.array([2.94523441e+08, 1.39027033e+06, 6.15530731e+06])
        return scaler

    def start(self):
        model = load_model("model.h5")

        while True:
            data = self.recv_conn.recv()
            pids = data[0]
            readings = data[1]
            scaled_readings = self.scaler.transform(readings)
            res = model.predict(scaled_readings)

            for i in range(res.size):
                if res[i][0] > 0.5:
                    print(f'{bcolors.FAIL}{pids[i]}: {readings[i]} {res[i][0]}')

            #self.send_conn.send(res)
