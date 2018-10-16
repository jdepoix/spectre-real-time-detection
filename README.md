# Detecting Spectre Attacks by identifying Cache Side-Channel Attacks using Machine Learning

This projects detects ongoing Spectre attacks, by using a neural network to analyze HPCs (Hardware Performance Counters). More indepth information can be found in the corresponding paper: https://www.cs.hs-rm.de/~kaiser/events/wamos2018/wamos18-proceedings.pdf#page=77

## Dataset

The dataset can be found in the `dataset` directory. However, when using the dataset keep in mind that it was produced in a very constrained environment, as explained in the paper. We only collected the data of a defined set of processes using only one machine. Therefore, it will most likely not be sufficient for training something which is supposed to work in a more general environment and you’ll most likely won’t get anything to work when using a different machine with a different CPU. It depends on what you want to do with the data, but you should probably consider creating your own dataset and retrain the neural network.

## Training

You can train your own model by using the code provided in the `training` directory. Install the requirements in `training/requirements.txt` and execute:

```
/path/to/venv/bin/python trainig.py /path/to/dataset.json /path/to/new_model.h5
```

## Cite

```
@article{depoix2018detecting,
  title={Detecting Spectre Attacks by identifying Cache Side-Channel Attacks using Machine Learning},
  author={Depoix, Jonas and Altmeyer, Philipp},
  journal={Advanced Microkernel Operating Systems},
  pages={75},
  year={2018}
}
```
