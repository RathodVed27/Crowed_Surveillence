"""
confusion_matrix.py
-----------------------------------------
Generates TP, FP, FN, TN for Crowd Counting
-----------------------------------------
Author: Ved Rathod (Refactored)
"""

class ConfusionMatrix:
    def __init__(self):
        self.tp = 0
        self.fp = 0
        self.fn = 0
        self.tn = 0

    def update(self, predicted, actual):
        """
        For crowd counting:
        TP = correctly predicted people (min of predicted and actual)
        FP = over predicted people (max(0, predicted - actual))
        FN = missed people (max(0, actual - predicted))
        TN = 0 (we only evaluate positive detections in counting without empty frames)
        """
        self.tp += min(predicted, actual)
        self.fp += max(0, predicted - actual)
        self.fn += max(0, actual - predicted)
        
    def get_matrix(self):
        return {
            "tp": self.tp,
            "fp": self.fp,
            "fn": self.fn,
            "tn": self.tn
        }
