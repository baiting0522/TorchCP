# Copyright (c) 2023-present, SUSTech-ML.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from abc import ABCMeta, abstractmethod
from typing import Any

class BaseScore(object):
    """
    Abstract base class for all graph score functions.
    """
    __metaclass__ = ABCMeta

    def __init__(self) -> None:
        pass

    @abstractmethod
    def __call__(self, base_scores, edge_index, edge_weights=None):
        """Virtual method to compute scores for a data pair (x,y).

        :param base_scores: the basic scores for inputs.
        :param edge_index: the edge indices or the adjacency matrix.
        :param edge_weights: the weights corresponding to the edges.
        """
        raise NotImplementedError