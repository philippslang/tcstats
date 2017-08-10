import matplotlib.pyplot as plt
import numpy as np

plt.style.use('ggplot')


def histogram(vals):
    n, bins, patches = plt.hist(vals, 50, normed=1)
    plt.show()
