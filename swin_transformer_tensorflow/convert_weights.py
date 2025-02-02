import argparse

import torch
import tensorflow as tf

from swin_transformer_tensorflow.config import get_config
from swin_transformer_tensorflow.model.build import build_model_with_config


def parse_option():
    parser = argparse.ArgumentParser('Swin Transformer weight conversion from PyTorch to TensorFlow', add_help=False)

    parser.add_argument(
        '--cfg',
        type=str,
        required=True,
        metavar="FILE",
        help='path to config file',
    )
    parser.add_argument(
        '--weights',
        type=str,
        required=True,
        metavar="FILE",
        help='path to PyTorch pretrained weights file',
    )
    parser.add_argument(
        '--weights_type',
        type=str,
        required=True,
        help='Type of pretrained weight file to load including number of classes',
        choices={"imagenet_1k", "imagenet_22k", "imagenet_22kto1k"},
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='path to output TF weights file',
    )

    args = parser.parse_args()
    config = get_config(args)

    return args, config


def main(args, config):
    swin_transformer = build_model_with_config(config)
    swin_transformer(
        tf.zeros([
            1,
            config.MODEL.SWIN.IN_CHANS,
            config.DATA.IMG_SIZE,
            config.DATA.IMG_SIZE
        ])
    )
    print('Model created')

    load_pytorch_weights(swin_transformer, args.weights)
    print('Weights loaded')

    swin_transformer.save_weights(args.output)
    print('Weights saved')


def load_pytorch_weights(tf_model, weights_file):
    """ Loads all Swin Transformer weights from .pth file into Tensorflow Keras Model.

    Iterates through all of the trainable variables in the Tensorflow Keras Model
    and assigns it the pretrained weight from the PyTorch .pth file.

    Args:
        tf_model: Tensorflow Keras Swin Transformer model
        weights_file: Path to the .pth file containing pretrained weights
    """
    
    torch_state_dict = torch.load(weights_file, map_location=torch.device("cpu"))
    model_keys = torch_state_dict['model'].keys()
    model_keys = list(model_keys)
    model_keys = filter_keys(model_keys)

    for layer in (tf_model.layers):
        for var in (layer.trainable_variables):
            key_index = 0

            if "patch_merging" in var.name and "truncated_dense" in var.name:
                key_index = find_key_index(model_keys, "downsample.reduction")
            elif "relative_position_bias_table" in var.name:
                key_index = find_key_index(model_keys, "attn.relative_position_bias_table")

            pytorch_key = model_keys.pop(key_index)
            
            try:
                if (len(var.shape) == 4):
                    var.assign(tf.transpose(torch_state_dict['model'][pytorch_key], perm=[2,3,1,0]))
                else:
                    var.assign(tf.transpose(torch_state_dict['model'][pytorch_key]))
            except:
                var.assign(torch_state_dict['model'][pytorch_key])


def filter_keys(model_keys):
    """ Remove untrainable variables left in pytorch .pth file.

    Args:
        model_keys: List of PyTorch model's state_dict keys
    
    Returns:
        A string list containing only the trainable variables
        from the PyTorch model's state_dict keys
    """
    to_remove = []
    for key in model_keys:
        if ("attn.relative_position_index" in key) or ("attn_mask" in key):
            to_remove.append(key)

    for a in to_remove:
        model_keys.remove(a)

    return model_keys


def find_key_index(model_keys, keyword):
    """ Find index of first occurence of keyword in model_keys.

    Args:
        model_keys: List of PyTorch model's state_dict keys
        keyword: Keyword to search for in model_keys
    
    Returns:
        Index of first occurence of keyword in model_keys
    """
    key_name = ""
    for key in reversed(model_keys):
        if (keyword in key):
            key_name = key
        else:
            if key_name == "":
                continue
            else:
                index = model_keys.index(key_name)
                break
    return index
                

if __name__ == '__main__':
    tf.debugging.set_log_device_placement(False)
    gpus = tf.config.experimental.list_physical_devices("GPU")
    if gpus:
        try:
            # Currently, memory growth needs to be the same across GPUs
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices("GPU")
            print(len(gpus), "Physical GPUs,", len(
                logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            # Memory growth must be set before GPUs have been initialized
            print(e)

    args, config = parse_option()
    main(args, config)