import matplotlib.pyplot as plt

def plot_graph(main_line, bottom_line, top_line, color, x_):
    plt.figure(figsize=(10, 5))
    ax = plt.gca()
    ax.plot(main_line, means, color = 'b', label = 'Mean')
    ax.fill_between(sampling_values, bottom_line, top_line, color = 'b', alpha = 0.1)