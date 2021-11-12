import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from data_utils import PROPERTY_FOCUS, SUPPORTED_PROPERTIES
import argparse
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--darkplot', action="store_true",
                        help='Use dark background for plotting results')
    parser.add_argument('--legend', action="store_true",
                        help='Add legend to plots')
    parser.add_argument('--novtitle', action="store_true",
                        help='Remove Y-axis label')
    parser.add_argument('--filter', choices=SUPPORTED_PROPERTIES,
                        required=True,
                        help='name for subfolder to save/load data from')
    args = parser.parse_args()

    first_cat = " 0.5"

    if args.darkplot:
        # Set dark background style
        plt.style.use('dark_background')

    # Set font size
    plt.rcParams.update({'font.size': 18})
    # plt.rcParams.update({'font.size': 14})
    # plt.rcParams.update({'font.size': 16})

    data = []
    columns = [
        r'%s proportion of training data ($\alpha$)' % PROPERTY_FOCUS[args.filter],
        "Accuracy (%)",
        r'$Layer #$'
    ]

    categories = ["0.0", "0.1", "0.2", "0.3",
                  "0.4", "0.6", "0.7", "0.8", "0.9", "1.0"]
    if args.filter == "sex":
        raw_data = {
            'All': {
                10: [
                        [50.63, 50.1, 47.77, 55.6, 63.733333333333334, 48.833333333333336, 61.63333333333333, 60.1, 51.166666666666664, 50.57],
                        [55.3, 46.57, 50.57, 52.36666666666667, 48.06666666666667, 60.56666666666667, 49.06666666666667, 54.56666666666667, 44.9, 53.07],
                        [53.47, 60.9, 45.97, 55.7, 42.766666666666666, 56.333333333333336, 55.43333333333333, 59.766666666666666, 55.833333333333336, 64.3],
                        [53.53, 49.8, 45.67, 38.266666666666666, 58.1, 45.0, 43.266666666666666, 55.5, 54.733333333333334, 59.7],
                        [53.13, 50.07, 43.2, 46.63333333333333, 53.733333333333334, 59.13333333333333, 48.666666666666664, 47.5, 36.333333333333336, 53.666666666666664],
                        [57.97, 52.27, 64.73333333333333, 50.96666666666667, 50.93333333333333, 48.9, 53.166666666666664, 51.46666666666667, 41.53333333333333, 51.166666666666664],
                        [49.1, 48.1, 48.933, 56.43333333333333, 49.43333333333333, 34.53333333333333, 51.43333333333333, 50.06666666666667, 46.43333333333333, 54.6],
                        [37.83, 51.4, 53.63, 48.4, 59.333333333333336, 47.46666666666667, 56.63333333333333, 39.86666666666667, 50.833333333333336, 56.8],
                        [54.27, 55.6, 41.93, 48.666666666666664, 46.733333333333334, 46.3, 54.8, 43.233333333333334, 51.233333333333334, 43.833333333333336],
                        [51.8, 54.23, 50.73, 54.96666666666667, 50.06666666666667, 53.56666666666667, 49.63333333333333, 57.0, 50.53333333333333, 51.13333333333333]
                    ],
                20: [
                        [45.06666666666667, 52.96666666666667, 63.03333333333333, 62.833333333333336, 64.16666666666667, 68.63333333333334, 74.5, 70.7, 50.8, 67.36666666666666],
                        [45.833333333333336, 45.766666666666666, 53.833333333333336, 51.13333333333333, 51.03333333333333, 58.9, 48.93333333333333, 46.43333333333333, 43.266666666666666, 63.166666666666664],
                        [45.833333333333336, 45.766666666666666, 53.833333333333336, 51.13333333333333, 51.03333333333333, 58.9, 48.93333333333333, 46.43333333333333, 43.266666666666666, 63.166666666666664],
                        [50.0, 46.733333333333334, 43.56666666666667, 56.86666666666667, 36.96666666666667, 45.333333333333336, 49.03333333333333, 57.766666666666666, 51.166666666666664, 52.766666666666666],
                        [45.2, 54.333333333333336, 53.86666666666667, 51.4, 61.8, 50.7, 47.46666666666667, 51.3, 48.06666666666667, 51.46666666666667],
                        [56.2, 48.833333333333336, 48.63333333333333, 45.766666666666666, 55.6, 44.13333333333333, 49.46666666666667, 45.8, 47.333333333333336, 55.13333333333333],
                        [47.833333333333336, 45.86666666666667, 57.43333333333333, 39.93333333333333, 53.06666666666667, 60.93333333333333, 48.5, 51.833333333333336, 45.6, 56.2],
                        [49.13333333333333, 57.9, 58.8, 55.5, 44.766666666666666, 56.6, 57.7, 50.1, 47.733333333333334, 52.4],
                        [51.63333333333333, 61.166666666666664, 51.166666666666664, 42.53333333333333, 55.96666666666667, 53.8, 55.46666666666667, 57.63333333333333, 44.56666666666667, 44.3],
                        [51.43333333333333, 56.833333333333336, 49.43333333333333, 56.733333333333334, 53.1, 60.96666666666667, 53.233333333333334, 50.833333333333336, 62.7, 48.233333333333334]
                    ],
                40: [
                        [100.0, 100.0, 99.86666666666666, 100.0, 99.93333333333334, 99.96666666666667, 99.73333333333333, 99.96666666666667, 100.0, 100.0],
                        [66.8, 59.56666666666667, 56.36666666666667, 55.03333333333333, 59.03333333333333, 58.9, 61.333333333333336, 51.53333333333333, 59.166666666666664, 56.8],
                        [53.233333333333334, 52.7, 55.766666666666666, 53.3, 59.233333333333334, 59.333333333333336, 62.233333333333334, 50.5, 50.13333333333333, 54.13333333333333],
                        [45.9, 51.5, 44.266666666666666, 53.96666666666667, 44.5, 50.7, 53.6, 56.8, 52.86666666666667, 48.166666666666664],
                        [54.7, 53.03333333333333, 41.56666666666667, 48.9, 50.63333333333333, 52.96666666666667, 59.53333333333333, 54.53333333333333, 53.56666666666667, 47.766666666666666],
                        [49.96666666666667, 49.03333333333333, 42.166666666666664, 53.63333333333333, 59.166666666666664, 55.4, 44.7, 51.0, 55.56666666666667, 47.1],
                        [50.46666666666667, 53.233333333333334, 48.266666666666666, 55.13333333333333, 51.9, 47.86666666666667, 59.13333333333333, 55.06666666666667, 47.0, 51.333333333333336],
                        [43.86666666666667, 57.8, 48.333333333333336, 48.6, 56.8, 49.5, 48.3, 55.56666666666667, 48.63333333333333, 52.0],
                        [59.333333333333336, 57.03333333333333, 56.233333333333334, 55.766666666666666, 58.166666666666664, 55.766666666666666, 50.833333333333336, 50.6, 55.666666666666664, 48.43333333333333],
                        [99.93333333333334, 83.5, 85.36666666666666, 99.26666666666667, 99.73333333333333, 99.96666666666667, 83.7, 87.53333333333333, 98.96666666666667, 90.26666666666667]
                    ],
                80: [
                        [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                        [55.3, 61.5, 66.7, 61.7, 63.4, 48.06666666666667, 59.2, 58.6, 58.666666666666664, 60.7],
                        [53.0, 50.63333333333333, 61.233333333333334, 58.13333333333333, 60.93333333333333, 47.1, 55.06666666666667, 61.0, 54.36666666666667, 54.13333333333333],
                        [47.266666666666666, 47.7, 54.6, 47.8, 45.166666666666664, 53.46666666666667, 51.63333333333333, 52.766666666666666, 59.7, 45.96666666666667],
                        [49.13333333333333, 48.3, 48.266666666666666, 54.733333333333334, 58.266666666666666, 49.9, 47.13333333333333, 47.833333333333336, 43.7, 50.9],
                        [52.233333333333334, 46.46666666666667, 57.766666666666666, 45.1, 51.7, 42.333333333333336, 48.233333333333334, 48.06666666666667, 44.46666666666667, 47.03333333333333],
                        [51.6, 49.266666666666666, 51.96666666666667, 51.333333333333336, 49.7, 55.233333333333334, 50.733333333333334, 55.53333333333333, 55.666666666666664, 52.53333333333333],
                        [58.9, 60.8, 55.4, 59.333333333333336, 59.766666666666666, 51.36666666666667, 57.166666666666664, 54.06666666666667, 57.43333333333333, 51.3],
                        [62.93333333333333, 67.83333333333333, 61.666666666666664, 55.0, 68.4, 67.76666666666667, 61.7, 65.03333333333333, 61.93333333333333, 58.4],
                        [83.03333333333333, 93.06666666666666, 83.76666666666667, 82.03333333333333, 83.43333333333334, 87.46666666666667, 99.86666666666666, 79.66666666666667, 78.03333333333333, 80.5]
                ],
                1600: [
                        [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                        [75.1, 78.23, 71.83, 68.567, 75.73, 75.2, 74.767, 74.467, 67.3, 71.03],
                        [63.836, 56.7676, 63.2676, 57.567, 50.6764, 59.234, 60.367, 57.13, 56.53, 54.367],
                        [55.067, 52.734, 56.13, 52.5, 50.2, 55.734, 52.7676, 51.03, 52.867, 50.367],
                        [47.3, 50.867, 46.1674, 51.2676, 47.13, 49.6, 49.336, 51.467, 47.1, 53.367],
                        [52.734, 55.234, 53.53, 52.1, 59.336, 55.2676, 58.0, 57.7, 61.93, 51.43],
                        [64.667, 62.567, 61.63, 62.6, 63.7676, 63.93, 64.267, 58.43, 63.7, 63.067],
                        [67.73, 68.067, 67.3, 66.9, 66.83, 67.067, 67.367, 67.8, 67.7, 68.2],
                        [71.467, 72.1, 70.53, 70.23, 71.0, 70.867, 70.367, 70.934, 70.3, 70.8],
                        [82.067, 99.73, 99.0, 81.267, 80.1, 77.867, 78.634, 77.73, 78.8, 82.367]
                    ]
            },
            "1": {
                10: [
                        [69.43333333333334, 63.53333333333333, 69.26666666666667, 90.9, 71.1, 89.43333333333334, 70.86666666666666, 84.9, 71.63333333333334, 90.2],
                        [63.2, 54.2, 52.93333333333333, 56.8, 52.03333333333333, 57.766666666666666, 46.266666666666666, 49.666666666666664, 61.733333333333334, 52.833333333333336],
                        [53.03333333333333, 44.8, 41.06666666666667, 48.166666666666664, 45.06666666666667, 46.8, 54.333333333333336, 59.06666666666667, 47.333333333333336, 49.4],
                        [45.6, 50.666666666666664, 59.333333333333336, 43.266666666666666, 58.266666666666666, 57.766666666666666, 42.56666666666667, 52.36666666666667, 50.6, 52.5],
                        [57.56666666666667, 56.46666666666667, 47.86666666666667, 38.4, 47.266666666666666, 40.43333333333333, 43.166666666666664, 52.233333333333334, 63.8, 47.13333333333333],
                        [46.5, 55.53333333333333, 42.233333333333334, 48.13333333333333, 54.1, 44.96666666666667, 56.766666666666666, 43.666666666666664, 39.9, 45.03333333333333],
                        [48.53333333333333, 49.93333333333333, 43.9, 61.4, 53.5, 49.666666666666664, 44.7, 48.9, 54.3, 51.766666666666666],
                        [55.6, 54.333333333333336, 40.43333333333333, 47.8, 65.26666666666667, 49.36666666666667, 57.3, 55.93333333333333, 59.0, 52.43333333333333],
                        [63.56666666666667, 52.56666666666667, 53.03333333333333, 48.2, 54.53333333333333, 59.53333333333333, 51.53333333333333, 50.5, 53.333333333333336, 51.96666666666667],
                        [73.46666666666667, 64.3, 68.1, 68.43333333333334, 68.23333333333333, 68.9, 72.2, 62.8, 97.03333333333333, 58.1]
                    ],
                20: [
                        [90.96666666666667, 98.83333333333333, 96.3, 96.96666666666667, 97.63333333333334, 99.06666666666666, 94.63333333333334, 95.16666666666667, 97.7, 93.9],
                        [51.766666666666666, 57.36666666666667, 49.266666666666666, 53.9, 60.233333333333334, 55.56666666666667, 64.83333333333333, 52.53333333333333, 67.7, 50.06666666666667],
                        [53.6, 44.666666666666664, 59.766666666666666, 50.86666666666667, 63.4, 65.76666666666667, 58.733333333333334, 58.96666666666667, 63.86666666666667, 57.03333333333333],
                        [58.93333333333333, 51.7, 55.13333333333333, 53.333333333333336, 51.233333333333334, 43.666666666666664, 56.43333333333333, 49.53333333333333, 58.4, 49.7],
                        [40.6, 49.6, 49.43333333333333, 48.3, 47.53333333333333, 51.333333333333336, 43.666666666666664, 49.5, 41.56666666666667, 45.8],
                        [59.5, 45.833333333333336, 46.93333333333333, 56.1, 59.53333333333333, 46.733333333333334, 46.06666666666667, 58.1, 50.5, 52.166666666666664],
                        [57.4, 50.56666666666667, 49.666666666666664, 52.166666666666664, 52.63333333333333, 58.233333333333334, 58.93333333333333, 47.5, 49.13333333333333, 60.03333333333333],
                        [55.2, 55.833333333333336, 55.36666666666667, 57.6, 53.46666666666667, 56.6, 52.2, 52.0, 54.166666666666664, 49.733333333333334],
                        [52.03333333333333, 44.7, 47.6, 58.06666666666667, 54.5, 60.166666666666664, 64.86666666666666, 59.86666666666667, 49.06666666666667, 51.86666666666667],
                        [99.36666666666666, 88.46666666666667, 85.5, 76.7, 85.13333333333334, 81.23333333333333, 91.63333333333334, 92.13333333333334, 96.7, 79.66666666666667]
                    ],
                40: [
                        [99.93333333333334, 98.53333333333333, 98.9, 100.0, 99.86666666666666, 98.9, 100.0, 100.0, 99.7, 99.86666666666666],
                        [62.6, 66.96666666666667, 62.733333333333334, 58.03333333333333, 65.4, 57.96666666666667, 64.86666666666666, 64.03333333333333, 60.1, 64.7],
                        [50.0, 58.56666666666667, 59.7, 63.6, 57.93333333333333, 64.36666666666666, 51.3, 56.53333333333333, 58.53333333333333, 54.6],
                        [50.1, 52.0, 55.733333333333334, 63.13333333333333, 50.63333333333333, 45.333333333333336, 43.266666666666666, 52.233333333333334, 45.733333333333334, 45.96666666666667],
                        [57.56666666666667, 54.7, 47.3, 45.53333333333333, 48.6, 57.266666666666666, 50.166666666666664, 54.666666666666664, 47.56666666666667, 47.733333333333334],
                        [55.7, 50.46666666666667, 58.7, 52.03333333333333, 53.96666666666667, 55.3, 43.3, 44.833333333333336, 50.06666666666667, 51.63333333333333],
                        [52.2, 61.7, 46.8, 49.0, 47.266666666666666, 63.333333333333336, 52.53333333333333, 45.96666666666667, 48.266666666666666, 51.46666666666667],
                        [49.96666666666667, 57.166666666666664, 59.1, 55.46666666666667, 47.8, 54.46666666666667, 64.5, 61.4, 58.96666666666667, 54.666666666666664],
                        [62.6, 61.3, 59.233333333333334, 56.666666666666664, 59.266666666666666, 51.6, 58.9, 62.6, 60.93333333333333, 64.3],
                        [88.93333333333334, 81.43333333333334, 86.6, 90.66666666666667, 82.6, 81.53333333333333, 84.26666666666667, 77.36666666666666, 94.43333333333334, 78.5]
                    ],
                80: [
                        [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 99.96666666666667, 100.0, 100.0],
                        [60.266666666666666, 61.5, 68.03333333333333, 65.06666666666666, 70.73333333333333, 70.5, 65.03333333333333, 63.93333333333333, 69.16666666666667, 65.73333333333333],
                        [55.9, 51.2, 56.96666666666667, 59.166666666666664, 58.666666666666664, 59.7, 59.666666666666664, 63.833333333333336, 57.46666666666667, 59.36666666666667],
                        [58.06666666666667, 59.766666666666666, 51.03333333333333, 55.93333333333333, 60.766666666666666, 50.8, 61.1, 56.93333333333333, 49.96666666666667, 55.766666666666666],
                        [50.833333333333336, 51.06666666666667, 45.6, 50.46666666666667, 50.166666666666664, 46.1, 52.7, 52.13333333333333, 49.0, 57.5],
                        [54.8, 53.8, 51.43333333333333, 50.666666666666664, 46.666666666666664, 54.0, 54.93333333333333, 51.96666666666667, 55.233333333333334, 53.6],
                        [54.03333333333333, 49.766666666666666, 60.666666666666664, 50.233333333333334, 59.06666666666667, 56.833333333333336, 61.266666666666666, 59.86666666666667, 34.6, 57.833333333333336],
                        [58.13333333333333, 54.96666666666667, 55.766666666666666, 53.63333333333333, 58.333333333333336, 63.0, 63.63333333333333, 60.3, 61.1, 58.53333333333333],
                        [69.03333333333333, 68.86666666666666, 67.8, 66.2, 64.16666666666667, 66.9, 66.46666666666667, 63.96666666666667, 68.9, 67.13333333333334],
                        [85.4, 83.13333333333334, 82.43333333333334, 82.7, 79.33333333333333,82.26666666666667, 77.86666666666666, 80.5, 89.56666666666666, 79.63333333333334]
                ],
                160: [
                        [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                        [69.33333333333333, 70.83333333333333, 71.33333333333333, 68.6, 70.03333333333333, 61.06666666666667, 67.23333333333333, 66.06666666666666, 65.33333333333333, 75.23333333333333],
                        [59.6, 63.43333333333333, 61.666666666666664, 61.666666666666664, 68.0, 65.43333333333334, 51.96666666666667, 54.96666666666667, 67.9, 51.8],
                        [54.166666666666664, 51.1, 53.833333333333336, 55.96666666666667, 57.4, 53.5, 53.233333333333334, 51.333333333333336, 51.733333333333334, 56.5],
                        [51.733333333333334, 48.766666666666666, 60.733333333333334, 53.733333333333334, 56.46666666666667, 45.36666666666667, 51.4, 47.2, 51.36666666666667, 53.833333333333336],
                        [55.333333333333336, 49.4, 51.43333333333333, 49.53333333333333, 53.06666666666667, 60.9, 54.333333333333336, 52.3, 59.833333333333336, 54.333333333333336],
                        [56.4, 58.2, 56.96666666666667, 54.96666666666667, 57.1, 60.6, 57.13333333333333, 53.46666666666667, 58.63333333333333, 56.93333333333333],
                        [59.93333333333333, 64.6, 64.2, 67.63333333333334, 60.7, 62.3, 64.4, 61.53333333333333, 65.63333333333334, 63.96666666666667],
                        [67.83333333333333, 68.43333333333334, 67.86666666666666, 67.33333333333333, 70.06666666666666, 67.2, 67.76666666666667, 71.03333333333333, 70.43333333333334, 72.43333333333334],
                        [79.3, 78.36666666666666, 77.83333333333333, 81.73333333333333, 79.83333333333333, 79.93333333333334, 79.83333333333333, 82.13333333333334, 93.83333333333333, 81.33333333333333]
                ],
                1600: [
                        [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                        [75.13333333333334, 74.76666666666667, 72.9, 76.1, 74.53333333333333, 72.8, 75.03333333333333, 73.66666666666667, 74.56666666666666, 76.0],
                        [60.36666666666667, 60.86666666666667, 58.43333333333333, 59.766666666666666, 53.06666666666667, 59.733333333333334, 61.86666666666667, 63.833333333333336, 63.56666666666667, 63.9],
                        [50.56666666666667, 54.63333333333333, 55.666666666666664, 56.766666666666666, 52.766666666666666, 51.93333333333333, 56.53333333333333, 50.53333333333333, 58.333333333333336, 54.266666666666666],
                        [41.36666666666667, 51.766666666666666, 49.733333333333334, 51.166666666666664, 52.7, 49.166666666666664, 52.3, 46.233333333333334, 54.266666666666666, 48.0],
                        [59.2, 58.8, 60.833333333333336, 59.96666666666667, 57.4, 59.43333333333333, 60.13333333333333, 60.13333333333333, 60.5, 60.1],
                        [64.83333333333333, 64.96666666666667, 63.666666666666664, 65.73333333333333, 63.93333333333333, 60.833333333333336, 63.46666666666667, 65.66666666666667, 64.96666666666667, 65.66666666666667],
                        [68.7, 68.4, 68.26666666666667, 68.6, 68.2, 68.13333333333334, 68.7, 68.03333333333333, 67.56666666666666, 67.56666666666666],
                        [70.3, 70.33333333333333, 72.1, 72.26666666666667, 72.93333333333334, 72.2, 72.03333333333333, 73.8, 72.5, 70.73333333333333],
                        [84.06666666666666, 85.56666666666666, 77.66666666666667, 81.36666666666666, 83.86666666666666, 84.5, 83.33333333333333, 79.83333333333333, 80.56666666666666, 82.53333333333333]
                    ]
            },
            # "1,2": {
            #     10: [
            #             [49.5, 64.83333333333333, 64.23333333333333, 50.233333333333334, 57.666666666666664, 48.2, 56.333333333333336, 46.1, 56.733333333333334, 59.266666666666666],
            #             [56.56666666666667, 58.03333333333333, 50.666666666666664, 48.03333333333333, 49.1, 57.56666666666667, 50.6, 49.233333333333334, 47.233333333333334, 42.1],
            #             [54.63333333333333, 53.833333333333336, 58.43333333333333, 55.03333333333333, 51.6, 47.53333333333333, 56.36666666666667, 41.93333333333333, 57.46666666666667, 51.9],
            #             [47.8, 42.6, 58.5, 53.666666666666664, 60.86666666666667, 53.166666666666664, 47.63333333333333, 62.56666666666667, 56.766666666666666, 57.233333333333334],
            #             [45.86666666666667, 54.166666666666664, 53.0, 57.5, 48.9, 52.333333333333336, 50.13333333333333, 59.63333333333333, 49.46666666666667, 42.166666666666664],
            #             [56.56666666666667, 47.13333333333333, 47.46666666666667, 40.2, 48.0, 45.43333333333333, 39.7, 50.13333333333333, 48.1, 56.4],
            #             [44.93333333333333, 40.2, 54.5, 38.0, 54.833333333333336, 52.13333333333333, 53.53333333333333, 50.266666666666666, 49.56666666666667, 44.3],
            #             [54.13333333333333, 58.96666666666667, 42.6, 52.1, 56.333333333333336, 51.13333333333333, 40.93333333333333, 45.266666666666666, 53.766666666666666, 50.3],
            #             [58.233333333333334, 41.4, 43.1, 46.666666666666664, 47.53333333333333, 58.3, 50.1, 59.666666666666664, 56.36666666666667, 55.4],
            #             [56.5, 53.666666666666664, 49.733333333333334, 45.13333333333333, 34.7, 57.63333333333333, 45.53333333333333, 49.86666666666667, 52.63333333333333, 59.266666666666666]
            #     ],
            #     20: [
            #             [64.06666666666666, 80.9, 90.9, 49.4, 58.2, 70.76666666666667, 58.06666666666667, 62.8, 76.63333333333334, 56.3],
            #             [48.1, 59.7, 63.2, 48.03333333333333, 51.03333333333333, 48.86666666666667, 53.43333333333333, 51.333333333333336, 52.6, 47.56666666666667],
            #             [48.63333333333333, 49.9, 56.6, 54.6, 55.93333333333333, 57.8, 48.06666666666667, 54.2, 45.56666666666667, 49.6],
            #             [44.36666666666667, 44.3, 56.36666666666667, 46.7, 55.733333333333334, 40.43333333333333, 51.63333333333333, 56.766666666666666, 58.333333333333336, 52.2],
            #             [56.03333333333333, 42.833333333333336, 42.53333333333333, 60.833333333333336, 52.5, 44.36666666666667, 51.56666666666667, 51.43333333333333, 47.3, 54.46666666666667],
            #             [48.333333333333336, 44.833333333333336, 48.7, 54.333333333333336, 60.266666666666666, 45.9, 46.3, 53.233333333333334, 56.63333333333333, 59.266666666666666],
            #             [44.93333333333333, 55.06666666666667, 40.666666666666664, 53.9, 45.63333333333333, 47.3, 54.06666666666667, 52.6, 49.96666666666667, 49.56666666666667],
            #             [53.666666666666664, 45.733333333333334, 53.9, 45.266666666666666, 47.06666666666667, 50.666666666666664, 40.266666666666666, 49.93333333333333, 52.93333333333333, 48.8],
            #             [53.53333333333333, 47.43333333333333, 51.833333333333336, 60.9, 48.8, 52.13333333333333, 56.13333333333333, 41.9, 50.8, 55.06666666666667],
            #             [60.3, 50.3, 51.56666666666667, 49.93333333333333, 61.766666666666666, 53.666666666666664, 61.03333333333333, 62.43333333333333, 51.733333333333334, 57.333333333333336]
            #         ],
            #     40: [
            #             [87.73333333333333, 95.96666666666667, 95.66666666666667, 97.33333333333333, 99.53333333333333, 98.43333333333334, 97.0, 99.56666666666666, 82.23333333333333, 89.93333333333334],
            #             [50.0, 50.96666666666667, 53.03333333333333, 63.13333333333333, 51.766666666666666, 45.9, 57.53333333333333, 49.2, 50.166666666666664, 45.53333333333333],
            #             [51.43333333333333, 52.1, 48.43333333333333, 42.9, 51.63333333333333, 53.0, 57.03333333333333, 52.03333333333333, 50.43333333333333, 50.2],
            #             [47.8, 55.833333333333336, 53.8, 47.06666666666667, 46.6, 51.86666666666667, 59.2, 58.233333333333334, 53.0, 45.8],
            #             [50.8, 54.833333333333336, 42.43333333333333, 52.63333333333333, 52.1, 46.7, 52.7, 54.06666666666667, 51.766666666666666, 48.233333333333334],
            #             [49.43333333333333, 43.233333333333334, 54.166666666666664, 46.93333333333333, 48.36666666666667, 53.36666666666667, 45.03333333333333, 47.733333333333334, 52.3, 58.1],
            #             [51.0, 51.2, 53.03333333333333, 54.36666666666667, 50.3, 54.53333333333333, 51.766666666666666, 48.86666666666667, 54.9, 56.93333333333333],
            #             [53.666666666666664, 54.46666666666667, 48.36666666666667, 52.63333333333333, 50.766666666666666, 50.86666666666667, 52.7, 56.333333333333336, 45.4, 63.53333333333333],
            #             [49.93333333333333, 48.3, 52.666666666666664, 48.93333333333333, 52.46666666666667, 53.36666666666667, 52.56666666666667, 49.63333333333333, 49.56666666666667, 55.8],
            #             [82.13333333333334, 84.8, 72.26666666666667, 89.3, 61.96666666666667, 78.2, 44.46666666666667, 86.46666666666667, 96.56666666666666, 98.73333333333333]
            #         ],
            #     1600: [
            #             [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
            #             [75.36666666666666, 76.03333333333333, 71.13333333333334, 69.66666666666667, 73.5, 68.23333333333333, 66.93333333333334, 73.86666666666666, 75.6, 69.36666666666666],
            #             [56.9, 52.9, 59.03333333333333, 59.333333333333336, 56.1, 58.333333333333336, 60.2, 62.6, 62.53333333333333, 58.0],
            #             [57.56666666666667, 56.03333333333333, 50.93333333333333, 50.833333333333336, 53.53333333333333, 54.666666666666664, 46.333333333333336, 50.233333333333334, 56.833333333333336, 50.733333333333334],
            #             [48.03333333333333, 50.3, 50.86666666666667, 55.3, 52.0, 52.93333333333333, 52.266666666666666, 45.1, 48.833333333333336, 47.9],
            #             [50.266666666666666, 53.06666666666667, 54.233333333333334, 56.0, 55.96666666666667, 57.46666666666667, 57.733333333333334, 54.833333333333336, 55.86666666666667, 56.166666666666664],
            #             [64.4, 66.96666666666667, 64.36666666666666, 65.46666666666667, 64.7, 62.166666666666664, 61.2, 64.43333333333334, 63.3, 61.0],
            #             [66.76666666666667, 66.9, 67.33333333333333, 66.2, 67.96666666666667, 67.13333333333334, 67.1, 67.86666666666666, 67.76666666666667, 65.63333333333334],
            #             [70.23333333333333, 71.86666666666666, 72.76666666666667, 71.8, 73.36666666666666, 71.0, 69.2, 70.13333333333334, 71.93333333333334, 70.16666666666667] ,
            #             [82.3, 78.8, 100.0, 82.2, 81.53333333333333, 81.8, 77.7, 80.13333333333334, 82.23333333333333, 84.3]
            #         ]
            # },
            "2": {
                1600: [
                        [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                        [73.1, 72.36666666666666, 73.63333333333334, 61.8, 73.2, 73.13333333333334, 72.13333333333334, 70.9, 65.5, 71.43333333333334],
                        [60.3, 56.0, 59.4, 59.333333333333336, 60.46666666666667, 63.266666666666666, 56.0, 57.233333333333334, 52.63333333333333, 57.166666666666664],
                        [46.96666666666667, 48.7, 54.96666666666667, 54.166666666666664, 57.766666666666666, 49.96666666666667, 48.333333333333336, 48.46666666666667, 60.233333333333334, 56.86666666666667],
                        [52.1, 50.666666666666664, 52.666666666666664, 46.93333333333333, 48.266666666666666, 48.6, 44.43333333333333, 46.13333333333333, 53.333333333333336, 48.46666666666667],
                        [57.3, 51.833333333333336, 55.9, 52.4, 57.36666666666667, 53.266666666666666, 57.233333333333334, 58.03333333333333, 60.06666666666667, 54.63333333333333],
                        [62.3, 64.1, 63.1, 60.4, 62.8, 64.2, 66.13333333333334, 64.13333333333334, 62.8, 65.03333333333333],
                        [67.23333333333333, 67.3, 67.4, 67.56666666666666, 68.23333333333333, 67.7, 68.26666666666667, 68.4, 67.7, 68.1],
                        [71.6, 69.83333333333333, 70.93333333333334, 72.43333333333334, 71.56666666666666, 71.86666666666666, 70.83333333333333, 70.56666666666666, 72.96666666666667, 69.76666666666667],
                        [80.23333333333333, 77.33333333333333, 97.66666666666667, 90.4, 84.2, 99.56666666666666, 77.66666666666667, 84.33333333333333, 77.66666666666667, 82.3]
                    ]
            },
            "3": {
                1600: [
                    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                    [72.8, 63.1, 76.53333333333333, 72.0, 71.93333333333334, 69.53333333333333, 74.43333333333334, 69.6, 68.76666666666667, 75.36666666666666],
                    [50.3, 63.333333333333336, 57.666666666666664, 53.56666666666667, 52.63333333333333, 59.333333333333336, 53.766666666666666, 56.9, 58.86666666666667, 62.266666666666666],
                    [46.63333333333333, 57.4, 48.53333333333333, 52.46666666666667, 50.833333333333336, 52.3, 55.46666666666667, 58.5, 50.9, 51.4],
                    [47.56666666666667, 49.36666666666667, 49.53333333333333, 50.56666666666667, 53.53333333333333, 51.56666666666667, 49.46666666666667, 51.833333333333336, 55.1, 51.1],
                    [58.03333333333333, 53.53333333333333, 48.2, 58.36666666666667, 55.2, 55.46666666666667, 58.56666666666667, 56.233333333333334, 58.86666666666667, 51.7],
                    [63.56666666666667, 64.46666666666667, 63.9, 65.4, 65.43333333333334, 63.96666666666667, 57.3, 64.0, 66.53333333333333, 64.1],
                    [66.33333333333333, 67.43333333333334, 67.26666666666667, 67.06666666666666, 66.63333333333334, 67.56666666666666, 67.93333333333334, 67.06666666666666, 67.1, 67.66666666666667],
                    [69.76666666666667, 69.7, 68.66666666666667, 69.6, 70.86666666666666, 71.03333333333333, 70.26666666666667, 71.03333333333333, 70.86666666666666, 69.46666666666667],
                    [80.7, 100.0, 78.96666666666667, 83.26666666666667, 77.5, 80.8, 79.96666666666667, 83.06666666666666, 81.5, 82.8]
                ]
            },
            "4": {
                1600: [
                    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                    [65.7, 72.23333333333333, 68.9, 69.73333333333333, 70.26666666666667, 70.33333333333333, 66.63333333333334, 70.36666666666666, 69.33333333333333, 72.03333333333333],
                    [60.0, 60.3, 57.6, 59.93333333333333, 56.63333333333333, 59.833333333333336, 61.1, 55.46666666666667, 61.4, 53.93333333333333],
                    [57.3, 53.833333333333336, 56.03333333333333, 56.06666666666667, 57.6, 48.8, 51.6, 53.13333333333333, 54.666666666666664, 49.3],
                    [46.233333333333334, 49.36666666666667, 48.93333333333333, 53.46666666666667, 52.06666666666667, 51.833333333333336, 43.833333333333336, 57.96666666666667, 54.5, 44.7],
                    [57.56666666666667, 61.7, 53.1, 53.833333333333336, 47.233333333333334, 54.43333333333333, 56.53333333333333, 49.666666666666664, 54.166666666666664, 57.666666666666664],
                    [62.333333333333336, 62.93333333333333, 64.33333333333333, 63.8, 66.1, 63.733333333333334, 65.43333333333334, 65.56666666666666, 65.06666666666666, 63.666666666666664],
                    [67.03333333333333, 67.66666666666667, 66.56666666666666, 67.0, 66.73333333333333, 67.7, 67.13333333333334, 67.83333333333333, 66.76666666666667, 66.56666666666666],
                    [70.86666666666666, 72.26666666666667, 72.9, 69.8, 72.8, 69.76666666666667, 70.1, 70.2, 71.8, 71.13333333333334],
                    [83.7, 79.13333333333334, 83.9, 91.36666666666666, 85.13333333333334, 80.1, 84.76666666666667, 82.46666666666667, 83.76666666666667, 100.0]
                ]
            }
        }
    else:
        raw_data = {
            "All": {
                1600: [
                    [100.0, 99.95, 100.0, 100.0, 100.0, 100.0, 99.95, 100.0, 100.0, 100.0],
                    [56.25, 53.75, 56.6, 56.3, 55.55, 57.55, 55.8, 55.95, 56.3, 58.7],
                    [55.1, 53.8, 54.65, 53.0, 53.4, 53.7, 53.65, 54.65, 54.7, 52.2],
                    [54.45 , 53.1 , 52.85 , 52.35 , 51.75 , 53.05 , 51.85 , 53.25 , 52.25 , 51.8],
                    [50.25 , 51.6 , 49.2 , 49.6 , 50.05 , 49.7 , 49.35 , 50.2 , 50.4 , 50.85],
                    [51.15, 49.3, 51.15, 48.7, 49.7, 49.55, 50.35, 50.3, 50.25, 51.1],
                    [51.95, 51.8, 49.45, 49.9, 50.9, 51.7, 53.9, 49.45, 49.55, 49.25],
                    [54.95, 52.4, 56.3, 49.9, 51.1, 56.7, 54.9, 50.4, 54.3, 49.5],
                    [51.26, 51.21, 51.56, 53.39, 51.41, 54.13, 49.73, 51.81, 50.07, 53.19],
                    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
                ]
            },
            "1": {
                1600: [
                    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                    [54.25, 55.85, 56.1, 56.4, 56.2, 56.8, 55.85, 56.35, 54.0, 57.4],
                    [51.45, 53.2, 51.9, 52.3, 52.95, 52.35, 52.65, 53.5, 52.8, 53.1],
                    [51.65, 51.05, 50.45, 50.7, 51.25, 50.4, 51.1, 50.45, 50.3, 51.4],
                    [49.3, 50.3, 51.5, 50.25, 49.95, 50.2, 50.1, 50.4, 49.85, 49.95],
                    [50.5, 50.05, 52.95, 51.4, 51.6, 51.9, 51.2, 52.2, 50.8, 51.5],
                    [49.45, 49.6, 49.4, 49.5, 49.95, 50.2, 49.65, 49.85, 50.8, 49.75],
                    [49.55, 49.75, 50.05, 49.75, 49.7, 50.95, 49.35, 49.9, 49.75, 49.6],
                    [51.41, 51.90, 52.00, 51.21, 53.14, 51.46, 51.31, 51.76, 51.01, 52.05],
                    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
                ]
            },
            "2": {
                1600: [
                    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                    [55.55, 54.3, 56.7, 54.85, 52.3, 52.25, 56.3, 52.4, 56.45, 57.15],
                    [51.8, 51.65, 51.45, 51.85, 52.9, 51.7, 51.4, 51.8, 50.75, 52.5],
                    [51.65, 50.9, 51.95, 52.1, 51.6, 51.45, 51.25, 52.25, 49.5, 50.75],
                    [52.7, 49.55, 48.8, 48.55, 50.0, 50.1, 49.05, 50.35, 50.0, 49.2],
                    [48.8, 51.95, 52.5, 50.55, 51.15, 51.3, 52.25, 49.9, 50.7, 50.65],
                    [50.1, 49.05, 50.3, 49.75, 49.3, 50.65, 49.35, 49.5, 49.85, 50.6],
                    [50.6, 50.15, 50.55, 49.7, 50.8, 50.15, 50.0, 49.85, 51.1, 50.0],
                    [52.60, 51.51, 55.02, 51.61, 51.81, 51.36, 52.75, 52.35, 51.95, 51.11],
                    [100.0, 100.0, 100.0, 100.0, 100.0,100.0, 100.0, 100.0, 100.0, 100.0]
                ]
            },
            "3": {
                1600: [
                    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                    [54.4, 52.55, 55.1, 55.6, 59.8, 52.4, 59.15, 52.35, 58.05, 59.65],
                    [52.2, 53.25, 53.25, 53.15, 53.05, 50.0, 54.1, 52.4, 53.6, 54.05],
                    [50.4, 50.2, 51.65, 52.35, 51.75, 52.85, 50.7, 51.3, 52.0, 52.2],
                    [50.45, 49.85, 52.0, 50.25, 49.65, 50.4, 47.9, 50.0, 49.75, 50.0],
                    [48.45, 49.0, 49.05, 48.1, 49.75, 50.2, 52.85, 50.35, 52.8, 50.5],
                    [50.0, 49.55, 49.85, 50.2, 49.5, 50.0, 50.45, 49.35, 49.45, 50.1],
                    [49.7, 50.65, 50.35, 51.3, 50.55, 49.8, 50.15, 49.7, 50.0, 50.05],
                    [52.5, 52.0, 51.71, 52.8, 49.93, 51.46, 51.26, 51.11, 51.06, 56.16],
                    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]   
                ]
            },
            "4": {
                1600: [
                    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
                    [55.9, 59.7, 54.6, 53.75, 57.4, 56.75, 57.95, 57.65, 57.0, 54.45],
                    [54.45, 55.05, 52.9, 54.7, 52.55, 52.5, 53.8, 53.5, 53.9, 55.15],
                    [51.5, 51.1, 52.15, 52.45, 52.2, 52.15, 52.65, 51.1, 51.5, 51.85],
                    [48.7, 50.45, 51.15, 49.5, 50.2, 47.8, 50.05, 48.15, 50.55, 50.65],
                    [50.5, 51.3, 50.4, 49.7, 48.2, 49.6, 49.4, 50.65, 47.8, 51.05],
                    [50.05, 49.85, 50.25, 50.25, 50.55, 49.5, 50.3, 49.45, 49.25, 49.15],
                    [54.48, 52.20, 51.46, 53.24, 61.80, 52.75, 52.15, 52.00, 51.66, 52.75],
                    [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
                ]
            }
        }

    focus_n = 1600
    for n, v1 in raw_data.items():
        if focus_n not in v1:
            continue
        v2 = v1[focus_n]

        # This data was for 1-ratio, so flip before plotting
        if args.filter == "race":
            v2 = v2[::-1]

        for i in range(len(v2)):
            for j in range(len(v2[i])):
                data.append([categories[i], v2[i][j], n])

    df = pd.DataFrame(data, columns=columns)
    sns_plot = sns.boxplot(x=columns[0], y=columns[1], hue=columns[2],
                           data=df, showfliers=False)

    if args.novtitle:
        plt.ylabel("", labelpad=0)

    # Accuracy range, with space to show good performance
    sns_plot.set(ylim=(45, 101))

    # Add dividing line in centre
    lower, upper = plt.gca().get_xlim()
    midpoint = (lower + upper) / 2
    plt.axvline(x=midpoint, color='white' if args.darkplot else 'black',
                linewidth=1.0, linestyle='--')

    # Map range to numbers to be plotted
    targets_scaled = range(int((upper - lower)))
    # plt.plot(targets_scaled, baselines, color='C1', marker='x', linestyle='--')

    if not args.legend:
        plt.legend([],[], frameon=False)

    # Make sure axis label not cut off
    plt.tight_layout()

    sns_plot.figure.savefig("./meta_boxplot_varying_n_%s_%d.png" % (args.filter, focus_n))
