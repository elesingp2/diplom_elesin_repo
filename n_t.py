
# Redefine constants to ensure continuity
a1 = 2
T_per = 1  # Small period
T_ust = 10  # Large period

# Define time arrays for each segment
t_exp1 = np.linspace(0, T_per, 500)
t_const = np.linspace(T_per, T_per + 1, 500)
t_exp2 = np.linspace(T_per + 1, T_per + 1 + T_ust, 500)

# Define the functions ensuring continuity and start from (0,0)
exp1 = a1 * (np.exp(t_exp1 / T_per) - 1)
const = np.ones_like(t_const) * exp1[-1]
exp2 = const[-1] * np.exp(-(t_exp2 - (T_per + 1)) / T_ust)

# Concatenate the time and function arrays
t_total = np.concatenate((t_exp1, t_const, t_exp2))
f_total = np.concatenate((exp1, const, exp2))

# Create a step function overlay for the right-side exponential part
step_intervals = 10
step_t = np.linspace(T_per + 1, T_per + 1 + T_ust, step_intervals)
step_f = const[-1] * np.exp(-(step_t - (T_per + 1)) / T_ust)

# Plot the functions with step function overlay
plt.figure(figsize=(10, 6))
plt.plot(t_total, f_total, label='Combined Function', color='blue')
plt.step(step_t, step_f, where='post', label='Step Function', color='orange')
plt.axvline(x=T_per, color='red', linestyle='--', label='T_per Boundary')
plt.axvline(x=T_per + 1, color='green', linestyle='--', label='T_ust Boundary')
plt.xlabel('Time')
plt.ylabel('Function Value')
plt.title('Combined Exponential and Constant Function with Step Function Overlay')
plt.legend()
plt.grid(True)
plt.show()
