import numpy as np
from math import sqrt
import pandas as pd
from matplotlib import pyplot as plt
import xlsxwriter

# constant

N_HEAT_VAP = 4.43 * pow(10, -8)
U_BLOW = 0.5
P_BLOW = 0.5 * pow(10, 6)
A_FLR = 1.4 * 10000
U_FOG = 0.5
O_FOG = 0
P_AIR = 1.215
U_PAD = 0.5
O_PAD = 0
N_PAD = 0
X_PAD = 0
X_OUT = 0
M_WATER = 18.0
R = 8.314 * pow(10, 3)

S_MV_12 = -0.1
VP_THSCR = 2939.2

T_THSCR = 297.0
VP_COV_IN = 2939.2
C_HEC_IN = 1.86
A_COV = 1.8 * pow(10, 4)

VP_MECH = 0
U_MECH_COOL = 0
COP_MECHCOOL = 0
P_MECHCOOL = 0
T_MECH = 0
DELTA_H = 2.45 * pow(10, 6)
T_COV_IN = 297.0
CP_AIR = pow(10, 3)
LAI = 2.0
Y = 65.8
R_B = 275.0
R_S = 82.0
VP_CAN = 2767.7
G = 9.81
S_INS_SCR = 1.0
P_TOP = 1.52
K_THSCR = 0.05 * pow(10, -3)
C_LEAKAGE = pow(10, -4)

CD = 0.75

U_SIDE = 0.5
A_ROOF = 0.14 * 10000
A_SIDE = 0
H_SIDE_ROOF = 0

CW = 0.09
N_SIDE = 1.1
N_SIDE_TH = 0
U_VENTFORCED = 0.5
O_VENTFORCED = 0
H_VENT = 1.6
N_ROOF = 1.3
N_ROOF_TH = 0.9
VP_OUT = 998.73
H_AIR = 3.8
H_TOP = 0.4
epxilon = pow(10, -8)

T_AIR = 293.25
T_OUT = 290.85
T_TOP = 294.25
V_WIND = 3.2
U_ROOF = 0.006
U_THSCR = 0
# --------

# --------Cap---------------------

def Cap_VP_Air(M_Water, H_Air, R, T_Air):
    return (M_Water * H_Air) / (R * T_Air)


def Cap_VP_Top(M_Water, H_Top, R, T_Top):
    return (M_Water * H_Top) / (R * T_Top)


# --------MV_BlowAir--------------

def MV_BlowAir(N_Heat_Vap, U_Blow, P_Blow, A_Flr):
    return (N_Heat_Vap * U_Blow * P_Blow) / A_Flr


# ---------MV_FogAir-------------

def MV_FogAir(U_Fog, O_Fog, A_Flr):
    return (U_Fog * O_Fog) / A_Flr


# ----------MV_PadAir------------

def MV_PadAir(U_Pad, O_Pad, P_Air, N_Pad, X_Pad, X_Out, A_Flr):
    return (U_Pad * O_Pad * P_Air * (N_Pad * (X_Pad - X_Out) + X_Out)) / A_Flr


# ------------MV_AirOut_Pad-------

def MV_AirOut_Pad(U_Pad, O_Pad, A_Flr, M_Water, R, VP_Air, T_Air):
    return (U_Pad * O_Pad * M_Water * VP_Air) / A_Flr * R * T_Air


# ------------MV_Air_ThScr--------------

def HEC_Air_ThScr(U_ThScr, T_ThScr, T_Air):
    return 1.7 * U_ThScr * pow(abs(T_Air - T_ThScr), 0.33)


def MV_Air_ThScr(S_MV_Air_ThScr, VP_Air, VP_ThScr, HEC_Air_ThScr):
    return (6.4 * pow(10, -9) * HEC_Air_ThScr * (VP_Air - VP_ThScr)) / (
                1 + pow(2.718, S_MV_Air_ThScr * (VP_Air - VP_ThScr)))


# ----------MV_Top_Cov_in-------------

def HEC_Top_Cov_in(c_Hec_in, T_Top, T_Cov_in, A_Cov, A_Flr):
    return c_Hec_in * pow(abs(T_Top - T_Cov_in), 0.33) * A_Cov / A_Flr


def MV_Top_Cov_in(S_MV_Top_Cov_in, VP_Top, VP_Cov_in, HEC_Top_Cov_in):
    a = 1 + pow(2.718, S_MV_Top_Cov_in * (VP_Top - VP_Cov_in))
    return (6.4 * pow(10, -9) * HEC_Top_Cov_in * (VP_Top - VP_Cov_in)) / a

# ----------MV_AirMech---------------

