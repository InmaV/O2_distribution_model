import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from scipy.ndimage import uniform_filter1d
from scipy.signal import argrelextrema

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def compute_timings(Tc,tFinal,m):
    n_cycles = 1
    idx_t = m.t > tFinal - n_cycles*Tc
    t = m.t[idx_t]
    
    Q_ao_valve = m.getVariable('LV', 'Qo')[idx_t]
    Q_mi_valve = m.getVariable('LA', 'Qo')[idx_t]  


    Ao = np.where(Q_ao_valve>0)[0]
    Mi = np.where(Q_mi_valve>0)[0] 

    t_Ao = (t[Ao[-1]] - t[Ao[0]])/Tc*100
    t_Mi = (t[Mi[-1]] - t[Mi[0]])/Tc*100
    t_ir = (t[Mi[0]] - t[Ao[-1]])/Tc*100
    t_ic = 100-t_Ao-t_Mi-t_ir

    print('Aortic valve: ' + str(np.round(t_Ao,2)) + '% Tc')
    print('Mitral valve: ' + str(np.round(t_Mi,2)) + '% Tc') 
    print('Isovolumetric relaxation: ' + str(np.round(t_ir,2)) + '% Tc') 
    print('Isovolumetric contraction: ' + str(np.round(t_ic,2)) + '% Tc')  

