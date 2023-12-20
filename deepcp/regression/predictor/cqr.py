import torch

from deepcp.regression.predictor.split import SplitPredictor
from deepcp.regression.utils.metrics import Metrics


class CQR(SplitPredictor):
    """_summary_

    :param model: a deep learning model that can output alpha/2 and 1-alpha/2 quantile regression.
    """
    def __init__(self, model, device):
        super().__init__(model, device)

    def calculate_threshold(self, predicts, y_truth, alpha):
        self.scores = torch.maximum(predicts[:, 0] - y_truth, y_truth - predicts[:, 1])
        self.q_hat = torch.quantile(self.scores, (1 - alpha) * (1 + 1 / self.scores.shape[0]))

    def predict(self, x_batch):
        predicts_batch = self._model(x_batch.to(self._device)).float()
        if len(x_batch.shape) == 2:
            
            lower_bound = predicts_batch[:, 0] - self.q_hat
            upper_bound = predicts_batch[:, 1] + self.q_hat
            prediction_intervals = torch.stack([lower_bound, upper_bound], dim=1)
        else:
            prediction_intervals = torch.zeros(2)
            prediction_intervals[0] = predicts_batch[0] - self.q_hat
            prediction_intervals[1] = predicts_batch[1] + self.q_hat
        return prediction_intervals
