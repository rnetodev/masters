import math

import numpy as np
from graphviz import Digraph
from skmultiflow.drift_detection.base_drift_detector import BaseDriftDetector


class MarkovChain:
    def __init__(self):
        self.system = {}

    def add(self, origin, destination, alpha):
        if origin not in self.system:
            self.system[origin] = {}
            self.system[origin][destination] = 1.0
            return

        if destination not in self.system[origin]:
            self.system[origin][destination] = 0.0

        for prev_destination in self.system[origin].keys():
            if prev_destination == destination:
                new_probability = self.system[origin][prev_destination] + alpha
                self.system[origin][prev_destination] = (
                    new_probability if new_probability <= 1 else 1
                )
            else:
                self.system[origin][prev_destination] -= alpha / (
                    len(self.system[origin]) - 1
                )

    def to_graphviz(self, output_filename):
        dot = Digraph(comment="RBF")

        # nodes
        for origin in self.system.keys():
            dot.node(str(origin))

        # edges
        for origin in self.system.keys():
            for destination in self.system[origin].keys():
                dot.edge(
                    str(origin),
                    str(destination),
                    constraint="false",
                    label=str(self.system[origin][destination]),
                )

        print(dot.source)
        dot.render('markov.gv', view=True)



class RBF(BaseDriftDetector):
    """ Radial Basis Functions - Drift Detection Method.

    Parameters
    ----------
    sigma: float (default=2)
        Delimits the Gaussian radius.

    lambda_: float (default=0.5)
        Minimum threshold.

    alpha: float (default=0.25)
        Value to increase the probability in the Markov Chain.
    """

    def __init__(self, sigma=2, lambda_=0.5, alpha=0.25):
        super().__init__()
        self.sigma = sigma
        self.lambda_ = lambda_
        self.alpha = alpha

        self.actual_center = None
        self.centers = []
        self.sample_count = 0

        self.markov = MarkovChain()

        self.reset()

    def reset(self):
        """ reset

        Resets the change detector parameters.

        """
        super().reset()
        self.sample_count = 1
        # Reset or not the markov
        # self.markov = MarkovChain()

    def add_element(self, input_data):
        """ Add a new element to the statistics

        Parameters
        ----------
        prediction: float
        """
        if self.in_concept_change:
            self.reset()

        self.sample_count += 1

        activation = 0.0
        activation_lambda = self.lambda_
        distance = 0.0
        activated_center = None

        for center in self.centers:
            distance = math.sqrt(math.pow(input_data - center, 2.0))
            activation = math.exp(-math.pow(self.sigma * distance, 2))

            if activation >= activation_lambda:
                activated_center = center
                activation_lambda = activation

        if not activated_center:
            self.centers.append(input_data)
            activated_center = input_data

        if activated_center != self.actual_center:
            if self.actual_center is None:
                self.actual_center = activated_center

                self.markov.add(self.actual_center, activated_center, self.alpha)
            else:
                self.markov.add(self.actual_center, activated_center, self.alpha)

                self.actual_center = activated_center
                self.in_concept_change = True


if __name__ == "__main__":
    rbf = RBF(sigma=2, lambda_=0.5, alpha=0.25)

    data_stream = [
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.9,
        0.10,
        0.11,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.1,
        0.1,
        0.1,
        0.1,
        0.1,
        0.16,
        0.16,
        0.16,
        0.15,
        0.6,
        0.5,
        0.1,
        0.1,
    ]

    for index, value in enumerate(data_stream):
        rbf.add_element(value)

        print(f"index={index}/value={value}/markov={rbf.markov.system}")

        if rbf.detected_change():
            print(
                "\t * Change has been detected in data: "
                + str(value)
                + " - of index: "
                + str(index)
            )

    rbf.markov.to_graphviz(None)
