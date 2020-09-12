import numpy as np
from sklearn import datasets
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import pandas as pd
import sys
import argparse
from utils import *

np.random.seed(0)

class Layer():
    def __init__(self, input_size, output_size, activation, activation_prime):
        self.weights = np.random.randn(input_size, output_size) / np.sqrt(input_size)
        self.bias = np.zeros((1, output_size))
        self.activation = activation
        self.activation_prime = activation_prime

    def forward_propagation(self, input_data, activated_data):
        self.input = input_data
        self.activated_input = activated_data
        if (len(activated_data) != 0):
            self.output = np.dot(self.activated_input, self.weights) + self.bias
        else:
            self.output = np.dot(self.input, self.weights) + self.bias
        self.output_activated = self.activation(self.output)
        return self.output_activated, self.output

    def backward_propagation(self, output_error, learning_rate, y, last_layer):
        if (last_layer == False):
            output_derivative = self.activation_prime(self.output) * output_error
        else:
            output_derivative = self.activation_prime(self.output_activated, y)
        input_error = np.dot(output_derivative, self.weights.T)
        if (len(self.activated_input) != 0):
            weights_error = np.dot(self.activated_input.T, output_derivative)
        else:
            weights_error = np.dot(X_train.T, output_derivative)
        self.weights -= learning_rate * weights_error
        self.bias -= learning_rate * np.sum(output_derivative, axis=0)
        return input_error

def process_file():
    df = pd.read_csv('data.csv')
    i = 0
    header = []
    while i < len(df.columns):
        if (i == 0):
            header.append('Index')
        elif (i == 1):
            header.append('State')
        else:
            header.append('Col-' + str(i))
        i+=1

    df.columns = header
    index = df['Index']
    state = df['State']
    df = df.drop(columns=['Index', 'State'])
    df = ((df-df.min())/(df.max()-df.min()))
    df['Index'] = index

    X = np.array(df[['Col-25', 'Col-29', 'Col-9', 'Col-24', 'Col-12']])
    y = np.array(pd.get_dummies(state))
    return train_test_split(X, y, test_size=0.1, train_size=0.9, shuffle=True)

X_train, X_test, y_train, y_test = process_file()
lsl = len(X_train)

def cost(layers, x, y):
    output = x
    output_activated = []
    for layer in layers:
        output_activated, output = layer.forward_propagation(output, output_activated)
    rez = -(1 / lsl) * np.sum(np.nan_to_num(y * np.log(output_activated + 1e-15) + (1 - y) * np.log(1 - (output_activated + 1e-15))))
    return rez

def predict(layers):
    output = X_test
    output_activated = []
    for layer in layers:
        output_activated, output = layer.forward_propagation(output, output_activated)
    return np.argmax(output, axis=1)

def create_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cost", type=int, help="Choose when to print cost", default=1)
    parser.add_argument("-zg", "--zoom", type=int, help="Choose where the plot start", default=0)
    parser.add_argument("-pc", "--plot_cost", help="Plot a graph of the cost", action="store_true")
    parser.add_argument("-pr", "--plot_result", help="Scatter the result", action="store_true")
    parser.add_argument("-m", "--mute", help="Mute cost prints", action="store_true")
    args = parser.parse_args()
    return args

def train(nn_hdim, num_passes, print_loss, cost_print, zoom, mute):
    layers = []
    layers.append(Layer(5, nn_hdim, sigmoid, dSigmoid))
    layers.append(Layer(nn_hdim, nn_hdim, sigmoid, dSigmoid))
    layers.append(Layer(nn_hdim, 2, softmax, dCrossEntropy))
    training_cost = []
    validate_cost = []
    for i in range(0, num_passes):
        output_activated = []
        output = X_train
        for layer in layers:
            output_activated, output = layer.forward_propagation(output, output_activated)
        length = len(layers)
        while (length > 0):
            if (length == 3):
                error = layers[length - 1].backward_propagation(None, 0.01, y_train, True)
            else:
                error = layers[length - 1].backward_propagation(error, 0.01, None, False)
            length -= 1
        if (i >= zoom):
            training_error = cost(layers, X_train, y_train)
            validate_error = cost(layers, X_test, y_test)
            training_cost.append(training_error)
            validate_cost.append(validate_error)
            if (i % cost_print == 0 and mute == True):
                print('Epoch: ', i, '/', num_passes, 'TC =', training_error, 'VC =', validate_error)

    return layers, training_cost, validate_cost

if __name__ == "__main__":
    options = create_options()
    if (options.cost < 1):
        print('The cost must be higher than 0.')
    layers, training_errors, validate_errors = train(9, 20000, True, options.cost, options.zoom, options.mute)

    if (options.plot_cost == True):
        plt.plot(training_errors)
        plt.plot(validate_errors)
        if (options.plot_result == False):
            plt.show()
    if (options.plot_result == True):
        y = np.argmax(y_test, axis=1)
        y_predicted = predict(layers)
        fig, ax = plt.subplots()
        ax.scatter(y, list(range(0, len(y))), color="red", alpha=0.5, label="True values")
        ax.scatter(y_predicted, list(range(0, len(y))), color="blue", alpha=0.5, label="Predicted values")
        plt.legend()
        ax.set_xlabel('Patient number')
        ax.set_ylabel('Result')
        plt.xticks([0, 1], ['Begnin', 'Malignant'])
        plt.show()