def HEC_AirMech(U_MechCool, COP_MechCool, P_MechCool, A_Flr, T_Air, T_Mech, Delta_H, VP_Air, VP_MechCool):
    a = U_MechCool * COP_MechCool * P_MechCool / A_Flr
    b = T_Air - T_Mech + 6.4 * pow(10, -9) * Delta_H * (VP_Air - VP_MechCool)
    return a / b


def MV_Air_Mech(S_MV_Air_Mech, VP_Mech, VP_Air, HEC_Air_Mech):
    return (6.4 * pow(10, -9) * HEC_Air_Mech * (VP_Air - VP_Mech)) / (
                1 + pow(2.718, S_MV_Air_Mech * (VP_Air - VP_Mech)))


# ----------f-Formula------------

def f_ThScr(U_ThScr, K_ThScr, T_Air, T_Top, g, p_Air, p_Top):
    a = U_ThScr * K_ThScr * pow(abs(T_Air - T_Top), 2 / 3)
    PMean_Air = (p_Air + p_Top) / 2
    b = (1 - U_ThScr) * pow(g * (1 - U_ThScr) * abs(p_Air - p_Top) / (2 * PMean_Air), 1 / 2)
    return a + b


def fleakage(cleakage, vWind):
    if vWind < 0.25:
        return 0.25 * cleakage
    else:
        return vWind * cleakage


def nInsScr(sInsScr):
    return sInsScr * (2 - sInsScr)


def f_Vent_Roof_Side(Cd, AFlr, URoof, USide, ARoof, ASide, g, hSideRoof, TAir, TOut, Cw, vWind):
    a = Cd / AFlr
    b = pow(URoof * USide * ARoof * ASide, 2) / (pow(URoof * ARoof, 2) + pow(USide * ASide, 2) + epxilon)
    TMean_Air = (TAir + TOut) / 2
    c = 2 * g * hSideRoof * (TAir - TOut) / TMean_Air
    _d = (URoof * ARoof + USide * ASide) / 2
    d = pow(_d, 2) * Cw * pow(vWind, 2)
    return a * sqrt(b * c + d)


def ppfVentSide(Cd, USide, ASide, vWind, AFlr, Cw):
    return Cd * USide * ASide * vWind * sqrt(Cw) / (2 * AFlr)


def f_VentSide(n_InsScr, ppf_VentSide, f_leakage, UThScr, f_VentRoofSide, nSide, nSide_Thr):
    if nSide >= nSide_Thr:
        return n_InsScr * ppf_VentSide + 0.5 * f_leakage
    else:
        return n_InsScr * (UThScr * ppf_VentSide + (1 - UThScr) * f_VentRoofSide * nSide) + 0.5 * f_leakage


def f_VentForced(n_InsScr, U_VentForced, phi_VentForced, A_Flr):
    return n_InsScr * U_VentForced * phi_VentForced / A_Flr


def ppfVentRoof(Cd, URoof, ARoof, AFlr, g, hVent, TAir, TOut, Cw, vWind):
    TMeanAir = (TAir + TOut) / 2
    part1 = Cd * URoof * ARoof / (2 * AFlr)
    part2 = g * hVent * (TAir - TOut) / 2 / TMeanAir + Cw * pow(vWind, 2)
    return part1 * sqrt(part2)


def fVentRoof(n_InsScr, f_leakage, UThScr, ppf_VentRoofSide, nRoof, nSide, nRoof_Thr, ppf_VentRoof):
    if nRoof >= nRoof_Thr:
        return n_InsScr * ppf_VentRoof + 0.5 * f_leakage
    else:
        return n_InsScr * (UThScr * ppf_VentRoof + (1 - UThScr) * ppf_VentRoofSide * nSide) + 0.5 * f_leakage


# -----------MV_AirTop-----------

def MV_AirTop(M_Water, R, f_Th_Scr, VP_Air, VP_Top, T_Air, T_Top):
    return M_Water * f_Th_Scr * (VP_Air / T_Air - VP_Top / T_Top) / R


# -----------MV_AirOut----------

def MV_AirOut(M_Water, R, VP_Air, VP_Out, T_Air, T_Out, f_vent_Side, f_vent_Forced):
    return M_Water * (f_vent_Forced + f_vent_Side) * (VP_Air / T_Air - VP_Out / T_Out) / R


# -----------MV_TopOut----------

def MV_TopOut(M_Water, R, VP_Top, VP_Out, T_Top, T_Out, f_vent_roof):
    return M_Water * f_vent_roof * (VP_Top / T_Top - VP_Out / T_Out) / R


# -----------MV_CanAir----------

