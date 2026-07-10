import numpy as np
from scipy import optimize
import importlib
import functions_to_import as fhealthy
import solver.model
#import solver.cwrapping 
importlib.reload(solver.model)
importlib.reload(solver.model.cwrapping)

def ventricular_disproportion_vasculature(m,degree_aovalve,degree_pvvalve,default_values):
    # Radius arch
    radius_bct = 0.19899999999999998
    radius_lsca = 0.136435
    radius_rsca = 0.136435
    radius_lcca = 0.15234000000000003
    radius_ist = 0.2329
    radius_dAoA = 0.24756422700788266
    radius_aAoA = 0.26546686273838843
    radius_aAo = 0.2984690662736599
    radius_tAo = 0.25955
    radius_duct = 0.2090187021180712
    radius_pA = 0.3415

    #print(f"degree_pvvalve = {degree_pvvalve}")
    #print(f"degree_aovalve = {degree_aovalve}")
    
    # Pulmonary artery
    degree_pa = np.sqrt(degree_pvvalve)
    #print(f"degree_pa = {degree_pa}")
    m.setConstantOrState0('Parameters', 'Rpa', default_values['Rpa']/(degree_pa**4)) 
    m.setConstantOrState0('Parameters', 'Bmpa', default_values['Bmpa']/(degree_pa**4)) 
    m.setConstantOrState0('Parameters', 'Cpa', default_values['Cpa']*(degree_pa**2))
    m.setConstantOrState0('Parameters', 'Lpa', default_values['Lpa']/(degree_pa**2)) 
    
    # Ascending aorta
    #print(degree_aovalve)
    degree_aAo = np.sqrt(degree_aovalve)
    #print(f"degree_aAo = {degree_aAo}")
    m.setConstantOrState0('Parameters', 'Raa', default_values['Raa']/(degree_aAo**4)) 
    m.setConstantOrState0('Parameters', 'Caa', default_values['Caa']*(degree_aAo**2))
    m.setConstantOrState0('Parameters', 'Laa', default_values['Laa']/(degree_aAo**2)) 

    # Ascending aortic arch
    degree_aAoA = np.cbrt(((degree_aAo*radius_aAo)**3 - radius_bct**3)/radius_aAoA**3)
    m.setConstantOrState0('Parameters', 'RaAoA', default_values['RaAoA']/(degree_aAoA**4))     
    m.setConstantOrState0('Parameters', 'CaAoA', default_values['CaAoA']*(degree_aAoA**2))
    m.setConstantOrState0('Parameters', 'LaAoA', default_values['LaAoA']/(degree_aAoA**2))   
        
    # Desdending aortic arch
    degree_dAoA = np.cbrt(((degree_aAoA*radius_aAoA)**3 - radius_lcca**3)/radius_dAoA**3)
    m.setConstantOrState0('Parameters', 'RdAoA', default_values['RdAoA']/(degree_dAoA**4))
    m.setConstantOrState0('Parameters', 'BdAoA', default_values['BdAoA']/(degree_dAoA**4))
    m.setConstantOrState0('Parameters', 'CdAoA', default_values['CdAoA']*(degree_dAoA**2))
    m.setConstantOrState0('Parameters', 'LdAoA', default_values['LdAoA']/(degree_dAoA**2)) 
    
    # Aortic isthmus
    degree_ist = np.cbrt(((degree_dAoA*radius_dAoA)**3 - radius_lsca**3)/radius_ist**3)
    m.setConstantOrState0('Parameters', 'Risthm', default_values['Risthm']/(degree_ist**4))
    m.setConstantOrState0('Parameters', 'Bisthm', default_values['Bisthm']/(degree_ist**4))
    m.setConstantOrState0('Parameters', 'Cisthm', default_values['Cisthm']*(degree_ist**2))
    m.setConstantOrState0('Parameters', 'Listhm', default_values['Listhm']/(degree_ist**2))
    #print(degree_ist)

