"""
-------------------------------------------------------
ShanghaiTech Dataset Loader

Reads .mat ground truth annotations and returns
the actual people count.

Author : Ved Rathod
-------------------------------------------------------
"""

import os
from scipy.io import loadmat


class ShanghaiLoader:

    def __init__(self, dataset_root):

        self.dataset_root = dataset_root

    # ---------------------------------------------------
    # Get Actual Count
    # ---------------------------------------------------

    def get_actual_count(self, image_path):

        """
        Example

        IMG_1.jpg

        ↓

        GT_IMG_1.mat

        """

        image_name = os.path.basename(image_path)

        base_name = os.path.splitext(image_name)[0]

        mat_name = f"GT_{base_name}.mat"

        ground_truth_folder = os.path.join(
            os.path.dirname(image_path),
            "..",
            "ground-truth"
        )

        ground_truth_folder = os.path.abspath(
            ground_truth_folder
        )

        mat_path = os.path.join(
            ground_truth_folder,
            mat_name
        )

        if not os.path.exists(mat_path):

            raise FileNotFoundError(
                f"Ground Truth not found:\n{mat_path}"
            )

        mat = loadmat(mat_path)

        points = mat["image_info"][0][0][0][0][0]

        return len(points)