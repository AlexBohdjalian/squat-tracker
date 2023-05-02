import numpy as np
import matplotlib.pyplot as plt

latency_measurements = [1.61, 1.81, 1.9, 1.31, 1.48, 1.5, 1.46, 1.4, 1.26, 1.23, 1.7, 1.3, 1.56, 1.2, 1.34, 1.4, 1.67, 1.81, 1.51, 1.34, 1.2, 1.13, 1.42, 1.23, 1.54]

mean_latency = np.mean(latency_measurements)
std_dev = np.std(latency_measurements)

# calculate the standard error of the mean (SEM)
sem = std_dev / np.sqrt(len(latency_measurements))
error_bar_len = sem

# plot the latency measurements as a scatter plot
plt.scatter(range(len(latency_measurements)), latency_measurements)
plt.axhline(y=mean_latency, color='r', linestyle='-')

# plot the error bars
plt.errorbar(range(len(latency_measurements)), latency_measurements, yerr=error_bar_len, fmt='none')

# add the SEM and average as text to the plot
plt.text(0.5, 0.95, f"Standard Error of Mean = {sem:.3f}", transform=plt.gca().transAxes, ha='center', va='top')
plt.text(0.5, 0.9, f"Average = {mean_latency:.3f}", transform=plt.gca().transAxes, ha='center', va='top')

# set the x-axis label and tick labels
plt.xlabel('Measurement Number')
plt.xticks(range(len(latency_measurements)), [str(i+1) for i in range(len(latency_measurements))])

# set the y-axis label and tick labels
plt.ylabel('Latency (seconds)')
plt.yticks(np.arange(0.5, 2.5, 0.1))

# save the plot
plt.title('Latency Measurements')
plt.savefig('./assets/processed/live_analysis_latency_graph.png')