def plot_1(m, index, n_cycles, Tc, tFinal, color, xlabel, ylabel, component, name, label, linestyle):
    idx_t = m.t > tFinal - n_cycles*Tc
    t = m.t[idx_t]
    plt.plot(t, m.getVariable(component, name)[idx_t], label=label, linestyle=linestyle, color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if index == 0:
        plt.legend(loc = 'upper right')
    plt.grid()
    
def plot_2(m, index, n_cycles, Tc, tFinal, color, xlabel, ylabel, component_1, name_1, label_1, linestyle_1, component_2, name_2, label_2, linestyle_2):
    idx_t = m.t > tFinal - n_cycles*Tc
    t = m.t[idx_t]
    plt.plot(t, m.getVariable(component_1, name_1)[idx_t], label=label_1, linestyle=linestyle_1, color=color)
    plt.plot(t, m.getVariable(component_2, name_2)[idx_t], label=label_2, linestyle=linestyle_2, color=color)    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if index == 0:
        plt.legend(loc = 'upper right')
    plt.grid()

def rmse(predictions, targets):
    differences = (predictions - targets)/np.mean(targets)       
    differences_squared = differences ** 2   
    mean_of_differences_squared = differences_squared.mean() 
    rmse_val = np.sqrt(mean_of_differences_squared)
    return rmse_val 

def rmse2(predictions, targets, weights):    
    error_array = np.zeros(len(targets))    
    for index in range(len(targets)):
        error_array[index] = rmse(predictions[index], targets[index])    
    # print('minV_LV, maxV_LV, minP_LV, maxP_LV, maxv_LV, Ev_LA, Av_LA, tEA_LA, minP_LA, maxP_LA, Ev_RA, Av_RA: ')
    # print(str(np.round(error_array,2)))
    rmse_val = np.sum(error_array * weights)    
    return rmse_val 

def resistance(viscosity,length_v,radius_v):
    R = 8*viscosity*length_v/(np.pi*radius_v**4)*0.0000000075/0.00001
    return R

def resistanceK(viscosity,length_v,radius_v):
    R = 8*viscosity*length_v/(np.pi*radius_v**4)*0.0000000075/0.00001
    return R

def capacitor(elasticity,thickness,radius_v,length_v):
    C = (3*np.pi*length_v*radius_v**3)/(2*elasticity*thickness)*133000000/100000
    return C
    
def inductance(density,length_v,radius_v):
    L = density*length_v/(np.pi*radius_v**2)*0.0000000075/0.00001
    return L

def scaling_param_weight(weight,ref_param, b):
    parameter = ref_param*(weight/2720)**b # now GA = 36 weeks, weight = 3025 grams for GA = 38 weeks
    return parameter

def scale_parameters_weight(m, weight, Tc):
    # escala les variables del model amb un paràmetre "b"
    b_R = -1; b_L = -0.33; b_C = 1.33; b_K = -1.33; b_d = 0.33; b_A = 0.67; b_V = 1; b_s = 0.1; b_V0 = 1.05; # cómo escala el estrés?

    Lscini = 2.
    C0 = 0.0
    Crest = 0.02
    Lsref = 2.
    kS_v = 3.
    p_trise_v = 0.13
    p_td_v = 0.08
    vmax_v = 7.
    p_tact_v = 0.26
    kS_a = 2.25
    p_trise_a = 0.18
    p_td_a = 0.16
    vmax_a = 10.5        
    p_tact_a = 0.10
    B_param = 3.975e-4
    m.setConstantOrState0('Parameters', 'p_tact_v', 0.10*0.85 + 0.45*Tc)
    m.setConstantOrState0('Parameters', 'delay_lv', 0.375*Tc/0.43) # no estoy segura del escalado de los delays, no estoy segura de que deba ser proporcional a Tc
    m.setConstantOrState0('Parameters', 'delay_rv', 0.375*Tc/0.43)
    m.setConstantOrState0('Parameters', 'p_tact_a', 0.1*Tc/0.43)
    m.setConstantOrState0('Parameters', 'delay_la', 0.325*Tc/0.43)
    m.setConstantOrState0('Parameters', 'delay_ra', 0.325*Tc/0.43)
    m.setConstantOrState0('LV', 'Vcav', scaling_param_weight(weight, 29.47, b_V0))
    m.setConstantOrState0('RV', 'Vcav', scaling_param_weight(weight, 29.47, b_V0))
    m.setConstantOrState0('LA', 'Vcav', scaling_param_weight(weight, 29.47, b_V0))
    m.setConstantOrState0('RA', 'Vcav', scaling_param_weight(weight, 29.47, b_V0))
    #m.setConstantOrState0('Parameters', 'spas_v', scaling_param_weight(weight, 18.4, b_s))
    #m.setConstantOrState0('Parameters', 'sact_v', scaling_param_weight(weight, 246, b_s))
    #m.setConstantOrState0('Parameters', 'spas_a', scaling_param_weight(weight, 45, b_s))
    #m.setConstantOrState0('Parameters', 'sact_a', scaling_param_weight(weight, 110, b_s))
    m.setConstantOrState0('Parameters', 'Vwall_lv', scaling_param_weight(weight, 8.9973, b_V))
    m.setConstantOrState0('Parameters', 'Amref_lv', scaling_param_weight(weight, 22.7025, b_A))
    m.setConstantOrState0('Parameters', 'Amdead_lv', scaling_param_weight(weight, 4.5983, b_A))
    m.setConstantOrState0('Parameters', 'Vwall_rv', scaling_param_weight(weight, 8.9973, b_V))
    m.setConstantOrState0('Parameters', 'Amref_rv', scaling_param_weight(weight, 22.7025, b_A))
    m.setConstantOrState0('Parameters', 'Amdead_rv', scaling_param_weight(weight, 4.5983, b_A))
    m.setConstantOrState0('Parameters', 'Vwall_la', scaling_param_weight(weight, 1.7573, b_V))
    m.setConstantOrState0('Parameters', 'Amref_la', scaling_param_weight(weight, 10.1137, b_A))
    m.setConstantOrState0('Parameters', 'Amdead_la', scaling_param_weight(weight, 4.5983, b_A))
    m.setConstantOrState0('Parameters', 'Vwall_ra', scaling_param_weight(weight, 1.7573, b_V))
    m.setConstantOrState0('Parameters', 'Amref_ra', scaling_param_weight(weight, 10.1137, b_A))
    m.setConstantOrState0('Parameters', 'Amdead_ra', scaling_param_weight(weight, 4.5983, b_A))
    m.setConstantOrState0('Parameters', 'L_param', scaling_param_weight(weight, 0.00034289, 0.33))
    m.setConstantOrState0('Parameters', 'Aao', scaling_param_weight(weight, 0.410, 0.9))
    m.setConstantOrState0('Parameters', 'Ami', scaling_param_weight(weight, 0.553, 0.9))
    m.setConstantOrState0('Parameters', 'Apv', scaling_param_weight(weight, 0.493, 0.9))
    m.setConstantOrState0('Parameters', 'Atr', scaling_param_weight(weight, 0.596, 0.9))
    m.setConstantOrState0('Parameters', 'Afo', scaling_param_weight(weight, 0.471, 0.4))
    m.setConstantOrState0('Parameters', 'Adv', scaling_param_weight(weight, 0.0157, 0.9))
    m.setConstantOrState0('Parameters', 'Rdtao', scaling_param_weight(weight, 0.04887, b_R))
    m.setConstantOrState0('Parameters', 'Rdaao', scaling_param_weight(weight, 0.06807, b_R))
    m.setConstantOrState0('Parameters', 'Rpa', scaling_param_weight(weight, 0.00448, b_R))
    m.setConstantOrState0('Parameters', 'Rlung', scaling_param_weight(weight, 9.7, b_R))
    m.setConstantOrState0('Parameters', 'Rda', scaling_param_weight(weight, 0.02766, b_R))
    m.setConstantOrState0('Parameters', 'Relg', scaling_param_weight(weight, 91.8888, b_R))
    m.setConstantOrState0('Parameters', 'Rmea', scaling_param_weight(weight, 38.572, b_R))
    m.setConstantOrState0('Parameters', 'Rporv', scaling_param_weight(weight, 7.94122, b_R))
    m.setConstantOrState0('Parameters', 'Rrea', scaling_param_weight(weight, 19.853, b_R))
    m.setConstantOrState0('Parameters', 'Rrev', scaling_param_weight(weight, 15.88, b_R))
    m.setConstantOrState0('Parameters', 'Rua', scaling_param_weight(weight, 1.5274, b_R))
    m.setConstantOrState0('Parameters', 'Rplac', scaling_param_weight(weight, 2.67, b_R))
    m.setConstantOrState0('Parameters', 'Rplac_prox', scaling_param_weight(weight, 2, b_R))
    m.setConstantOrState0('Parameters', 'Ruv', scaling_param_weight(weight, 0.2803, b_R))
    m.setConstantOrState0('Parameters', 'Rfa', scaling_param_weight(weight, 10.5, b_R))
    m.setConstantOrState0('Parameters', 'Rfv', scaling_param_weight(weight, 0.68074, b_R))
    m.setConstantOrState0('Parameters', 'Rha', scaling_param_weight(weight, 0.25, b_R))
    m.setConstantOrState0('Parameters', 'Rhv', scaling_param_weight(weight, 0.16005, b_R))
    m.setConstantOrState0('Parameters', 'Rdv_fo', scaling_param_weight(weight, 1.5522, b_R))
    m.setConstantOrState0('Parameters', 'Rdv_ra', scaling_param_weight(weight, 29.492, b_R))
    m.setConstantOrState0('Parameters', 'Rsvc', scaling_param_weight(weight, 0.2276, b_R))
    m.setConstantOrState0('Parameters', 'Rivc', scaling_param_weight(weight, 0.00171, b_R))
    m.setConstantOrState0('Parameters', 'Rivc_ra', scaling_param_weight(weight, 0.38857, b_R))
    m.setConstantOrState0('Parameters', 'Rivc_la', scaling_param_weight(weight, 0.20923, b_R))
    m.setConstantOrState0('Parameters', 'Rla', scaling_param_weight(weight, 2.2691, b_R)) 
    m.setConstantOrState0('Parameters', 'Kfo', scaling_param_weight(weight, 0.21, -0.1))
    m.setConstantOrState0('Parameters', 'Kdv_fo', scaling_param_weight(weight, 0.306, -0.88))
    m.setConstantOrState0('Parameters', 'Kdv_ra', scaling_param_weight(weight, 5.81, -0.88))
    #m.setConstantOrState0('Parameters', 'Lda', scaling_param_weight(weight, 0.0000894, b_L))
    #m.setConstantOrState0('Parameters', 'Lpa', scaling_param_weight(weight, 0.00243, b_L))
    m.setConstantOrState0('Parameters', 'Cua', scaling_param_weight(weight, 0.00917, b_C))
    m.setConstantOrState0('Parameters', 'Cao1', scaling_param_weight(weight, 0.07, b_C))
    m.setConstantOrState0('Parameters', 'Cao2', scaling_param_weight(weight, 0.08456, b_C))
    m.setConstantOrState0('Parameters', 'Cpa', scaling_param_weight(weight, 0.08455, b_C))
    m.setConstantOrState0('Parameters', 'Clung', scaling_param_weight(weight, 0.33821, b_C))
    m.setConstantOrState0('Parameters', 'Cinte', scaling_param_weight(weight, 0.21138, b_C))
    m.setConstantOrState0('Parameters', 'Ckid', scaling_param_weight(weight, 0.01691, b_C))
    m.setConstantOrState0('Parameters', 'Che', scaling_param_weight(weight, 2.53659, b_C))
    m.setConstantOrState0('Parameters', 'Cplac', scaling_param_weight(weight, 1.2683, b_C))
    m.setConstantOrState0('Parameters', 'Cleg', scaling_param_weight(weight, 3.38212, b_C))
    m.setConstantOrState0('Parameters', 'Cuv', scaling_param_weight(weight, 0.25366, b_C))
    m.setConstantOrState0('Parameters', 'Csvc', scaling_param_weight(weight, 0.8455, b_C))
    m.setConstantOrState0('Parameters', 'Civc', scaling_param_weight(weight, 0.50732, b_C))
    m.setConstantOrState0('Parameters', 'Risthm', scaling_param_weight(weight, 0.00782, b_R))
    m.setConstantOrState0('Parameters', 'Raa', scaling_param_weight(weight, 0.00733, b_R))
    m.setConstantOrState0('Parameters', 'RaAoA', scaling_param_weight(weight, 0.0059, b_R))
    m.setConstantOrState0('Parameters', 'RdAoA', scaling_param_weight(weight, 0.00832, b_R))
    m.setConstantOrState0('Parameters', 'Rbct', scaling_param_weight(weight, 0.02529, b_R))
    m.setConstantOrState0('Parameters', 'R_L_CCA', scaling_param_weight(weight, 0.3706, b_R))
    m.setConstantOrState0('Parameters', 'R_L_ICA', scaling_param_weight(weight, 0.6324, b_R))
    m.setConstantOrState0('Parameters', 'R_L_SC', scaling_param_weight(weight, 0.16147, b_R))
    m.setConstantOrState0('Parameters', 'R_L_ub', scaling_param_weight(weight, 48, b_R))
    m.setConstantOrState0('Parameters', 'R_L_br', scaling_param_weight(weight, 15.5, b_R))
    m.setConstantOrState0('Parameters', 'R_L_ub_p', scaling_param_weight(weight, 18, b_R))
    m.setConstantOrState0('Parameters', 'R_L_br_p', scaling_param_weight(weight, 1, b_R))
    m.setConstantOrState0('Parameters', 'R_R_CCA', scaling_param_weight(weight, 0.259, b_R))
    m.setConstantOrState0('Parameters', 'R_R_ICA', scaling_param_weight(weight, 0.6324, b_R))
    m.setConstantOrState0('Parameters', 'R_R_SC', scaling_param_weight(weight, 0.16147, b_R))
    m.setConstantOrState0('Parameters', 'R_R_ub', scaling_param_weight(weight, 48, b_R))
    m.setConstantOrState0('Parameters', 'R_R_br', scaling_param_weight(weight, 15.5, b_R))
    m.setConstantOrState0('Parameters', 'R_R_ub_p', scaling_param_weight(weight, 18, b_R))
    m.setConstantOrState0('Parameters', 'R_R_br_p', scaling_param_weight(weight, 1, b_R))
    m.setConstantOrState0('Parameters', 'R0_Coronary', scaling_param_weight(weight, 48, b_R))
    m.setConstantOrState0('Parameters', 'k_Coronary', scaling_param_weight(weight, 10, b_R))
    m.setConstantOrState0('Parameters', 'Ps_Coronary', scaling_param_weight(weight, 25, b_s))
    #m.setConstantOrState0('Parameters', 'Listhm', scaling_param_weight(weight, 0.0000104, b_L))
    #m.setConstantOrState0('Parameters', 'Laa', scaling_param_weight(weight, 0.0000521, b_L))
    #m.setConstantOrState0('Parameters', 'LaAoA', scaling_param_weight(weight, 0.0000209, b_L))
    #m.setConstantOrState0('Parameters', 'LdAoA', scaling_param_weight(weight, 0.000028, b_L))
    #m.setConstantOrState0('Parameters', 'Lbct', scaling_param_weight(weight, 0.0000411, b_L))
    #m.setConstantOrState0('Parameters', 'Ldv', scaling_param_weight(weight, 0.00005, b_L))
    #m.setConstantOrState0('Parameters', 'L_L_CCA', scaling_param_weight(weight, 0.0003575, b_L))
    #m.setConstantOrState0('Parameters', 'L_L_ICA', scaling_param_weight(weight, 0.000469, b_L))
    #m.setConstantOrState0('Parameters', 'L_L_SC', scaling_param_weight(weight, 0.000125, b_L))
    #m.setConstantOrState0('Parameters', 'L_R_CCA', scaling_param_weight(weight, 0.0003003, b_L))
    #m.setConstantOrState0('Parameters', 'L_R_CCO', scaling_param_weight(weight, 0.0003003, b_L))
    #m.setConstantOrState0('Parameters', 'L_R_ICA', scaling_param_weight(weight, 0.000469, b_L))
    #m.setConstantOrState0('Parameters', 'L_R_SC', scaling_param_weight(weight, 0.000125, b_L))
    m.setConstantOrState0('Parameters', 'Cisthm', scaling_param_weight(weight, 0.001504, b_C))
    m.setConstantOrState0('Parameters', 'Caa', scaling_param_weight(weight, 0.0708, b_C))
    m.setConstantOrState0('Parameters', 'CaAoA', scaling_param_weight(weight, 0.00209, b_C))
    m.setConstantOrState0('Parameters', 'CdAoA', scaling_param_weight(weight, 0.00176, b_C))
    m.setConstantOrState0('Parameters', 'Cbct', scaling_param_weight(weight, 0.001907, b_C))
    m.setConstantOrState0('Parameters', 'C_L_CCA', scaling_param_weight(weight, 0.00374, b_C))
    m.setConstantOrState0('Parameters', 'C_L_ICA', scaling_param_weight(weight, 0.001015, b_C))
    m.setConstantOrState0('Parameters', 'C_L_SC', scaling_param_weight(weight, 0.000844, b_C))
    m.setConstantOrState0('Parameters', 'C_L_ub', scaling_param_weight(weight, 0.07187, b_C))
    m.setConstantOrState0('Parameters', 'C_L_br', scaling_param_weight(weight, 0.0169884, b_C))
    m.setConstantOrState0('Parameters', 'C_R_CCA', scaling_param_weight(weight, 0.00262, b_C))
    m.setConstantOrState0('Parameters', 'C_R_ICA', scaling_param_weight(weight, 0.001015, b_C))
    m.setConstantOrState0('Parameters', 'C_R_SC', scaling_param_weight(weight, 0.000844, b_C))
    m.setConstantOrState0('Parameters', 'C_R_ub', scaling_param_weight(weight, 0.22998, b_C))
    m.setConstantOrState0('Parameters', 'C_R_br', scaling_param_weight(weight, 0.0169884, b_C))

    GA = np.power(weight/0.02594,1/3.226) 
    Es = 3.8E2*GA**2 + 4.7E3*GA + 1.5E4
    Es28 = 3.8E2*28**2 + 4.7E3*28 + 1.5E4
    viscosity =(1.15+0.075*GA)/100
    density = 1.05

    length_bct = 0.1*(-1.056+0.29*GA)
    radius_bct = (3.7632*np.log(0.0877*GA) - 1.0454)/20
    elasticity_bct = 9.0E5*Es/Es28

    length_lsca = 0.1*(-2.1482+0.4302*GA)
    radius_lsca = (2.6359*np.log(0.0920*GA) - 0.6678)/20
    elasticity_lsca = 13.5E5*Es/Es28

    length_rsca =  0.1*(-2.1482+0.4302*GA)
    radius_rsca = (2.6359*np.log(0.0920*GA) - 0.6678)/20
    elasticity_rsca = 13.5E5*Es/Es28

    length_lcca = 0.1*(-9.6918+1.5963*GA)
    radius_lcca = (1.8541*np.log(0.1182*GA) - 0.5645)/20
    elasticity_lcca = 13.5E5*Es/Es28

    length_ist = (1/3)*0.1*(-6.079 + 0.6370*GA)
    radius_ist = (4.2430*np.log(0.0702*GA) + 0.2784)/20
    elasticity_ist = 7.5E5*Es/Es28

    length_dAoA = (1/3)*0.1*(-6.079 + 0.6370*GA)
    radius_dAoA = (4.4126*np.log(0.1304*GA) - 1.8989)/20
    elasticity_dAoA = 7.5E5*Es/Es28

    length_aAoA = (1/3)*0.1*(-6.079 + 0.6370*GA)
    radius_aAoA = (3.9115*np.log(0.1974*GA) - 2.8041)/20
    elasticity_aAoA = 7.5E5*Es/Es28

    length_aAo = 0.1*(-4.678 + 0.4647*GA)
    radius_aAo = (5.4873*np.log(0.1583*GA) - 3.2911)/20
    elasticity_aAo = 7.5E5*Es/Es28

    length_tAo = 0.1*(-19.654+2.0512*GA)
    radius_tAo = (6.1507*np.log(0.0654*GA) + 0.4682)/20
    elasticity_tAo = 9.0E5*Es/Es28

    length_duct = 0.1*(-3.0726+0.4381*GA) 
    kduct = 0.0028*GA + 0.798
    radius_duct = (5.3851*np.log(17.1555*GA) - 29.9470)/20
    elasticity_duct = 13.5E5*Es/Es28
    k_DA=0.009 

    length_pA = 0.1*(-5.6035+0.5705*GA)
    radius_pA = (8.8763*np.log(0.1454*GA) - 6.4004)/20
    elasticity_pA = 7.5E5*Es/Es28

    m.setConstantOrState0('Parameters', 'Rbct', resistance(viscosity,length_bct,radius_bct))
    m.setConstantOrState0('Parameters', 'Cbct', capacitor(elasticity_bct,0.12*radius_bct,radius_bct,length_bct))
    m.setConstantOrState0('Parameters', 'R_L_SC', resistance(viscosity,length_lsca,radius_lsca))
    m.setConstantOrState0('Parameters', 'C_L_SC', capacitor(elasticity_lsca,0.09*radius_lsca,radius_lsca,length_lsca))
    m.setConstantOrState0('Parameters', 'R_R_SC', resistance(viscosity,length_rsca,radius_rsca))
    m.setConstantOrState0('Parameters', 'C_R_SC', capacitor(elasticity_rsca,0.09*radius_rsca,radius_rsca,length_rsca))
    m.setConstantOrState0('Parameters', 'R_L_CCA', resistance(viscosity,length_lcca,radius_lcca)*0.13)
    m.setConstantOrState0('Parameters', 'C_L_CCA', capacitor(elasticity_lcca,0.1*radius_lcca,radius_lcca,length_lcca))              
    m.setConstantOrState0('Parameters', 'R_R_CCA', resistance(viscosity,length_lcca,radius_lcca)*0.11)
    m.setConstantOrState0('Parameters', 'C_R_CCA', capacitor(elasticity_lcca,0.1*radius_lcca,radius_lcca,length_lcca))            
    m.setConstantOrState0('Parameters', 'Risthm', resistance(viscosity,length_ist,radius_ist))
    m.setConstantOrState0('Parameters', 'Cisthm', capacitor(elasticity_ist,0.06*radius_ist,radius_ist,length_ist))
    m.setConstantOrState0('Parameters', 'RdAoA', resistance(viscosity,length_dAoA,radius_dAoA))
    m.setConstantOrState0('Parameters', 'CdAoA', capacitor(elasticity_dAoA,0.06*radius_dAoA,radius_dAoA,length_dAoA))
    m.setConstantOrState0('Parameters', 'RaAoA', resistance(viscosity,length_aAoA,radius_aAoA))
    m.setConstantOrState0('Parameters', 'CaAoA', capacitor(elasticity_aAoA,0.06*radius_aAoA,radius_aAoA,length_aAoA))
    m.setConstantOrState0('Parameters', 'Raa', resistance(viscosity,length_aAo,radius_aAo))
    m.setConstantOrState0('Parameters', 'Caa', capacitor(elasticity_aAo,0.06*radius_aAo,radius_aAo,length_aAo)*6.5)   
    m.setConstantOrState0('Parameters', 'Rdtao', resistance(viscosity,length_tAo,radius_tAo))
    m.setConstantOrState0('Parameters', 'Cao1', capacitor(elasticity_tAo,0.06*radius_tAo,radius_tAo,length_tAo))
    m.setConstantOrState0('Parameters', 'Rda', resistance(viscosity,length_duct,radius_duct))
    m.setConstantOrState0('Parameters', 'Rpa', resistance(viscosity,length_pA,radius_pA))
    m.setConstantOrState0('Parameters', 'Cpa', capacitor(elasticity_pA,0.06*radius_pA,radius_pA,length_pA)*3.4) 
    m.setConstantOrState0('Parameters', 'Lpa', inductance(density,length_pA,radius_pA))   

    m.setConstantOrState0('Parameters', 'Bisthm', 1.05*1.706e-4/(2*0.2275*(np.pi*radius_ist**2)**2))
    m.setConstantOrState0('Parameters', 'Bda', 1.05*1.706e-4/(2*0.2275*(np.pi*radius_duct**2)**2))
    m.setConstantOrState0('Parameters', 'Bmpa', 1.05*1.706e-4/(2*0.2275*(np.pi*radius_pA**2)**2))
    m.setConstantOrState0('Parameters', 'BdAoA', 1.05*1.706e-4/(2*0.2275*(np.pi*radius_dAoA**2)**2))

def scale_parameters_weight_2(m, weight, Tc):
    # escala les variables del model amb un paràmetre "b"
    b_R = -1; b_L = -0.33; b_C = 1.33; b_K = -1.33; b_d = 0.33; b_A = 0.67; b_V = 1; b_s = 0.1; b_V0 = 1.05; # cómo escala el estrés?

    Lscini = 2.
    C0 = 0.0
    Crest = 0.02
    Lsref = 2.
    kS_v = 3.
    p_trise_v = 0.13
    p_td_v = 0.08
    vmax_v = 7.
    p_tact_v = 0.26
    kS_a = 2.25
    p_trise_a = 0.18
    p_td_a = 0.16
    vmax_a = 10.5        
    p_tact_a = 0.10
    B_param = 3.975e-4
    m.setConstantOrState0('Parameters', 'p_tact_v', 0.10*0.85 + 0.45*Tc)
    m.setConstantOrState0('Parameters', 'delay_lv', 0.375*Tc/0.43) # no estoy segura del escalado de los delays, no estoy segura de que deba ser proporcional a Tc
    m.setConstantOrState0('Parameters', 'delay_rv', 0.375*Tc/0.43)
    m.setConstantOrState0('Parameters', 'p_tact_a', 0.1*Tc/0.43)
    m.setConstantOrState0('Parameters', 'delay_la', 0.325*Tc/0.43)
    m.setConstantOrState0('Parameters', 'delay_ra', 0.325*Tc/0.43)
    m.setConstantOrState0('LV', 'Vcav', scaling_param_weight(weight, 29.47, b_V0))
    m.setConstantOrState0('RV', 'Vcav', scaling_param_weight(weight, 29.47, b_V0))
    m.setConstantOrState0('LA', 'Vcav', scaling_param_weight(weight, 29.47, b_V0))
    m.setConstantOrState0('RA', 'Vcav', scaling_param_weight(weight, 29.47, b_V0))
    m.setConstantOrState0('Parameters', 'spas_v', scaling_param_weight(weight, 18.4, b_s))
    m.setConstantOrState0('Parameters', 'sact_v', scaling_param_weight(weight, 246, b_s))
    m.setConstantOrState0('Parameters', 'spas_a', scaling_param_weight(weight, 45, b_s))
    m.setConstantOrState0('Parameters', 'sact_a', scaling_param_weight(weight, 110, b_s))
    m.setConstantOrState0('Parameters', 'Vwall_lv', scaling_param_weight(weight, 8.9973, b_V))
    m.setConstantOrState0('Parameters', 'Amref_lv', scaling_param_weight(weight, 22.7025, b_A))
    m.setConstantOrState0('Parameters', 'Amdead_lv', scaling_param_weight(weight, 4.5983, b_A))
    m.setConstantOrState0('Parameters', 'Vwall_rv', scaling_param_weight(weight, 8.9973, b_V))
    m.setConstantOrState0('Parameters', 'Amref_rv', scaling_param_weight(weight, 22.7025, b_A))
    m.setConstantOrState0('Parameters', 'Amdead_rv', scaling_param_weight(weight, 4.5983, b_A))
    m.setConstantOrState0('Parameters', 'Vwall_la', scaling_param_weight(weight, 1.7573, b_V))
    m.setConstantOrState0('Parameters', 'Amref_la', scaling_param_weight(weight, 10.1137, b_A))
    m.setConstantOrState0('Parameters', 'Amdead_la', scaling_param_weight(weight, 4.5983, b_A))
    m.setConstantOrState0('Parameters', 'Vwall_ra', scaling_param_weight(weight, 1.7573, b_V))
    m.setConstantOrState0('Parameters', 'Amref_ra', scaling_param_weight(weight, 10.1137, b_A))
    m.setConstantOrState0('Parameters', 'Amdead_ra', scaling_param_weight(weight, 4.5983, b_A))
    m.setConstantOrState0('Parameters', 'L_param', scaling_param_weight(weight, 0.00034289, 0.33))
    m.setConstantOrState0('Parameters', 'Aao', scaling_param_weight(weight, 0.410, 0.9))
    m.setConstantOrState0('Parameters', 'Ami', scaling_param_weight(weight, 0.553, 0.9))
    m.setConstantOrState0('Parameters', 'Apv', scaling_param_weight(weight, 0.493, 0.9))
    m.setConstantOrState0('Parameters', 'Atr', scaling_param_weight(weight, 0.596, 0.9))
    m.setConstantOrState0('Parameters', 'Afo', scaling_param_weight(weight, 0.471, 0.275))
    m.setConstantOrState0('Parameters', 'Adv', scaling_param_weight(weight, 0.0157, 0.9))
    m.setConstantOrState0('Parameters', 'Rdtao', scaling_param_weight(weight, 0.058938170499768704, b_R))
    m.setConstantOrState0('Parameters', 'Rdaao', scaling_param_weight(weight, 0.06807, b_R))
    m.setConstantOrState0('Parameters', 'Rpa', scaling_param_weight(weight, 0.003716498473896793, b_R))
    m.setConstantOrState0('Parameters', 'Rlung', scaling_param_weight(weight, 9.7, b_R))
    m.setConstantOrState0('Parameters', 'Rda', scaling_param_weight(weight, 0.03177141196648154, b_R))
    m.setConstantOrState0('Parameters', 'Relg', scaling_param_weight(weight, 91.8888, b_R))
    m.setConstantOrState0('Parameters', 'Rmea', scaling_param_weight(weight, 38.572, b_R))
    m.setConstantOrState0('Parameters', 'Rporv', scaling_param_weight(weight, 7.94122, b_R))
    m.setConstantOrState0('Parameters', 'Rrea', scaling_param_weight(weight, 19.853, b_R))
    m.setConstantOrState0('Parameters', 'Rrev', scaling_param_weight(weight, 15.88, b_R))
    m.setConstantOrState0('Parameters', 'Rua', scaling_param_weight(weight, 1.5274, b_R))
    m.setConstantOrState0('Parameters', 'Rplac', scaling_param_weight(weight, 2.67, b_R))
    m.setConstantOrState0('Parameters', 'Rplac_prox', scaling_param_weight(weight, 2, b_R))
    m.setConstantOrState0('Parameters', 'Ruv', scaling_param_weight(weight, 0.2803, b_R))
    m.setConstantOrState0('Parameters', 'Rfa', scaling_param_weight(weight, 10.5, b_R))
    m.setConstantOrState0('Parameters', 'Rfv', scaling_param_weight(weight, 0.68074, b_R))
    m.setConstantOrState0('Parameters', 'Rha', scaling_param_weight(weight, 0.25, b_R))
    m.setConstantOrState0('Parameters', 'Rhv', scaling_param_weight(weight, 0.16005, b_R))
    m.setConstantOrState0('Parameters', 'Rdv_fo', scaling_param_weight(weight, 1.5522, b_R))
    m.setConstantOrState0('Parameters', 'Rdv_ra', scaling_param_weight(weight, 29.492, b_R))
    m.setConstantOrState0('Parameters', 'Rsvc', scaling_param_weight(weight, 0.2276, b_R))
    m.setConstantOrState0('Parameters', 'Rivc', scaling_param_weight(weight, 0.00171, b_R))
    m.setConstantOrState0('Parameters', 'Rivc_ra', scaling_param_weight(weight, 0.38857, b_R))
    m.setConstantOrState0('Parameters', 'Rivc_la', scaling_param_weight(weight, 0.20923, b_R))
    m.setConstantOrState0('Parameters', 'Rla', scaling_param_weight(weight, 2.2691, b_R)) 
    m.setConstantOrState0('Parameters', 'Kfo', scaling_param_weight(weight, 0.21, -0.1))
    m.setConstantOrState0('Parameters', 'Kdv_fo', scaling_param_weight(weight, 0.306, -0.88))
    m.setConstantOrState0('Parameters', 'Kdv_ra', scaling_param_weight(weight, 5.81, -0.88))
    #m.setConstantOrState0('Parameters', 'Lda', scaling_param_weight(weight, 0.0000894, b_L))
    m.setConstantOrState0('Parameters', 'Lpa', scaling_param_weight(weight, 0.0021778527820286433, b_L))
    m.setConstantOrState0('Parameters', 'Cua', scaling_param_weight(weight, 0.00917, b_C))
    m.setConstantOrState0('Parameters', 'Cao1', scaling_param_weight(weight, 0.03397048758684603, b_C))
    m.setConstantOrState0('Parameters', 'Cao2', scaling_param_weight(weight, 0.08456, b_C))
    m.setConstantOrState0('Parameters', 'Cpa', scaling_param_weight(weight, 0.07985645360327016, b_C))
    m.setConstantOrState0('Parameters', 'Clung', scaling_param_weight(weight, 0.33821, b_C))
    m.setConstantOrState0('Parameters', 'Cinte', scaling_param_weight(weight, 0.21138, b_C))
    m.setConstantOrState0('Parameters', 'Ckid', scaling_param_weight(weight, 0.01691, b_C))
    m.setConstantOrState0('Parameters', 'Che', scaling_param_weight(weight, 2.53659, b_C))
    m.setConstantOrState0('Parameters', 'Cplac', scaling_param_weight(weight, 1.2683, b_C))
    m.setConstantOrState0('Parameters', 'Cleg', scaling_param_weight(weight, 3.38212, b_C))
    m.setConstantOrState0('Parameters', 'Cuv', scaling_param_weight(weight, 0.25366, b_C))
    m.setConstantOrState0('Parameters', 'Csvc', scaling_param_weight(weight, 0.8455, b_C))
    m.setConstantOrState0('Parameters', 'Civc', scaling_param_weight(weight, 0.50732, b_C))
    m.setConstantOrState0('Parameters', 'Risthm', scaling_param_weight(weight, 0.02099658011150054, b_R))
    m.setConstantOrState0('Parameters', 'Raa', scaling_param_weight(weight, 0.00924331602477372, b_R))
    m.setConstantOrState0('Parameters', 'RaAoA', scaling_param_weight(weight, 0.011785331743546408, b_R))
    m.setConstantOrState0('Parameters', 'RdAoA', scaling_param_weight(weight, 0.011237376881167806, b_R))
    m.setConstantOrState0('Parameters', 'Rbct', scaling_param_weight(weight, 0.0952625695405053, b_R))
    m.setConstantOrState0('Parameters', 'R_L_CCA', scaling_param_weight(weight, 0.36140119823982575, b_R))
    m.setConstantOrState0('Parameters', 'R_L_ICA', scaling_param_weight(weight, 0.6324, b_R))
    m.setConstantOrState0('Parameters', 'R_L_SC', scaling_param_weight(weight, 0.4090252375570464, b_R))
    m.setConstantOrState0('Parameters', 'R_L_ub', scaling_param_weight(weight, 48, b_R))
    m.setConstantOrState0('Parameters', 'R_L_br', scaling_param_weight(weight, 15.5, b_R))
    m.setConstantOrState0('Parameters', 'R_L_ub_p', scaling_param_weight(weight, 18, b_R))
    m.setConstantOrState0('Parameters', 'R_L_br_p', scaling_param_weight(weight, 1, b_R))
    m.setConstantOrState0('Parameters', 'R_R_CCA', scaling_param_weight(weight, 0.3058010138952372, b_R))
    m.setConstantOrState0('Parameters', 'R_R_ICA', scaling_param_weight(weight, 0.6324, b_R))
    m.setConstantOrState0('Parameters', 'R_R_SC', scaling_param_weight(weight, 0.4090252375570464, b_R))
    m.setConstantOrState0('Parameters', 'R_R_ub', scaling_param_weight(weight, 48, b_R))
    m.setConstantOrState0('Parameters', 'R_R_br', scaling_param_weight(weight, 15.5, b_R))
    m.setConstantOrState0('Parameters', 'R_R_ub_p', scaling_param_weight(weight, 18, b_R))
    m.setConstantOrState0('Parameters', 'R_R_br_p', scaling_param_weight(weight, 1, b_R))
    m.setConstantOrState0('Parameters', 'R0_Coronary', scaling_param_weight(weight, 48, b_R))
    m.setConstantOrState0('Parameters', 'k_Coronary', scaling_param_weight(weight, 10, b_R))
    m.setConstantOrState0('Parameters', 'Ps_Coronary', scaling_param_weight(weight, 25, b_s))
    #m.setConstantOrState0('Parameters', 'Listhm', scaling_param_weight(weight, 0.0000104, b_L))
    #m.setConstantOrState0('Parameters', 'Laa', scaling_param_weight(weight, 0.0000521, b_L))
    #m.setConstantOrState0('Parameters', 'LaAoA', scaling_param_weight(weight, 0.0000209, b_L))
    #m.setConstantOrState0('Parameters', 'LdAoA', scaling_param_weight(weight, 0.000028, b_L))
    #m.setConstantOrState0('Parameters', 'Lbct', scaling_param_weight(weight, 0.0000411, b_L))
    #m.setConstantOrState0('Parameters', 'Ldv', scaling_param_weight(weight, 0.00005, b_L))
    #m.setConstantOrState0('Parameters', 'L_L_CCA', scaling_param_weight(weight, 0.0003575, b_L))
    #m.setConstantOrState0('Parameters', 'L_L_ICA', scaling_param_weight(weight, 0.000469, b_L))
    #m.setConstantOrState0('Parameters', 'L_L_SC', scaling_param_weight(weight, 0.000125, b_L))
    #m.setConstantOrState0('Parameters', 'L_R_CCA', scaling_param_weight(weight, 0.0003003, b_L))
    #m.setConstantOrState0('Parameters', 'L_R_CCO', scaling_param_weight(weight, 0.0003003, b_L))
    #m.setConstantOrState0('Parameters', 'L_R_ICA', scaling_param_weight(weight, 0.000469, b_L))
    #m.setConstantOrState0('Parameters', 'L_R_SC', scaling_param_weight(weight, 0.000125, b_L))
    m.setConstantOrState0('Parameters', 'Cisthm', scaling_param_weight(weight, 0.002279669771077823, b_C))
    m.setConstantOrState0('Parameters', 'Caa', scaling_param_weight(weight, 0.07017085191430876, b_C))
    m.setConstantOrState0('Parameters', 'CaAoA', scaling_param_weight(weight, 0.003042813371873828, b_C))
    m.setConstantOrState0('Parameters', 'CdAoA', scaling_param_weight(weight, 0.0031161169509763952, b_C))
    m.setConstantOrState0('Parameters', 'Cbct', scaling_param_weight(weight, 0.000962776951119818, b_C))
    m.setConstantOrState0('Parameters', 'C_L_CCA', scaling_param_weight(weight, 0.0016378395767641387, b_C))
    m.setConstantOrState0('Parameters', 'C_L_ICA', scaling_param_weight(weight, 0.001015, b_C))
    m.setConstantOrState0('Parameters', 'C_L_SC', scaling_param_weight(weight, 0.0006999409820848433, b_C))
    m.setConstantOrState0('Parameters', 'C_L_ub', scaling_param_weight(weight, 0.07187, b_C))
    m.setConstantOrState0('Parameters', 'C_L_br', scaling_param_weight(weight, 0.0169884, b_C))
    m.setConstantOrState0('Parameters', 'C_R_CCA', scaling_param_weight(weight, 0.0016378395767641387, b_C))
    m.setConstantOrState0('Parameters', 'C_R_ICA', scaling_param_weight(weight, 0.001015, b_C))
    m.setConstantOrState0('Parameters', 'C_R_SC', scaling_param_weight(weight, 0.0006999409820848433, b_C))
    m.setConstantOrState0('Parameters', 'C_R_ub', scaling_param_weight(weight, 0.22998, b_C))
    m.setConstantOrState0('Parameters', 'C_R_br', scaling_param_weight(weight, 0.0169884, b_C))

    GA = np.power(weight/0.02594,1/3.226) 
    Es = 3.8E2*GA**2 + 4.7E3*GA + 1.5E4
    Es28 = 3.8E2*28**2 + 4.7E3*28 + 1.5E4
    viscosity =(1.15+0.075*GA)/100
    density = 1.05

    length_bct = 0.1*(-1.056+0.29*GA)
    radius_bct = (3.7632*np.log(0.0877*GA) - 1.0454)/20
    elasticity_bct = 9.0E5*Es/Es28

    length_lsca = 0.1*(-2.1482+0.4302*GA)
    radius_lsca = (2.6359*np.log(0.0920*GA) - 0.6678)/20
    elasticity_lsca = 13.5E5*Es/Es28

    length_rsca =  0.1*(-2.1482+0.4302*GA)
    radius_rsca = (2.6359*np.log(0.0920*GA) - 0.6678)/20
    elasticity_rsca = 13.5E5*Es/Es28

    length_lcca = 0.1*(-9.6918+1.5963*GA)
    radius_lcca = (1.8541*np.log(0.1182*GA) - 0.5645)/20
    elasticity_lcca = 13.5E5*Es/Es28

    length_ist = (1/3)*0.1*(-6.079 + 0.6370*GA)
    radius_ist = (4.2430*np.log(0.0702*GA) + 0.2784)/20
    elasticity_ist = 7.5E5*Es/Es28

    length_dAoA = (1/3)*0.1*(-6.079 + 0.6370*GA)
    radius_dAoA = (4.4126*np.log(0.1304*GA) - 1.8989)/20
    elasticity_dAoA = 7.5E5*Es/Es28

    length_aAoA = (1/3)*0.1*(-6.079 + 0.6370*GA)
    radius_aAoA = (3.9115*np.log(0.1974*GA) - 2.8041)/20
    elasticity_aAoA = 7.5E5*Es/Es28

    length_aAo = 0.1*(-4.678 + 0.4647*GA)
    radius_aAo = (5.4873*np.log(0.1583*GA) - 3.2911)/20
    elasticity_aAo = 7.5E5*Es/Es28

    length_tAo = 0.1*(-19.654+2.0512*GA)
    radius_tAo = (6.1507*np.log(0.0654*GA) + 0.4682)/20
    elasticity_tAo = 9.0E5*Es/Es28

    length_duct = 0.1*(-3.0726+0.4381*GA) 
    kduct = 0.0028*GA + 0.798
    radius_duct = (5.3851*np.log(17.1555*GA) - 29.9470)/20
    elasticity_duct = 13.5E5*Es/Es28
    k_DA=0.009 

    length_pA = 0.1*(-5.6035+0.5705*GA)
    radius_pA = (8.8763*np.log(0.1454*GA) - 6.4004)/20
    elasticity_pA = 7.5E5*Es/Es28

    m.setConstantOrState0('Parameters', 'Bisthm', 1.05*1.706e-4/(2*0.2275*(np.pi*radius_ist**2)**2))
    m.setConstantOrState0('Parameters', 'Bda', 1.05*1.706e-4/(2*0.2275*(np.pi*radius_duct**2)**2))
    m.setConstantOrState0('Parameters', 'Bmpa', 1.05*1.706e-4/(2*0.2275*(np.pi*radius_pA**2)**2))
    m.setConstantOrState0('Parameters', 'BdAoA', 1.05*1.706e-4/(2*0.2275*(np.pi*radius_dAoA**2)**2))