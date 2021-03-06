# coding=utf-8
# Copyright 2019 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""Evaluation script."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path as osp
import pdb
import sys
import traceback

from absl import flags
from absl import logging
from monty.collections import AttrDict
import sklearn.cluster
import tensorflow as tf

from stacked_capsule_autoencoders.capsules.configs import data_config
from stacked_capsule_autoencoders.capsules.configs import model_config
from stacked_capsule_autoencoders.capsules.eval import cluster_classify
from stacked_capsule_autoencoders.capsules.eval import collect_results
from stacked_capsule_autoencoders.capsules.plot import make_tsne_plot
from stacked_capsule_autoencoders.capsules.train import tools
from stacked_capsule_autoencoders.capsules import capsule as _capsule

flags.DEFINE_string('snapshot', '', 'Checkpoint file.')
flags.DEFINE_string(
    'tsne_figure_name', 'tsne.png', 'Filename for the TSNE '
    'figure. It will be saved in the checkpoint folder.')

# These two flags are necessary for model loading. Don't change them!
flags.DEFINE_string('dataset', 'mnist', 'Don\'t change!')
flags.DEFINE_string('model', 'scae', 'Don\'t change!.')


def _collect_results(sess, tensors, dataset, n_batches):
    """Collects some tensors from many batches."""

    for i in range(n_batches):
        print('\rCollecting: {}/{}'.format(i + 1, n_batches), end='')
        if i == 20:
            sess.run(tensors)


def main(_=None):
    FLAGS = flags.FLAGS  # pylint: disable=invalid-name,redefined-outer-name
    config = FLAGS
    FLAGS.__dict__['config'] = config

    # Build the graph
    with tf.Graph().as_default():

        model_dict = model_config.get(FLAGS)
        data_dict = data_config.get(FLAGS)

        model = model_dict.model
        trainset = data_dict.trainset
        validset = data_dict.validset

        # Optimisation target
        validset = tools.maybe_convert_dataset(validset)
        trainset = tools.maybe_convert_dataset(trainset)

        t1 = model(trainset)
        t2 = model(validset)

        sess = tf.Session()
        saver = tf.train.Saver()
        saver.restore(sess, FLAGS.snapshot)

    if config.dataset == 'mnist':
        _collect_results(sess, _capsule.save_op, validset,
                         10000 // FLAGS.batch_size)
        _collect_results(sess, _capsule.save_op, trainset,
                         60000 // FLAGS.batch_size)
    elif config.dataset == 'svhn':
        _collect_results(sess, _capsule.save_op, validset,
                         26032 // FLAGS.batch_size)

        _collect_results(sess, _capsule.save_op, trainset,
                         73257 // FLAGS.batch_size)
    elif config.dataset == 'cifar10':
        _collect_results(sess, _capsule.save_op, validset,
                         10000 // FLAGS.batch_size)

        _collect_results(sess, _capsule.save_op, trainset,
                         50000 // FLAGS.batch_size)


if __name__ == '__main__':
    try:
        logging.set_verbosity(logging.INFO)
        tf.app.run()
    except Exception as err:  # pylint: disable=broad-except
        FLAGS = flags.FLAGS

        last_traceback = sys.exc_info()[2]
        traceback.print_tb(last_traceback)
        print(err)
        pdb.post_mortem(last_traceback)
