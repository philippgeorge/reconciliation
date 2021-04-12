# Leading Question:
# How fast are the reconciliation methods?
import auxiliary_functions as aux
import plotting as plot
import sys

runtimes = aux.runtimes

# Plotting
#runtimes = {k: v for k, v in sorted(runtimes.items(), key=lambda item: item[1], reverse=True)}
# Plot as horizontal bars
x = list(runtimes.keys())
y = list(runtimes.values())
plot.horizontal_bar_plot(x, y)
    


