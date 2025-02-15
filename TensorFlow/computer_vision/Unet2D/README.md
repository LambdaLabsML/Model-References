# UNet for 2D Medical Image Segmentation
This repository provides a script and recipe to train UNet Medical to achieve state of the art accuracy, and is tested and maintained by Habana Labs, Ltd. an Intel Company. Please visit [this page](https://developer.habana.ai/resources/habana-training-models/#performance) for performance information.

## Table of Contents

For more information about training deep learning models on Gaudi, visit [developer.habana.ai](https://developer.habana.ai/resources/).

* [Model-References](../../../README.md)
* [Model overview](#model-overview)
* [Setup](#setup)
* [Training](#training)
* [Advanced](#Advanced)
* [Changelog](#changelog)

## Model Overview

This repository provides script to train UNet Medical model for 2D Segmentation on Habana Gaudi (HPU). It is based on [NVIDIA UNet Medical Image Segmentation for TensorFlow 2.x](https://github.com/NVIDIA/DeepLearningExamples/tree/master/TensorFlow2/Segmentation/UNet_Medical) repository. Implementation provided in this repository covers UNet model as described in the original paper [UNet: Convolutional Networks for Biomedical Image Segmentation](https://arxiv.org/abs/1505.04597).

### Model architecture
UNet allows for seamless segmentation of 2D images, with high accuracy and performance, and can be adapted to solve many different segmentation problems.

The following figure shows the construction of the UNet model and its components. UNet is composed of a contractive and an expanding path, that aims at building a bottleneck in its centermost part through a combination of convolution and pooling operations. After this bottleneck, the image is reconstructed through a combination of convolutions and upsampling. Skip connections are added with the goal of helping the backward flow of gradients in order to improve the training.

![UNet](images/unet.png)
Figure 1. The architecture of a UNet model. Taken from the [UNet: Convolutional Networks for Biomedical Image Segmentation paper](https://arxiv.org/abs/1505.04597).

### Model changes
Major changes done to original model from [NVIDIA UNet Medical Image Segmentation for TensorFlow 2.x](https://github.com/NVIDIA/DeepLearningExamples/tree/master/TensorFlow2/Segmentation/UNet_Medical):
* GPU specific configurations have been removed;
* Some scripts were changed in order to run the model on Gaudi. It includes loading habana tensorflow modules and using multi Gaudi card helpers;
* Model is using bfloat16 precision instead of float16;
* tf.keras.activations.softmax was replaced with tf.nn.softmax due to performance issues described in https://github.com/tensorflow/tensorflow/pull/47572;
* Additional tensorboard and performance logging was added;
* GPU specific files (examples/*, Dockerfile etc.) and some unused code have been removed,
* In order to improve the performance the tf.data.experimental.prefetch_to_device has been enabled for HPU device.

### Default configuration
- Execution mode: train and evaluate;
- Batch size: 8;
- Data type: bfloat16;
- Maximum number of steps: 6400;
- Weight decay: 0.0005;
- Learning rate: 0.0001;
- Number of Horovod workers (HPUs): 1;
- Data augmentation: True;
- Cross-validation: disabled;
- Using XLA: False;
- Logging losses and performance every N steps: 100.

## Setup
Please follow the instructions given in the following link for setting up the
environment including the `$PYTHON` environment variable: [Gaudi Installation
Guide](https://docs.habana.ai/en/latest/Installation_Guide/GAUDI_Installation_Guide.html).
This guide will walk you through the process of setting up your system to run
the model on Gaudi.

### Clone Habana Model garden and go to UNet2D Medical repository:

In the docker container, clone this repository and switch to the branch that
matches your SynapseAI version. (Run the
[`hl-smi`](https://docs.habana.ai/en/latest/Management_and_Monitoring/System_Management_Tools_Guide/System_Management_Tools.html#hl-smi-utility-options)
utility to determine the SynapseAI version.)

```bash
git clone -b [SynapseAI version] https://github.com/HabanaAI/Model-References /root/Model-References
```
Go to the UNet2D directory
```bash
  cd /root/Model-References/TensorFlow/computer_vision/Unet2D
```

### Install Model Requirements

In the docker container, go to the UNet2D directory
```bash
cd /root/Model-References/TensorFlow/computer_vision/Unet2D
```
Install required packages using pip
```bash
$PYTHON -m pip install -r requirements.txt
```

### Add Tensorflow packages from model_garden to python path:
```bash
  export PYTHONPATH=$PYTHONPATH:/root/Model-References/
```

### Download the [EM segmentation challenge dataset](http://brainiac2.mit.edu/isbi_challenge/home)*:
```bash
  $PYTHON download_dataset.py
```
by default it will download the dataset to `./data` path, use `--data_dir <path>` to change

*If original location is unavailable, dataset is also mirrored on Kaggle: https://www.kaggle.com/soumikrakshit/isbi-challenge-dataset. Registration is required.
## Training
The model was tested both in single Gaudi and 8x Gaudi cards configurations.

### Run training on single Gaudi card

```bash
$PYTHON unet2d.py --data_dir <path/to/dataset> --batch_size <batch_size> \
--dtype <precision> --model_dir <path/to/model_dir> --fold <fold>
```

For example:
- single Gaudi card training with batch size 8, bfloat16 precision and fold 0:
    ```bash
    $PYTHON unet2d.py --data_dir /data/tensorflow/unet2d --batch_size 8 --dtype bf16 --model_dir /tmp/unet2d_1_hpu --fold 0 --tensorboard_logging
    ```
- single Gaudi card training with batch size 8, float32 precision and fold 0:
    ```bash
    $PYTHON unet2d.py --data_dir /data/tensorflow/unet2d --batch_size 8 --dtype fp32 --model_dir /tmp/unet2d_1_hpu --fold 0 --tensorboard_logging
    ```

### Run training on 8 Gaudi cards
Running the script via mpirun requires`--use_horovod` argument, and mpirun prefix with several parameters. 

*<br>mpirun map-by PE attribute value may vary on your setup and should be calculated as:<br>
socket:PE = floor((number of physical cores) / (number of gaudi devices per each node))*

```bash
mpirun --allow-run-as-root --bind-to core --map-by socket:PE=7 -np 8 \
 $PYTHON unet2d.py --data_dir <path/to/dataset> --batch_size <batch_size> \
 --dtype <precision> --model_dir <path/to/model_dir> --fold <fold> --use_horovod
```

For example:

*<br>mpirun map-by PE attribute value may vary on your setup and should be calculated as:<br>
socket:PE = floor((number of physical cores) / (number of gaudi devices per each node))*

- 8 Gaudi cards training with batch size 8, bfloat16 precision and fold 0:
    ```bash
    mpirun --allow-run-as-root --tag-output --merge-stderr-to-stdout --bind-to core --map-by socket:PE=7 -np 8 \
    $PYTHON unet2d.py --data_dir /data/tensorflow/unet2d/ --batch_size 8 \
    --dtype bf16 --model_dir /tmp/unet2d_8_hpus --fold 0 --tensorboard_logging --log_all_workers --use_horovod
    ```
- 8 Gaudi cards training with batch size 8, float32 precision and fold 0:
    ```bash
    mpirun --allow-run-as-root --tag-output --merge-stderr-to-stdout --bind-to core --map-by socket:PE=7 -np 8 \
    $PYTHON unet2d.py --data_dir /data/tensorflow/unet2d/ --batch_size 8 \
    --dtype fp32 --model_dir /tmp/unet2d_8_hpus --fold 0 --tensorboard_logging --log_all_workers --use_horovod
    ```

### Run 5-fold Cross-Validation and compute average dice score
All the commands described above will train and evaluate the model on the dataset with fold 0. To perform 5-fold-cross-validation on the dataset and compute average dice score across 5 folds, the user can execute training script 5 times and calculate the average dice score manually or run bash script `train_and_evaluate.sh`:
```bash
bash train_and_evaluate.sh <path/to/dataset> <path/for/results> <batch_size> <precision> <number_of_HPUs>
```
For example:
- single Gaudi card 5-fold-cross-validation with batch size 8 and bfloat16 precision
    ```bash
    bash train_and_evaluate.sh /data/tensorflow/unet2d/ /tmp/unet2d_1_hpu 8 bf16 1
    ```
- single Gaudi card 5-fold-cross-validation with batch size 8 and float32 precision
    ```bash
    bash train_and_evaluate.sh /data/tensorflow/unet2d/ /tmp/unet2d_1_hpu 8 fp32 1
    ```
- 8 Gaudi cards 5-fold-cross-validation with batch size 8 and bfloat16 precision
    ```bash
    bash train_and_evaluate.sh /data/tensorflow/unet2d/ /tmp/unet2d_8_hpus 8 bf16 8
    ```
- 8 Gaudi cards 5-fold-cross-validation with batch size 8 and float32 precision
    ```bash
    bash train_and_evaluate.sh /data/tensorflow/unet2d/ /tmp/unet2d_8_hpus 8 fp32 8
    ```

## Advanced

The following sections provide more details of scripts in the repository, available parameters, and command-line options.

### Scripts definitions

* `unet2d.py`: The training script of the UNet2D model, entry point to the application.
* `download_dataset.py` - Script for downloading dataset.
* `data_loading/data_loader.py`: Implements the data loading and augmentation.
* `model/layers.py`: Defines the different blocks that are used to assemble UNet.
* `model/unet.py`: Defines the model architecture using the blocks from the `layers.py` script.
* `runtime/arguments.py`: Implements the command-line arguments parsing.
* `runtime/losses.py`: Implements the losses used during training and evaluation.
* `runtime/run.py`: Implements the logic for training, evaluation, and inference.
* `runtime/parse_results.py`: Implements the intermediate results parsing.
* `runtime/setup.py`: Implements helper setup functions.
* `train_and_evaluate.sh`: Runs the topology training and evaluates the model for 5 cross-validation.

Other folders included in the root directory are:
* `images/`: Contains a model diagram.

### Parameters

The complete list of the available parameters for the `unet2d.py` script contains:
* `--exec_mode`: Select the execution mode to run the model (default: `train_and_evaluate`). Modes available:
  * `train` - trains model from scratch.
  * `evaluate` - loads checkpoint from `--model_dir` (if available) and performs evaluation on validation subset (requires `--fold` other than `None`).
  * `train_and_evaluate` - trains model from scratch and performs validation at the end (requires `--fold` other than `None`).
  * `predict` - loads checkpoint from `--model_dir` (if available) and runs inference on the test set. Stores the results in `--model_dir` directory.
  * `train_and_predict` - trains model from scratch and performs inference.
* `--model_dir`: Set the output directory for information related to the model (default: `/tmp/unet2d`).
* `--data_dir`: Set the input directory containing the dataset (default: `None`).
* `--log_dir`: Set the output directory for logs (default: `/tmp/unet2d`).
* `--batch_size`: Size of each minibatch per HPU (default: `8`).
* `--dtype`: Set precision to be used in model: fp32/bf16 (default: `bf16`).
* `--fold`: Selected fold for cross-validation (default: `None`).
* `--max_steps`: Maximum number of steps (batches) for training (default: `6400`).
* `--log_every`: Log data every n steps (default: `100`).
* `--evaluate_every`: Evaluate every n steps (default: `0` - evaluate once at the end).
* `--warmup_steps`: Used during benchmarking - the number of steps to skip (default: `200`). First iterations are usually much slower since the graph is being constructed. Skipping the initial iterations is required for a fair performance assessment.
* `--weight_decay`: Weight decay coefficient (default: `0.0005`).
* `--learning_rate`: Model’s learning rate (default: `0.0001`).
* `--seed`: Set random seed for reproducibility (default: `0`).
* `--dump_config`: Directory for dumping debug traces (default: `None`).
* `--augment`: Enable data augmentation (default: `True`).
* `--benchmark`: Enable performance benchmarking (default: `False`). If the flag is set, the script runs in a benchmark mode - each iteration is timed and the performance result (in images per second) is printed at the end. Works for both `train` and `predict` execution modes.
* `--xla`: Enable accelerated linear algebra optimization (default: `False`).
* `--resume_training`: Resume training from a checkpoint (default: `False`).
* `--no_hpu`: Disable execution on HPU, train on CPU  (default: `False`).
* `--synth_data`: Use deterministic and synthetic data (default: `False`).
* `--disable_ckpt_saving`: Disables saving checkpoints (default: `False`).
* `--use_horovod`: Enable horovod usage (default: `False`).
* `--tensorboard_logging`: Enable tensorboard logging (default: `False`).
* `--log_all_workers`: Enable logging data for every horovod worker in a separate directory named `worker_N` (default: False).
* `--bf16_config_path`: Path to custom mixed precision config to use given in JSON format.
* `--tf_verbosity`: If set changes logging level from Tensorflow:
    * `0` - all messages are logged (default behavior);
    * `1` - INFO messages are not printed;
    * `2` - INFO and WARNING messages are not printed;
    * `3` - INFO, WARNING, and ERROR messages are not printed.

### Command-line options

To see the full list of available options and their descriptions, use the `-h` or `--help` command-line option, for example:
```bash
$PYTHON unet2d.py --help
```
## Supported Configuration

| Device | SynapseAI Version | TensorFlow Version(s)  |
|:------:|:-----------------:|:-----:|
| Gaudi  | 1.4.0             | 2.8.0 |
| Gaudi  | 1.4.0             | 2.7.1 |

## Changelog
### 1.2.0
- removed setting number of parallel calls in dataloader mapping in order to improve performance for different TF versions
- updated requirements.txt
### 1.3.0
- moved BF16 config json file from TensorFlow/common/ to model's dir
- updated requirements.txt
### 1.4.0
- in order to improve the performance the tf.data.experimental.prefetch_to_device has been enabled for HPU device.
- Change `python` or `python3` to `$PYTHON` to execute correct version based on environment setup.
- Import horovod-fork package directly instead of using Model-References' TensorFlow.common.horovod_helpers; wrapped horovod import with a try-catch block so that the user is not required to install this library when the model is being run on a single card
- References to custom demo script were replaced by community entry points in README and train_and_evaluate.sh