def VEC_CanAir(p_Air, c_p_Air, LAI, Delta_H, y, r_b, r_s):
    return (2 * p_Air * c_p_Air * LAI) / (Delta_H * y * (r_s + r_b))


def MV_CanAir(VEC_CanAir, VP_Can, VP_Air):
    return VEC_CanAir * (VP_Can - VP_Air)


# -----------result_dx----------

def dx(VP_Air, VP_Top):
    # MV_BlowAir
    mv_blow_air = MV_BlowAir(N_HEAT_VAP, U_BLOW, P_BLOW, A_FLR)

    # MV_FogAir
    mv_fog_air = MV_FogAir(U_FOG, O_FOG, A_FLR)

    # MV_PadAir
    mv_pad_air = MV_PadAir(U_PAD, O_PAD, P_AIR, N_PAD, X_PAD, X_OUT, A_FLR)

    # MV_AirOut_Pad
    mv_airout_pad = MV_AirOut_Pad(U_PAD, O_PAD, A_FLR, M_WATER, R, VP_Air, T_AIR)

    # MV_Air_ThScr
    hec_air_thscr = HEC_Air_ThScr(U_THSCR, T_THSCR, T_AIR)
    mv_air_thscr = MV_Air_ThScr(S_MV_12, VP_Air, VP_THSCR, hec_air_thscr)

    # MV_Top_Cov_in
    hec_top_cov_in = HEC_Top_Cov_in(C_HEC_IN, T_TOP, T_COV_IN, A_COV, A_FLR)
    mv_top_cov_in = MV_Top_Cov_in(S_MV_12, VP_Top, VP_COV_IN, hec_top_cov_in)

    # MV_AirMech
    hec_air_mech = HEC_AirMech(U_MECH_COOL, COP_MECHCOOL, P_MECHCOOL, A_FLR, T_AIR, T_MECH, DELTA_H, VP_Air, VP_MECH)
    mv_air_mech = MV_Air_Mech(S_MV_12, VP_MECH, VP_Air, hec_air_mech)

    # MV_CanAir
    vec_can_air = VEC_CanAir(P_AIR, CP_AIR, LAI, DELTA_H, Y, R_B, R_S)
    mv_can_air = MV_CanAir(vec_can_air, VP_CAN, VP_Air)

    # f-Formula
    n_ins_scr = nInsScr(S_INS_SCR)
    f_th_scr = f_ThScr(U_THSCR, K_THSCR, T_AIR, T_TOP, G, P_AIR, P_TOP)
    f_leakage = fleakage(C_LEAKAGE, V_WIND)
    f_vent_roof_side = f_Vent_Roof_Side(CD, A_FLR, U_ROOF, U_SIDE, A_ROOF, A_SIDE, G, H_SIDE_ROOF, T_AIR, T_OUT, CW,
                                        V_WIND)
    ppf_vent_side = ppfVentSide(CD, U_SIDE, A_SIDE, V_WIND, A_FLR, CW)
    f_vent_side = f_VentSide(n_ins_scr, ppf_vent_side, f_leakage, U_THSCR, f_vent_roof_side, N_SIDE, N_SIDE_TH)
    f_vent_forced = f_VentForced(n_ins_scr, U_VENTFORCED, O_VENTFORCED, A_FLR)
    ppf_vent_roof = ppfVentRoof(CD, U_ROOF, A_ROOF, A_FLR, G, H_VENT, T_AIR, T_OUT, CW, V_WIND)
    f_vent_roof = fVentRoof(n_ins_scr, f_leakage, U_THSCR, f_vent_roof_side, N_ROOF, N_SIDE, N_ROOF_TH, ppf_vent_roof)

    # MV_AirTop
    mv_air_top = MV_AirTop(M_WATER, R, f_th_scr, VP_Air, VP_Top, T_AIR, T_TOP)

    # MV_AirOut
    mv_air_out = MV_AirOut(M_WATER, R, VP_Air, VP_OUT, T_AIR, T_OUT, f_vent_side, f_vent_forced)

    # MV_TopOut
    mv_top_out = MV_TopOut(M_WATER, R, VP_Top, VP_OUT, T_TOP, T_OUT, f_vent_roof)

    # dx
    cap_VP_air = Cap_VP_Air(M_WATER, H_AIR, R, T_AIR)
    cap_VP_top = Cap_VP_Top(M_WATER, H_TOP, R, T_TOP)
    dx_VP_air = (mv_can_air + mv_pad_air + mv_fog_air + mv_blow_air - mv_air_mech - mv_air_thscr
                 - mv_air_out - mv_air_top - mv_airout_pad) / cap_VP_air
    dx_VP_top = (mv_air_top - mv_top_cov_in - mv_top_out) / cap_VP_top
    return dx_VP_air, dx_VP_top



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
            #U_ROOF = float(df.at[i, "Uroof"])
            #U_TH_SCR = float(df.at[i, "UThScr"])
            i += 1
        t[k + 1] = t[k] + h
        f[k + 1, 0] = f[k, 0] + h * dx(f[k, 0], f[k, 1])[0]
        f[k + 1, 1] = f[k, 1] + h * dx(f[k, 0], f[k, 1])[1]
    return f, t


