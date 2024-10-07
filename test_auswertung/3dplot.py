import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define the function
def expression_diff(x0, x1):
    expr1 = x0 / (2 * x1 + 2.0)
    expr2 = x0 / (x1 + (x1 + 1.0)**1.0 + 1.0)
    expr3 = 0.5 * x0 * np.arcsin(np.sin(1 / (x1 + 1.0)))
    return expr1 - expr2

# Create meshgrid
x0 = np.linspace(-2, 2, 50)
x1 = np.linspace(-2, 2, 50)
X0, X1 = np.meshgrid(x0, x1)
Z = expression_diff(X0, X1)

# Plotting the 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X0, X1, Z, cmap='viridis')

ax.set_xlabel('x_0')
ax.set_ylabel('x_1')
ax.set_zlabel('Differenz')
ax.set_title('3D Plot der Differenz zwischen f und f\'')

plt.savefig("3D_Plot_Difference(true).pdf", format='pdf')

plt.show()
