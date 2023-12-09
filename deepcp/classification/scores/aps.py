# Copyright (c) 2023-present, SUSTech-ML.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

# The reference repository is https://github.com/aangelopoulos/conformal_classification


import numpy as np
import torch

from deepcp.classification.scores.base import BaseScoreFunction


class APS(BaseScoreFunction):
    def __init__(self, randomized=True):
        super(APS, self).__init__()
        self.__randomized = randomized

    def __call__(self, probs, y):

        # sorting probabilities
        indices, ordered, cumsum = self._sort_sum(probs)
        idx = torch.where(indices == y)[0]
        if not self.__randomized:
            return cumsum[idx]
        else:
            U = torch.rand(1)[0]
            if idx == torch.tensor(0):
                return U * cumsum[idx]
            else:
                return U * ordered[idx] + cumsum[idx - 1]

    def predict(self, probs):
        I, ordered, cumsum = self._sort_sum(probs)
        U = torch.rand(probs.shape[0])
        if self.__randomized:
            ordered_scores = cumsum - ordered * U
        else:
            ordered_scores = cumsum
        return ordered_scores[torch.sort(I, descending=False)[1]]

    def _sort_sum(self, probs):

        # ordered: the ordered probabilities in descending order
        # indices: the rank of ordered probabilities in descending order
        ordered, indices = torch.sort(probs, descending=True)
        # the accumulation of sorted probabilities
        cumsum = torch.cumsum(ordered, dim=0)
        return indices, ordered, cumsum