def ductus_change(m,degree_da,default_constants):
    m.setConstantOrState0('Parameters', 'Rda', default_constants['Rda']/(degree_da**4)) 
    m.setConstantOrState0('Parameters', 'Bda', default_constants['Bda']/(degree_da**4))
    return default_constants

def brain_change(m,degree_brain,default_values):
    degree_vessels = degree_brain #np.cbrt(1/degree_brain)
    m.setConstantOrState0('Parameters', 'R_L_br_p', default_values['R_L_br_p']/(degree_vessels**4)) 
    m.setConstantOrState0('Parameters', 'R_R_br_p', default_values['R_R_br_p']/(degree_vessels**4))
    m.setConstantOrState0('Parameters', 'R_L_br', default_values['R_L_br']/(degree_vessels**4)) 
    m.setConstantOrState0('Parameters', 'R_R_br', default_values['R_R_br']/(degree_vessels**4))
    m.setConstantOrState0('Parameters', 'C_L_br', default_values['C_L_br']*(degree_vessels**2)) 
    m.setConstantOrState0('Parameters', 'C_R_br', default_values['C_R_br']*(degree_vessels**2)) 

    m.setConstantOrState0('Parameters', 'R_L_ICA', default_values['R_L_ICA']/(degree_vessels**4)) 
    m.setConstantOrState0('Parameters', 'R_L_CCA', default_values['R_L_CCA']/(degree_vessels**4)) 
    m.setConstantOrState0('Parameters', 'R_R_ICA', default_values['R_R_ICA']/(degree_vessels**4)) 
    m.setConstantOrState0('Parameters', 'R_R_CCA', default_values['R_R_CCA']/(degree_vessels**4)) 
    m.setConstantOrState0('Parameters', 'C_L_ICA', default_values['C_L_ICA']*(degree_vessels**2)) 
    m.setConstantOrState0('Parameters', 'C_L_CCA', default_values['C_L_CCA']*(degree_vessels**2)) 
    m.setConstantOrState0('Parameters', 'C_R_ICA', default_values['C_R_ICA']*(degree_vessels**2)) 
    m.setConstantOrState0('Parameters', 'C_R_CCA', default_values['C_R_CCA']*(degree_vessels**2)) 
    m.setConstantOrState0('Parameters', 'Rsvc', default_values['Rsvc']/(degree_vessels**4)) 
    m.setConstantOrState0('Parameters', 'Csvc', default_values['Csvc']*(degree_vessels**2))

