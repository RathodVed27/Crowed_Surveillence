"""
metrics.py
-----------------------------------------
Calculates evaluation metrics for AI Model
-----------------------------------------
Author: Ved Rathod (Refactored)
"""

class Metrics:
    @staticmethod
    def calculate_accuracy(tp, fp, fn, tn):
        total = tp + fp + fn + tn
        if total == 0:
            return 0.0
        return (tp + tn) / total * 100.0
