# Copyright (c) 2023-present, SUSTech-ML.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import torch
import torch.optim as optim

from .split import SplitPredictor
from ..loss import QuantileLoss


class CQR(SplitPredictor):
    """
    Conformalized Quantile Regression (Romano et al., 2019)
    paper: https://arxiv.org/abs/1905.03222

    :param model: a pytorch model that can output alpha/2 and 1-alpha/2 quantile regression.
    """

    def __init__(self, model):
        super().__init__(model)
        
    def fit(self, train_dataloader, **kwargs):
        criterion = kwargs.get('criterion', None)
        
        if criterion is None:
            alpha = kwargs.get('alpha', None)
            if alpha is None:
                raise ValueError("When 'criterion' is not provided, 'alpha' must be specified.")
            quantiles = [alpha / 2, 1 - alpha / 2]
            criterion = QuantileLoss(quantiles)
        
        epochs = kwargs.get('epochs', 100)
        lr = kwargs.get('lr', 0.01)
        optimizer = kwargs.get('optimizer', optim.Adam(self._model.parameters(), lr=lr))
        
        self.train(epochs, train_dataloader, criterion, optimizer)

    def calculate_score(self, predicts, y_truth):
        if len(predicts.shape) == 2:
            predicts = predicts.unsqueeze(1)
        if len(y_truth.shape) == 1:
            y_truth = y_truth.unsqueeze(1)
        return torch.maximum(predicts[..., 0] - y_truth, y_truth - predicts[..., 1])

    def predict(self, x_batch):
        self._model.eval()
        if len(x_batch.shape) == 1:
            x_batch = x_batch.unsqueeze(0)
        predicts_batch = self._model(x_batch.to(self._device)).float()
        if len(predicts_batch.shape) == 2:
            predicts_batch = predicts_batch.unsqueeze(1)
        prediction_intervals = x_batch.new_zeros((predicts_batch.shape[0], self.q_hat.shape[0], 2))
        prediction_intervals[..., 0] = predicts_batch[..., 0] - self.q_hat.view(1, self.q_hat.shape[0], 1)
        prediction_intervals[..., 1] = predicts_batch[..., 1] + self.q_hat.view(1, self.q_hat.shape[0], 1)
        return prediction_intervals