def fetal_TGA():
    v_degree_Afo = [1,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2] 
    v_degree_da = np.linspace(1,0.6,9)
    v_degree_lung = np.linspace(1,1.75,9)
    v_degree_Rlung = v_degree_lung**(-4/3)
    v_degree_Clung = v_degree_lung**(2/3)
    v_degree_dv = [0.9,0.8,0.7,0.6,0.5,0.4] 
    v_degree_brain = [1,1.05,1.1,1.15] 
    v_change_RA_RV = 1.05*np.asarray([1.1978057922708945,1.216802367643545,1.2372096020575007,1.2590167212061103,1.2827098866096258,1.3090626004699915,1.3387868196691453,1.3737595989542841,1.4173752324854583])
    v_change_LA_LV = 0.9*np.asarray([0.8317880074029675,0.7882507838376269,0.7467440282193657,0.7070986083322605,0.6674103545436759,0.625682378570038,0.5806958091345805,0.5295440663608926,0.46651534643586606])

    v_change_RA_RV_2 = np.asarray([1,1.06,1.12,1.18])
    Tc = 0.43
     
    for ii in range(len(v_degree_Afo)):
        degree_Afo = v_degree_Afo[ii]
        degree_da = v_degree_da[ii]
        degree_lung = v_degree_Rlung[ii]
        degree_Clung = v_degree_Clung[ii]
        change_RA_RV = v_change_RA_RV[ii]
        change_LA_LV = v_change_LA_LV[ii]

        for degree_dv in v_degree_dv:

            for jj in range(len(v_degree_brain)):

                data = np.load("default_constants.npz", allow_pickle=True)   
                default_constants = {key: data[key] for key in data}

                degree_brain = v_degree_brain[jj]
                change_RA_RV_2 = v_change_RA_RV_2[jj]

                m = solver.model.ModelSolver('FETAL_MODEL_36_TGA_FO2.c')

                tFinal = 100*Tc

                FO_volume_change = degree_Afo**(3/2)
                change_aortic_valve = (change_RA_RV*change_RA_RV_2)**(2/3)  
                change_pulmonary_valve = change_LA_LV**(2/3)      

                Amref_ra = 7.5825*change_RA_RV**(2/3)
                Amref_rv = 20.43225*change_RA_RV**(2/3)
                Vwall_ra = 1.232*change_RA_RV
                Vwall_rv = 8.9973*change_RA_RV
                Amref_la = 7.5825*change_LA_LV**(2/3)
                Amref_lv = 20.43225*change_LA_LV**(2/3)
                Vwall_la = 1.232*change_LA_LV
                Vwall_lv = 8.9973*change_LA_LV
                
                default_constants = ductus_change(m,degree_da,default_constants)

                m.setConstantOrState0('Parameters', 'Vwall_lv', Vwall_lv)
                m.setConstantOrState0('Parameters', 'Vwall_rv', Vwall_rv)
                m.setConstantOrState0('Parameters', 'Amref_lv', Amref_lv)
                m.setConstantOrState0('Parameters', 'Amref_rv', Amref_rv)   
                m.setConstantOrState0('Parameters', 'Vwall_la', default_constants['Vwall_la']*Vwall_lv/default_constants['Vwall_lv'])
                m.setConstantOrState0('Parameters', 'Vwall_ra', default_constants['Vwall_ra']*Vwall_rv/default_constants['Vwall_rv'])
                m.setConstantOrState0('Parameters', 'Amref_la', default_constants['Amref_la']*Vwall_lv**(2/3)/default_constants['Vwall_lv']**(2/3))
                m.setConstantOrState0('Parameters', 'Amref_ra', default_constants['Amref_ra']*Vwall_rv**(2/3)/default_constants['Vwall_rv']**(2/3))
                m.setConstantOrState0('Parameters', 'Aao', default_constants['Aao']*change_aortic_valve**(2/3)) # TGA
                m.setConstantOrState0('Parameters', 'Ami', default_constants['Ami']*Vwall_lv**(2/3)/default_constants['Vwall_lv']**(2/3))
                m.setConstantOrState0('Parameters', 'Apv', default_constants['Apv']*change_pulmonary_valve**(2/3)) # TGA
                m.setConstantOrState0('Parameters', 'Atr', default_constants['Atr']*Vwall_rv**(2/3)/default_constants['Vwall_rv']**(2/3))        
                ventricular_disproportion_vasculature(m,change_aortic_valve**(2/3),change_pulmonary_valve**(2/3),default_constants)
                
                m.setConstantOrState0('LV', 'Vcav', 23.5) 
                m.setConstantOrState0('RV', 'Vcav', 23.5)
                m.setConstantOrState0('LA', 'Vcav', 23.5)
                m.setConstantOrState0('RA', 'Vcav', 23.5)
                m.setConstantOrState0('Parameters', 'percentage_DV_to_FO', degree_dv)  

                m.setConstantOrState0('Parameters', 'Afo', 0.471*degree_Afo)  
                m.setConstantOrState0('Parameters', 'Rla', 0.5691*degree_lung) 
                m.setConstantOrState0('Parameters', 'Rlung', 11.4*degree_lung) 
                m.setConstantOrState0('Parameters', 'Clung', 0.33821*degree_lung) 

                 
                brain_change(m,degree_brain,default_constants)

                with fhealthy.HiddenPrints():
                    m.solve(tFinal = tFinal) 
                    
                m.saveResults('./Results_TGA_100/FO' + str(round(degree_Afo*100)) + '_DA' + str(round(degree_da*100)) + '_LUNG' + str(round(degree_lung*100)) + '_DV' + str(round(degree_dv*100)) + '_BRAIN' + str(round(degree_brain*100)) + '.npz', degree_Afo = degree_Afo, degree_da = degree_da, degree_lung = degree_lung, degree_dv = degree_dv, degree_brain = degree_brain)

                idx = m.t > tFinal - Tc
                input_variables_o2 = {
                    "Q_PLAC": np.round(np.trapz(m.getVariable("UA_RC", "Qo")[idx]/0.43, m.t[idx]),3),
                    "Q_BR": np.round(np.trapz((m.getVariable("ICaroAR_RCL", "Qo")[idx]+m.getVariable("ICaroAL_RCL", "Qo")[idx])/0.43, m.t[idx]),3),
                    "Q_UB": np.round(np.trapz((m.getVariable("SubAR_RCL", "Qo")[idx]+m.getVariable("SubAL_RCL", "Qo")[idx])/0.43, m.t[idx]),3),
                    "Q_DA": np.round(np.trapz(m.getVariable("Bif_PAin_LUNG1out_DA2out", "Qo2")[idx]/0.43, m.t[idx]),3),
                    "Q_LUNG": np.round(np.trapz(m.getVariable("Bif_PAin_LUNG1out_DA2out", "Qo1")[idx]/0.43, m.t[idx]),3),
                    "Q_AO": np.round(np.trapz(m.getVariable("AI_RCL", "Qo")[idx], m.t[idx])/0.43,3),
                    "Q_KID": np.round(np.trapz(m.getVariable("Bif_AOin_AO1out_INTE2out_HE3out_KID4out", "Qo4")[idx]/0.43, m.t[idx]),3),
                    "Q_HeArt": np.round(np.trapz(m.getVariable("Bif_AOin_AO1out_INTE2out_HE3out_KID4out", "Qo3")[idx]/0.43, m.t[idx]),3),
                    "Q_IntraHe": np.round(np.trapz(m.getVariable("Bif_UVin_DV1out_HE2out", "Qo2")[idx], m.t[idx])/0.43,3),
                    "Q_INTE": np.round(np.trapz(m.getVariable("Bif_AOin_AO1out_INTE2out_HE3out_KID4out", "Qo2")[idx]/0.43, m.t[idx]),3),
                    "Q_LEG": np.round(np.trapz(m.getVariable("Bif_AOin_LEG1out_UA2out", "Qo1")[idx]/0.43, m.t[idx]),3),
                    "Q_DVfo": np.round(np.trapz(m.getVariable("Bif_DVin_FO1out_RA2out", "Qo1")[idx]/0.43, m.t[idx]),3),
                    "Q_DVra": np.round(np.trapz(m.getVariable("Bif_DVin_FO1out_RA2out", "Qo2")[idx]/0.43, m.t[idx]),3),
                    "Q_IVCfo": np.round(np.trapz(m.getVariable("Bif_IVCin_FO1out_RA2out", "Qo1")[idx]/0.43, m.t[idx]),3),
                    "Q_IVCra": np.round(np.trapz(m.getVariable("Bif_IVCin_FO1out_RA2out", "Qo2")[idx]/0.43, m.t[idx]),3),
                    "Q_CORONARIES": np.round(np.trapz(m.getVariable("Coronary_R", "Qo")[idx], m.t[idx])/0.43,3),
                }
                np.savez('./Flow_TGA_100/Flow_FO' + str(round(degree_Afo*100)) + '_DA' + str(round(degree_da*100)) + '_LUNG' + str(round(degree_lung*100)) + '_DV' + str(round(degree_dv*100)) + '_BRAIN' + str(round(degree_brain*100)) + '.npz', **input_variables_o2)

    return m       

# RUN SIMULATIONS
m = fetal_TGA()