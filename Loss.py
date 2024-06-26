import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class MixedLoss(nn.Module):
    def __init__(self, alpha=None, gamma=2., reduction='mean'):
        super(MixedLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        assert reduction in ['none', 'mean', 'sum']
        self.reduction = reduction

        self.lambda_param = nn.Parameter(torch.tensor(0.5, requires_grad=True))

    def forward(self, logits, targets):
      
        probs = torch.sigmoid(logits)

   
        ce_loss = nn.functional.binary_cross_entropy_with_logits(
            logits, targets.float(), reduction='none')

        p_t = probs * targets + (1. - probs) * (1. - targets)
        modulating_factor = torch.pow(1. - p_t, self.gamma)
        focal_loss = modulating_factor * ce_loss

       
        if self.alpha is not None:
            alpha_factor = self.alpha[targets] * (targets == 1).float() + \
                           (1. - self.alpha[targets]) * (targets == 0).float()
            focal_loss *= alpha_factor

  
        mixed_loss = self.lambda_param * focal_loss + (1. - self.lambda_param) * ce_loss

    
        if self.reduction == 'mean':
            loss = mixed_loss.mean()
        elif self.reduction == 'sum':
            loss = mixed_loss.sum()
        else:
            loss = mixed_loss

        return loss

