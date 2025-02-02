# Swin-Transformer-Tensorflow
A direct translation of the official PyTorch implementation of ["Swin Transformer: Hierarchical Vision Transformer using Shifted Windows"](https://arxiv.org/abs/2103.14030) to TensorFlow 2.

The official Pytorch implementation can be found [here](https://github.com/microsoft/Swin-Transformer).

## Fork

This Fork is a packaged version of the original repo. 

### Usage
```bash
pip install git+https://github.com/johnypark/Swin-Transformer-Tensorflow@main

```
Still under construction.
-Update readme
-Make things work

## Introduction:
![Swin Transformer Architecture Diagram](./images/swin-transformer.png)

**Swin Transformer** (the name `Swin` stands for **S**hifted **win**dow) is initially described in [arxiv](https://arxiv.org/abs/2103.14030), which capably serves as a
general-purpose backbone for computer vision. It is basically a hierarchical Transformer whose representation is
computed with shifted windows. The shifted windowing scheme brings greater efficiency by limiting self-attention
computation to non-overlapping local windows while also allowing for cross-window connection.

Swin Transformer achieves strong performance on COCO object detection (`58.7 box AP` and `51.1 mask AP` on test-dev) and
ADE20K semantic segmentation (`53.5 mIoU` on val), surpassing previous models by a large margin.


## Usage:
### 1. To Run a Pre-trained Swin Transformer

`Swin-T`:

```bash
python main.py --cfg configs/swin_tiny_patch4_window7_224.yaml --include_top 1 --resume 1 --weights_type imagenet_1k
```

`Swin-S`:

```bash
python main.py --cfg configs/swin_small_patch4_window7_224.yaml --include_top 1 --resume 1 --weights_type imagenet_1k
```

`Swin-B`:

```bash
python main.py --cfg configs/swin_base_patch4_window7_224.yaml --include_top 1 --resume 1 --weights_type imagenet_1k
```

The possible options for `cfg` and `weights_type` are:  

| cfg | weights_type | 22K model | 1K Model |
| :---: | :---: | :---: | :---: |
| configs/swin_tiny_patch4_window7_224.yaml | imagenet_1k | - | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_tiny_patch4_window7_224_1k.tar.gz) |
| configs/swin_small_patch4_window7_224.yaml | imagenet_1k | - | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_small_patch4_window7_224_1k.tar.gz) |
| configs/swin_base_patch4_window7_224.yaml | imagenet_1k | - | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_base_patch4_window7_224_1k.tar.gz) |
| configs/swin_base_patch4_window12_384.yaml | imagenet_1k | - | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_base_patch4_window12_384_1k.tar.gz) |
| configs/swin_base_patch4_window7_224.yaml | imagenet_22kto1k | - | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_base_patch4_window7_224_22kto1k.tar.gz) |
| configs/swin_base_patch4_window12_384.yaml | imagenet_22kto1k | - | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_base_patch4_window12_384_22kto1k.tar.gz) |
| configs/swin_large_patch4_window7_224.yaml | imagenet_22kto1k | - | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_large_patch4_window7_224_22kto1k.tar.gz) |
| configs/swin_large_patch4_window12_384.yaml | imagenet_22kto1k | - | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_large_patch4_window12_384_22kto1k.tar.gz) |
| configs/swin_base_patch4_window7_224.yaml | imagenet_22k | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_base_patch4_window7_224_22k.tar.gz) | - |
| configs/swin_base_patch4_window12_384.yaml | imagenet_22k| [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_base_patch4_window12_384_22k.tar.gz) | - | 
| configs/swin_large_patch4_window7_224.yaml | imagenet_22k | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_large_patch4_window7_224_22k.tar.gz) | - | 
| configs/swin_large_patch4_window12_384.yaml | imagenet_22k | [github](https://github.com/VcampSoldiers/Swin-Transformer-Tensorflow/releases/download/v1.0/swin_large_patch4_window12_384_22k.tar.gz) | - |

### 2. Create custom models

To create a custom classification model:
```python
import argparse

import tensorflow as tf

from config import get_config
from models.build import build_model

parser = argparse.ArgumentParser('Custom Swin Transformer')

parser.add_argument(
    '--cfg',
    type=str,
    metavar="FILE",
    help='path to config file',
    default="CUSTOM_YAML_FILE_PATH"
)
parser.add_argument(
    '--resume',
    type=int,
    help='Whether or not to resume training from pretrained weights',
    choices={0, 1},
    default=1,
)
parser.add_argument(
    '--weights_type',
    type=str,
    help='Type of pretrained weight file to load including number of classes',
    choices={"imagenet_1k", "imagenet_22k", "imagenet_22kto1k"},
    default="imagenet_1k",
)

args = parser.parse_args()
custom_config = get_config(args, include_top=False)

swin_transformer = tf.keras.Sequential([
    build_model(config=custom_config, load_pretrained=args.resume, weights_type=args.weights_type),
    tf.keras.layers.Dense(CUSTOM_NUM_CLASSES)
)
```
**Model ouputs are logits, so don't forget to include softmax in training/inference!!**

You can easily customize the model configs with custom YAML files. Predefined YAML files provided by Microsoft are located in the `configs` directory.

### 3. Convert PyTorch pretrained weights into Tensorflow checkpoints
We provide a python script with which we convert official PyTorch weights into Tensorflow checkpoints.
```bash
$ python convert_weights.py --cfg config_file --weights the_path_to_pytorch_weights --weights_type type_of_pretrained_weights --output the_path_to_output_tf_weights
```
## TODO:
- [x] Translate model code over to TensorFlow
- [x] Load PyTorch pretrained weights into TensorFlow model
- [ ] Write trainer code
- [ ] Reproduce results presented in paper
    - [ ] Object Detection
- [ ] Reproduce training efficiency of official code in TensorFlow

### Citations: 
```bibtex
@misc{liu2021swin,
      title={Swin Transformer: Hierarchical Vision Transformer using Shifted Windows}, 
      author={Ze Liu and Yutong Lin and Yue Cao and Han Hu and Yixuan Wei and Zheng Zhang and Stephen Lin and Baining Guo},
      year={2021},
      eprint={2103.14030},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```
