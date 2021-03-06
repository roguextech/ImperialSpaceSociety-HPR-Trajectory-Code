import numpy as np
import scipy.integrate as spi
import matplotlib.pyplot as plt


def stage1(t, z):
    rho = 1.22
    A = 2.552 * 10 ** -3
    C_d = 0.75
    mdot = 0.2225  # kg/s - mass flow rate
    u_e = 2175  # m/s

    h = z[0]  # initial values
    v = z[1]
    m = z[2]

    dhdt = v
    dvdt = - 9.81 - (0.5 * rho * v ** 2) * C_d * A / m + (mdot * u_e) / m
    dmdt = - mdot
    return [dhdt, dvdt, dmdt]


def stage2(t, z):
    rho = 1.22
    A = 2.552 * 10 ** -3
    C_d = 0.75
    mdot = 0.1915  # kg/s - mass flow rate
    u_e = 1947.8  # m/s

    h = z[0]  # initial values
    v = z[1]
    m = z[2]

    dhdt = v
    dvdt = - 9.81 - (0.5 * rho * v ** 2) * C_d * A / m + (mdot * u_e) / m
    dmdt = - mdot
    return [dhdt, dvdt, dmdt]


def coast(t, z):
    rho = 1.22
    A = 2.552 * 10 ** -3
    C_d = 0.75

    h = z[0]  # initial values
    v = z[1]
    m = z[2]

    dhdt = v
    dvdt = - 9.81 - (0.5 * rho * v ** 2) * C_d * A / m
    dmdt = 0
    return [dhdt, dvdt, dmdt]


def accel(m, v, phase):
    rho = 1.22
    A = 2.552 * 10 ** -3
    C_d = 0.75

    if phase == 0:  # lower stage burn
        mdot = 0.2225  # kg/s - mass flow rate
        u_e = 2175
        return - 9.81 - (0.5 * rho * v ** 2) * C_d * A / m + (mdot * u_e) / m

    elif phase == 1:  # coasting
        return - 9.81 - (0.5 * rho * v ** 2) * C_d * A / m

    elif phase == 2:  # upper stage
        mdot = 0.1915  # kg/s - mass flow rate
        u_e = 1947.8
        return - 9.81 - (0.5 * rho * v ** 2) * C_d * A / m + (mdot * u_e) / m


m_init = 4.4  # initial fully loaded mass in kg
num = 100
# 1st burn
z0 = [0, 0, m_init]  # setting initial conditions [height, velocity, mass]
t_end = 0.2472 / 0.2225
t = np.linspace(0, t_end, num)
sol = spi.solve_ivp(stage1, (0, t_end), z0, t_eval=t)

# Coast for 1 second
z1 = [sol.y[0, -1], sol.y[1, -1], sol.y[2, -1]]
ct = t_end + 0.5
t2 = np.linspace(t_end, ct, num)
sol2 = spi.solve_ivp(coast, (t_end, ct), z1, t_eval=t2)

# 2nd Burn
z2 = [sol2.y[0, -1], sol2.y[1, -1], sol2.y[2, -1] - 1.995]  # taking into account bottom stage mass loss
t2_end = 0.337 / 0.1915
t3 = np.linspace(ct, ct + t2_end, num)
sol3 = spi.solve_ivp(stage2, (ct, ct + t2_end), z2, t_eval=t3)

# Final Coast
z3 = [sol3.y[0, -1], sol3.y[1, -1], sol3.y[2, -1]]
cstart = ct + t2_end
t4 = np.linspace(cstart, cstart + 17, num)
sol4 = spi.solve_ivp(coast, (cstart, cstart + 17), z3, t_eval=t4)

time = np.concatenate((sol.t, sol2.t, sol3.t, sol4.t))

height = np.concatenate((sol.y[0, :], sol2.y[0, :], sol3.y[0, :], sol4.y[0, :]))
print(f"The Max Height is {max(height)} m")

velocity = np.concatenate((sol.y[1, :], sol2.y[1, :], sol3.y[1, :], sol4.y[1, :]))
print(f"The Max velocity is {max(velocity)} m/s")

mass = np.concatenate((sol.y[2, :], sol2.y[2, :], sol3.y[2, :], sol4.y[2, :]))

boost_1 = [0] * num
for i in range(num):
    m = sol.y[2, i]
    for j in range(num):
        v = sol.y[1, i]
        boost_1[i] = accel(m, v, 0)
        break

coast_1 = [0] * num
for i in range(num):
    m = sol2.y[2, i]
    for j in range(num):
        v = sol2.y[1, i]
        coast_1[i] = accel(m, v, 1)
        break

boost_2 = [0] * num
for i in range(num):
    m = sol3.y[2, i]
    for j in range(num):
        v = sol3.y[1, i]
        boost_2[i] = accel(m, v, 2)
        break

coast_2 = [0] * num
for i in range(num):
    m = sol4.y[2, i]
    for j in range(num):
        v = sol4.y[1, i]
        coast_2[i] = accel(m, v, 1)
        break

accel = np.concatenate((boost_1, coast_1, boost_2, coast_2))/9.81

grad = np.gradient(velocity, time) /9.81 # should get same results, this is a 2nd order central diff scheme

plt.figure(0)
plt.plot(time, height, label='Height')
plt.xlabel('Time (seconds)')
plt.ylabel('Height (m)')
plt.legend()

plt.figure(1)
plt.plot(time, velocity, label='Velocity')
plt.xlabel('Time (seconds)')
plt.ylabel('Velocity (m/s)')
plt.legend()

plt.figure(2)
plt.plot(time, mass, label='Mass')
plt.xlabel('Time (seconds)')
plt.ylabel('Mass (kg)')
plt.legend()
plt.show()

plt.figure(3)
plt.plot(time, accel, label='Acceleration')
plt.plot(time, grad, 'r*', label='Gradient')  # verification
plt.xlabel('Time (seconds)')
plt.ylabel('Acceleration in Gs (m/s^2)')
plt.legend()
plt.show()