# --------------Runge_Kutta-----------------

def rk4(dx, init_vp_air, init_vp_top, t0, h):
    number_of_steps = N
    t = np.zeros(number_of_steps + 1)
    f = np.zeros((number_of_steps + 1, 2))
    t[0] = t0
    f[0, 0] = init_vp_air
    f[0, 1] = init_vp_top
    data = pd.read_excel("dataset.xlsx")
    df = pd.DataFrame(data)
    i = 0
    for k in range(number_of_steps):
        t[k + 1] = t[k] + h
        if (k % 300) == 0:
            global T_AIR, T_OUT, T_TOP, V_WIND, U_ROOF, U_TH_SCR
            T_AIR = float(df.at[i, "Tair"])
            T_OUT = float(df.at[i, "Tout"])
            T_TOP = float(df.at[i, "Ttop"])
            V_WIND = float(df.at[i, "Vwind"])
            U_ROOF = U_TH_SCR = 0.3
            #U_ROOF = float(df.at[i, "Uroof"])
            #U_TH_SCR = float(df.at[i, "UThScr"])
            i += 1
        k1_0 = dx(f[k, 0], f[k, 1])[0]
        k1_1 = dx(f[k, 0], f[k, 1])[1]
        k2_0 = dx(f[k, 0] + 0.5 * h * k1_0, f[k, 1] + 0.5 * h * k1_0)[0]
        k2_1 = dx(f[k, 0] + 0.5 * h * k1_1, f[k, 1] + 0.5 * h * k1_1)[1]
        k3_0 = dx(f[k, 0] + 0.5 * h * k2_0, f[k, 1] + 0.5 * h * k2_0)[0]
        k3_1 = dx(f[k, 0] + 0.5 * h * k2_1, f[k, 1] + 0.5 * h * k2_1)[1]
        k4_0 = dx(f[k, 0] + h * k3_0, f[k, 1] + h * k3_0)[0]
        k4_1 = dx(f[k, 0] + h * k3_1, f[k, 1] + h * k3_1)[1]
        f[k + 1, 0] = f[k, 0] + (1.0 / 6.0) * h * (k1_0 + 2 * (k2_0 + k3_0) + k4_0)
        f[k + 1, 1] = f[k, 1] + (1.0 / 6.0) * h * (k1_1 + 2 * (k2_1 + k3_1) + k4_1)
    return f, t


if __name__ == "__main__":
    init_vp_air = 2287.2592
    init_vp_top = 998.7252
    t0 = 0
    h = 1
    f, t = euler(dx, init_vp_air, init_vp_top, t0, h)
    u, time = rk4(dx, init_vp_air, init_vp_top, t0, h)
    plt.plot(t, f[:, 0], label="vp_air")
    data = pd.read_excel("dataset.xlsx")
    df = pd.DataFrame(data)
    real = np.zeros(N + 1)
    i = -1
    for k in range(N + 1):
        if k % 300 == 0:
            i += 1
        real[k] = float(df.at[i, "VPair(real data)"])
    plt.plot(t, real, label="Real")
    plt.xlabel("Time")
    plt.ylabel("VP concentration")
    plt.show()
    workbook = xlsxwriter.Workbook('result_euler.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Time')
    worksheet.write('B1', 'VP_Air')
    worksheet.write('C1', 'VP_Top')
    worksheet.write('D1', 'VP_Air(actual)')
    i = 0
    for count in range(0, 7200, 300):
        worksheet.write(i + 1, 0, count)
        worksheet.write(i + 1, 1, f[count][0])
        worksheet.write(i + 1, 2, f[count][1])
        worksheet.write(i + 1, 3, real[count])
        i += 1
    workbook.close()
    workbook = xlsxwriter.Workbook('result_rk4.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Time')
    worksheet.write('B1', 'VP_Air')
    worksheet.write('C1', 'VP_Top')
    worksheet.write('D1', 'VP_Air(actual)')
    i = 0
    for count in range(0, 7200, 300):
        worksheet.write(i + 1, 0, count)
        worksheet.write(i + 1, 1, u[count][0])
        worksheet.write(i + 1, 2, u[count][1])
        worksheet.write(i + 1, 3, real[count])
        i += 1
    workbook.close()
