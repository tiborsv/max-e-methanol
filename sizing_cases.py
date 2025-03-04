from dataclasses import dataclass, field
import numpy as np
import itertools

@dataclass(kw_only=True)
class SizingResults:
    name: str = ""
    SizingCases_run = list
    CAPgen_ins = float
    ratio_wind_solar = float
    Production_annual_t_list = list
    LCOMeOH_list = list
    CAP_ins_list_IN = list
    S_ins_list_IN = list
    CAP_ins_list_OUT = list
    S_ins_list_OUT = list
    df_LCOMeOH_stacked_bar = list
    LCOMeOH_selected = float
    Production_annual_t_selected = float
    CAP_ins_selected = dict
    S_ins_selected = dict
@dataclass(kw_only=True)
class SizingCase:
    name: str = "Sizing case (SC)"
    description: str = ('defines the relative sizes of process units of a particular design')
    rel_CAP_ins: dict = field(default_factory=lambda: {"WEL":   [],
                                                      "DAC":    [],
                                                      "MTS":    [],
                                                      "HP_int": [], # heat pump for integration (providing 100 heat)
                                                      "HP_amb": []  # heat pump providing LT heat (50 degC) from ambient
                                                      })

    S_days_of_storage: dict = field(default_factory= lambda: {  'CGH2': [],
                                                                'CO2tank': [],
                                                                'BAT': [],
                                                                'TES': []})

    rel_CAP_ins_alternatives: dict = field(default_factory=lambda: {"WEL":   [0],
                                                                      "DAC":    [0],
                                                                      "MTS":    [0],
                                                                      "HP_int": [0], # heat pump for integration (providing 100 heat)
                                                                      "HP_amb": [0]  # heat pump providing LT heat (50 degC) from ambient
                                                                      })

    S_days_of_storage_alternatives: dict = field(default_factory=lambda: {'CGH2': [0],
                                                                         'CO2tank': [0],
                                                                         'BAT': [0],
                                                                         'TES': [0]})


Sync_WDM = SizingCase(name="WDM")
Sync_WDM.description = "WEL, DAC, MTS synchronized with GEN"
Sync_WDM.rel_CAP_ins_alternatives['WEL'] = [0.9, 0.8, 0.7, 0.6]
for k in Sync_WDM.rel_CAP_ins.keys():
    Sync_WDM.rel_CAP_ins[k] = Sync_WDM.rel_CAP_ins_alternatives['WEL']

Sync_WDM.rel_CAP_ins['HP_int'] = list(np.ones(len(Sync_WDM.rel_CAP_ins_alternatives['WEL'])))

for k in Sync_WDM.S_days_of_storage_alternatives.keys():
    Sync_WDM.S_days_of_storage[k] = [0]


process_rel_CAP_alternatives = [1.0, 0.8, 0.6, 0.4]
storage_days_alternatives = [0.5, 1.0, 2.0, 3.0, 4.0]

Sync_W = SizingCase(name="W")
Sync_W.description = "WEL synchronized with GEN"

Sync_W.rel_CAP_ins_alternatives['WEL'] = process_rel_CAP_alternatives
Sync_W.rel_CAP_ins_alternatives['MTS'] = process_rel_CAP_alternatives

rel_CAP_ins_product = list(itertools.product(*[Sync_W.rel_CAP_ins_alternatives[k] for k in ['WEL', 'MTS']]))
rel_CAP_ins_product_filter = []

rel_CAP_ins_WEL = []
rel_CAP_ins_MTS = []

for i in range(len(rel_CAP_ins_product)):
    if rel_CAP_ins_product[i][0] > rel_CAP_ins_product[i][1]:
        rel_CAP_ins_product_filter.append(rel_CAP_ins_product[i])
        rel_CAP_ins_WEL.append(rel_CAP_ins_product[i][0])
        rel_CAP_ins_MTS.append(rel_CAP_ins_product[i][1])

Sync_W.rel_CAP_ins['WEL'] = rel_CAP_ins_WEL
Sync_W.rel_CAP_ins['DAC'] = rel_CAP_ins_MTS
Sync_W.rel_CAP_ins['HP_amb'] = rel_CAP_ins_MTS
Sync_W.rel_CAP_ins['HP_int'] = list(np.ones(len(rel_CAP_ins_WEL)))
Sync_W.rel_CAP_ins['MTS'] = rel_CAP_ins_MTS

Sync_W.S_days_of_storage_alternatives['CGH2'] = storage_days_alternatives
Sync_W.S_days_of_storage_alternatives['CO2tank'] = [0]
Sync_W.S_days_of_storage_alternatives['BAT'] = storage_days_alternatives
Sync_W.S_days_of_storage_alternatives['TES'] = [0]


Sync_WD = SizingCase(name="WD")
Sync_WD.description = "WEL, DAC synchronized with GEN"

Sync_WD.rel_CAP_ins_alternatives['WEL'] = process_rel_CAP_alternatives
Sync_WD.rel_CAP_ins_alternatives['MTS'] = process_rel_CAP_alternatives

rel_CAP_ins_product = list(itertools.product(*[Sync_WD.rel_CAP_ins_alternatives[k] for k in ['WEL', 'MTS']]))
rel_CAP_ins_product_filter = []

rel_CAP_ins_WEL = []
rel_CAP_ins_MTS = []

for i in range(len(rel_CAP_ins_product)):
    if rel_CAP_ins_product[i][0] > rel_CAP_ins_product[i][1]:
        rel_CAP_ins_product_filter.append(rel_CAP_ins_product[i])
        rel_CAP_ins_WEL.append(rel_CAP_ins_product[i][0])
        rel_CAP_ins_MTS.append(rel_CAP_ins_product[i][1])

Sync_WD.rel_CAP_ins['WEL'] = rel_CAP_ins_WEL
Sync_WD.rel_CAP_ins['DAC'] = rel_CAP_ins_WEL
Sync_WD.rel_CAP_ins['HP_amb'] = rel_CAP_ins_WEL
Sync_WD.rel_CAP_ins['HP_int'] = list(np.ones(len(rel_CAP_ins_WEL)))
Sync_WD.rel_CAP_ins['MTS'] = rel_CAP_ins_MTS

Sync_WD.S_days_of_storage_alternatives['CGH2'] = storage_days_alternatives
Sync_WD.S_days_of_storage_alternatives['CO2tank'] = storage_days_alternatives
Sync_WD.S_days_of_storage_alternatives['BAT'] = storage_days_alternatives
Sync_WD.S_days_of_storage_alternatives['TES'] = [0]

