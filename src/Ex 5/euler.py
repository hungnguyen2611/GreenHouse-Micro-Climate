N = 600000

# ------------Euler---------------
def euler(dx, init_vp_air, init_vp_top, t0, h):
    number_of_steps = N
    t = np.zeros(number_of_steps + 1)
    f = np.zeros((number_of_steps + 1, 2))
    f[0, 0] = init_vp_air
    f[0, 1] = init_vp_top
    t[0] = t0
    data = pd.read_excel("dataset.xlsx")
    df = pd.DataFrame(data)
    i = 0
    for k in range(number_of_steps):
        if (k % 300) == 0:
            global T_AIR, T_OUT, T_TOP, V_WIND, U_ROOF, U_TH_SCR
            T_AIR = float(df.at[i, "Tair"])
            T_OUT = float(df.at[i, "Tout"])
            T_TOP = float(df.at[i, "Ttop"])
            V_WIND = float(df.at[i, "Vwind"])
            U_ROOF = U_TH_SCR = 0.3
            U_ROOF = float(df.at[i, "Uroof"])
            U_TH_SCR = float(df.at[i, "UThScr"])
            i += 1
        t[k + 1] = t[k] + h
        f[k + 1, 0] = f[k, 0] + h * dx(f[k, 0], f[k, 1])[0]
        f[k + 1, 1] = f[k, 1] + h * dx(f[k, 0], f[k, 1])[1]
    return f, t

