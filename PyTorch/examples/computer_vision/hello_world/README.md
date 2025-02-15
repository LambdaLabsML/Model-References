## Setup
Please follow the instructions given in the following link for setting up the
environment including the `$PYTHON` environment variable: [Gaudi Installation
Guide](https://docs.habana.ai/en/latest/Installation_Guide/GAUDI_Installation_Guide.html).
This guide will walk you through the process of setting up your system to run
the model on Gaudi.

## Simple Example for model migration

The simple example.py model shows the minimal changes needed to allow a model to run on Gaudi.  Please refer to the [PyTorch Migration Guide]( https://docs.habana.ai/en/latest/PyTorch/Migration_Guide/Porting_Simple_PyTorch_Model_to_Gaudi.html) for more details.

Single Gaudi lazy mode run command:
```bash
$PYTHON example.py
```

## Habana PyTorch Hello World Usage

For more information about training deep learning models on Gaudi, visit [developer.habana.ai](https://developer.habana.ai/resources/).
This mnist based hello world model is forked from github repo [pytorch/examples](https://github.com/pytorch/examples/tree/master/mnist).

## Hello World MNIST example

This hello world example can run on single Gaudi and 8 Gaudi in eager mode and lazy mode with FP32 data type and BF16 mixed data type.

### PYTHONPATH set up
```bash
export PYTHONPATH=/path/to/Model-References:$PYTHONPATH
```

### Single Gaudi run commands
Single Gaudi FP32 eager mode run command:
```bash
$PYTHON demo_mnist.py --hpu
```

Single Gaudi BF16 eager mode run command:
```bash
$PYTHON demo_mnist.py --hpu --hmp
```

Single Gaudi FP32 lazy mode run command:
```bash
$PYTHON demo_mnist.py --hpu --use_lazy_mode
```

Single Gaudi BF16 lazy mode run command:
```bash
$PYTHON demo_mnist.py --hpu --hmp --use_lazy_mode
```

### Multi-HPU run commands

8 Gaudi FP32 eager mode run command:
```bash
$PYTHON demo_mnist.py --hpu --data_type fp32 --world_size 8
```

8 Gaudi BF16 eager mode run command:
```bash
$PYTHON demo_mnist.py --hpu --data_type bf16 --world_size 8
```

8 Gaudi FP32 lazy mode run command:
```bash
$PYTHON demo_mnist.py --hpu --data_type fp32 --use_lazy_mode --world_size 8
```

8 Gaudi BF16 lazy mode run command:
```bash
$PYTHON demo_mnist.py --hpu --data_type bf16 --use_lazy_mode --world_size 8
```
