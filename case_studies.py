from dataclasses import dataclass, field
from process_parameters import PEM, SOEC, DAC_L, DAC_S, MT, HP_50_100, HP_Tamb_50, HP_Tamb_100, BAT_in, BAT_out, CGH2_in, CGH2_out, TES_in, TES_out, CO2tank_in, CO2tank_out, Curt


@dataclass(kw_only=True)
class Case:
    name: str = "PEM, DAC-S, MTS, nu = 1"
    description: str = '-'

    de: dict = field(default_factory=lambda: {"WEL": PEM,
                                              "DAC": DAC_S,
                                              "MTS": MT,
                                              "HP_int": HP_50_100,
                                              "HP_amb": HP_Tamb_100,
                                              "BAT_in": BAT_in,
                                              "BAT_out": BAT_out,
                                              "CGH2_in": CGH2_in,
                                              "CGH2_out": CGH2_out,
                                              "TES_in": TES_in,
                                              "TES_out": TES_out,
                                              "CO2tank_in": CO2tank_in,
                                              "CO2tank_out": CO2tank_out,
                                              "Curt" : Curt})  # [-] DEsign selection (selecting the type of WEL, DAC and MTS)

    nu: dict = field(default_factory=lambda: {"WEL": 1,
                                              "DAC": 1,
                                              "MTS": 1,
                                              "HP_int": 1,
                                              "HP_amb": 1,
                                              "BAT_in": 1,
                                              "BAT_out": 1,
                                              "CGH2_in": 1,
                                              "CGH2_out": 1,
                                              "TES_in": 1,
                                              "TES_out": 1,
                                              "CO2tank_in": 1,
                                              "CO2tank_out": 1,
                                              "Curt": 1,
                                              })  # [-] Number of Units as part of the design for each technology

    cmp: dict = field(default_factory=lambda: { "WEL": 0,
                                                "DAC": 0,
                                                "MTS": 0,
                                                "HP_int": 0,
                                                "HP_amb": 0,
                                                "BAT_in": 0,
                                                "BAT_out": 0,
                                                "CGH2_in": 0,
                                                "CGH2_out": 0,
                                                "TES_in": 0,
                                                "TES_out": 0,
                                                "CO2tank_in": 0,
                                                "CO2tank_out": 0,
                                                "Curt":0
                                                }) # [-] Coefficient of Mass Production (learning rate)
    year: str = '2020'

    minCAP: dict = field(default_factory=lambda: { "WEL": 0,
                                                    "DAC": 0,
                                                    "MTS": 0,
                                                    "HP_int": 0,
                                                    "HP_amb": 0,
                                                    "BAT_in": 0,
                                                    "BAT_out": 0,
                                                    "CGH2_in": 0,
                                                    "CGH2_out": 0,
                                                    "TES_in": 0,
                                                    "TES_out": 0,
                                                    "CO2tank_in": 0,
                                                    "CO2tank_out": 0,
                                                    "Curt":0
                                                    }) # [-] Coefficient of Mass Production (learning rate)

    switch_capex_max_cap_scaling: float = 0
    switch_capex_max_cap_scaling_equal_sizes: float = 0
    res: dict = field(default_factory= lambda: {})
    time_of_run: str = ''

@dataclass(kw_only=True)
class CaseStudy:
    name: str
    description: str = ''
    cases: dict = field(default_factory=lambda: {})  # [-] a dictionary which combines different Cases to construct a CaseStudy


C_p01s01m01 = Case()

C_p02s02m02 = Case(name = "PEM, DAC-S, MTS, nu = 2")
C_p02s02m02.nu.update(dict.fromkeys(["WEL", "DAC", "MTS"], 2))

C_p04s04m04 = Case(name = "PEM, DAC-S, MTS, nu = 4")
C_p04s04m04.nu.update(dict.fromkeys(["WEL", "DAC", "MTS"], 4))

C_p08s08m08 = Case(name="PEM, DAC-S, MTS, nu = 8")
C_p08s08m08.nu.update(dict.fromkeys(["WEL", "DAC", "MTS"], 8))

C_p16s16m16 = Case(name="PEM, DAC-S, MTS, nu = 16")
C_p16s16m16.nu.update(dict.fromkeys(["WEL", "DAC", "MTS"], 16))

C_p32s32m32 = Case(name="PEM, DAC-S, MTS, nu = 32")
C_p32s32m32.nu.update(dict.fromkeys(["WEL", "DAC", "MTS"], 32))

CS_nu = CaseStudy(name = 'Case study into increasing the number of units uniformly for all technologies')
CS_nu.cases = [C_p01s01m01, C_p02s02m02, C_p04s04m04, C_p08s08m08, C_p16s16m16, C_p32s32m32]


C_p10s10m10_cmp00 = Case(name="PEM, DAC-S, MTS, nu = 10, cmp = 0.00")
C_p10s10m10_cmp00.nu.update(dict.fromkeys(["WEL", "DAC","MTS"], 10))

C_p10s10m10_cmp05 = Case(name="PEM, DAC-S, MTS, nu = 10, cmp = 0.05")
C_p10s10m10_cmp05.nu.update(dict.fromkeys(["WEL", "DAC","MTS"], 10))
C_p10s10m10_cmp05.cmp.update(dict.fromkeys(["WEL", "DAC","MTS"], 0.05))

C_p10s10m10_cmp10 = Case(name="PEM, DAC-S, MTS, nu = 10, cmp = 0.10")
C_p10s10m10_cmp10.nu.update(dict.fromkeys(["WEL", "DAC","MTS"], 10))
C_p10s10m10_cmp10.cmp.update(dict.fromkeys(["WEL", "DAC","MTS"], 0.10))

CS_cmp = CaseStudy(name = 'Case study into increasing the coefficient of mass production uniformly for all technologies')
CS_cmp.cases = [C_p10s10m10_cmp00, C_p10s10m10_cmp05, C_p10s10m10_cmp10]


C_p1s1m1_y2020 = Case(name = "C_p1s1m1_y2020")
C_p1s1m1_y2020.description = "PEM, DAC-S, MTS, year = 2020"
C_p1s1m1_y2020.year = '2020'

C_p1s1m1_y2030 = Case(name = "C_p1s1m1_y2030")
C_p1s1m1_y2030.description = "PEM, DAC-S, MTS, year = 2030"
C_p1s1m1_y2030.year = '2030'

C_p1s1m1_y2050 = Case(name = "C_p1s1m1_y2050")
C_p1s1m1_y2050.description = "PEM, DAC-S, MTS, year = 2050"
C_p1s1m1_y2050.year = '2050'

CS_psm_years = CaseStudy(name = 'CS_YEARS_p1s1m1')
CS_psm_years.description = 'Case study of different years for a 1 unit PEM, DAC-S, MTS design'
CS_psm_years.cases = [C_p1s1m1_y2020, C_p1s1m1_y2030, C_p1s1m1_y2050]


C_p1l1m1_y2020 = Case(name = "C_p1l1m1_y2020")
C_p1l1m1_y2020.description = "PEM, DAC-L, MTS, year = 2020"
C_p1l1m1_y2020.de.update({'DAC': DAC_L})
C_p1l1m1_y2020.year = '2020'

C_p1l1m1_y2030 = Case(name = "C_p1l1m1_y2030")
C_p1l1m1_y2030.description = "PEM, DAC-L, MTS, year = 2030"
C_p1l1m1_y2030.de.update({'DAC': DAC_L})
C_p1l1m1_y2030.year = '2030'

C_p1l1m1_y2050 = Case(name = "C_p1l1m1_y2050")
C_p1l1m1_y2050.description = "PEM, DAC-L, MTS, year = 2050"
C_p1l1m1_y2050.de.update({'DAC': DAC_L})
C_p1l1m1_y2050.year = '2050'

CS_plm_years = CaseStudy(name = 'CS_YEARS_p1l1m1')
CS_plm_years.description = 'Case study of different years for a 1 unit PEM, DAC-L, MTS design'
CS_plm_years.cases = [C_p1l1m1_y2020, C_p1l1m1_y2030, C_p1l1m1_y2050]


# MIN CAPACITY DACL



C_p1l1m1_y2020_minCAP_DACL_25 = Case(name = "C_p1l1m1_y2020_minCAP_DACL_25")
C_p1l1m1_y2020_minCAP_DACL_25.description = "PEM, DAC-L, MTS, year = 2020"
C_p1l1m1_y2020_minCAP_DACL_25.de.update({'DAC': DAC_L})
C_p1l1m1_y2020_minCAP_DACL_25.year = '2020'
C_p1l1m1_y2020_minCAP_DACL_25.minCAP.update(dict.fromkeys(["DAC"], 0.25))

C_p1l1m1_y2030_minCAP_DACL_25 = Case(name = "C_p1l1m1_y2030_minCAP_DACL_25")
C_p1l1m1_y2030_minCAP_DACL_25.description = "PEM, DAC-L, MTS, year = 2030"
C_p1l1m1_y2030_minCAP_DACL_25.de.update({'DAC': DAC_L})
C_p1l1m1_y2030_minCAP_DACL_25.year = '2030'
C_p1l1m1_y2030_minCAP_DACL_25.minCAP.update(dict.fromkeys(["DAC"], 0.25))

C_p1l1m1_y2050_minCAP_DACL_25 = Case(name = "C_p1l1m1_y2050_minCAP_DACL_25")
C_p1l1m1_y2050_minCAP_DACL_25.description = "PEM, DAC-L, MTS, year = 2050"
C_p1l1m1_y2050_minCAP_DACL_25.de.update({'DAC': DAC_L})
C_p1l1m1_y2050_minCAP_DACL_25.year = '2050'
C_p1l1m1_y2050_minCAP_DACL_25.minCAP.update(dict.fromkeys(["DAC"], 0.25))

CS_plm_years_minCAP_DACL_25 = CaseStudy(name = 'CS_YEARS_minCAP_DACL_25_p1l1m1')
CS_plm_years_minCAP_DACL_25.description = 'Case study of different minCAP for a 1 unit PEM, DAC-L, MTS design'
CS_plm_years_minCAP_DACL_25.cases = [C_p1l1m1_y2020_minCAP_DACL_25, C_p1l1m1_y2030_minCAP_DACL_25, C_p1l1m1_y2050_minCAP_DACL_25]

C_p1l1m1_y2020_minCAP_DACL_50 = Case(name = "C_p1l1m1_y2020_minCAP_DACL_50")
C_p1l1m1_y2020_minCAP_DACL_50.description = "PEM, DAC-L, MTS, year = 2020"
C_p1l1m1_y2020_minCAP_DACL_50.de.update({'DAC': DAC_L})
C_p1l1m1_y2020_minCAP_DACL_50.year = '2020'
C_p1l1m1_y2020_minCAP_DACL_50.minCAP.update(dict.fromkeys(["DAC"], 0.50))

C_p1l1m1_y2030_minCAP_DACL_50 = Case(name = "C_p1l1m1_y2030_minCAP_DACL_50")
C_p1l1m1_y2030_minCAP_DACL_50.description = "PEM, DAC-L, MTS, year = 2030"
C_p1l1m1_y2030_minCAP_DACL_50.de.update({'DAC': DAC_L})
C_p1l1m1_y2030_minCAP_DACL_50.year = '2030'
C_p1l1m1_y2030_minCAP_DACL_50.minCAP.update(dict.fromkeys(["DAC"], 0.50))

C_p1l1m1_y2050_minCAP_DACL_50 = Case(name = "C_p1l1m1_y2050_minCAP_DACL_50")
C_p1l1m1_y2050_minCAP_DACL_50.description = "PEM, DAC-L, MTS, year = 2050"
C_p1l1m1_y2050_minCAP_DACL_50.de.update({'DAC': DAC_L})
C_p1l1m1_y2050_minCAP_DACL_50.year = '2050'
C_p1l1m1_y2050_minCAP_DACL_50.minCAP.update(dict.fromkeys(["DAC"], 0.50))

CS_plm_years_minCAP_DACL_50 = CaseStudy(name = 'CS_YEARS_minCAP_DACL_50_p1l1m1')
CS_plm_years_minCAP_DACL_50.description = 'Case study of different minCAP for a 1 unit PEM, DAC-L, MTS design'
CS_plm_years_minCAP_DACL_50.cases = [C_p1l1m1_y2020_minCAP_DACL_50, C_p1l1m1_y2030_minCAP_DACL_50, C_p1l1m1_y2050_minCAP_DACL_50]


C_p1l1m1_y2020_minCAP_DACL_75 = Case(name = "C_p1l1m1_y2020_minCAP_DACL_75")
C_p1l1m1_y2020_minCAP_DACL_75.description = "PEM, DAC-L, MTS, year = 2020"
C_p1l1m1_y2020_minCAP_DACL_75.de.update({'DAC': DAC_L})
C_p1l1m1_y2020_minCAP_DACL_75.year = '2020'
C_p1l1m1_y2020_minCAP_DACL_75.minCAP.update(dict.fromkeys(["DAC"], 0.75))

C_p1l1m1_y2030_minCAP_DACL_75 = Case(name = "C_p1l1m1_y2030_minCAP_DACL_75")
C_p1l1m1_y2030_minCAP_DACL_75.description = "PEM, DAC-L, MTS, year = 2030"
C_p1l1m1_y2030_minCAP_DACL_75.de.update({'DAC': DAC_L})
C_p1l1m1_y2030_minCAP_DACL_75.year = '2030'
C_p1l1m1_y2030_minCAP_DACL_75.minCAP.update(dict.fromkeys(["DAC"], 0.75))

C_p1l1m1_y2050_minCAP_DACL_75 = Case(name = "C_p1l1m1_y2050_minCAP_DACL_75")
C_p1l1m1_y2050_minCAP_DACL_75.description = "PEM, DAC-L, MTS, year = 2050"
C_p1l1m1_y2050_minCAP_DACL_75.de.update({'DAC': DAC_L})
C_p1l1m1_y2050_minCAP_DACL_75.year = '2050'
C_p1l1m1_y2050_minCAP_DACL_75.minCAP.update(dict.fromkeys(["DAC"], 0.75))

CS_plm_years_minCAP_DACL_75 = CaseStudy(name = 'CS_YEARS_minCAP_DACL_75_p1l1m1')
CS_plm_years_minCAP_DACL_75.description = 'Case study of different minCAP for a 1 unit PEM, DAC-L, MTS design'
CS_plm_years_minCAP_DACL_75.cases = [C_p1l1m1_y2020_minCAP_DACL_75, C_p1l1m1_y2030_minCAP_DACL_75, C_p1l1m1_y2050_minCAP_DACL_75]

C_p1l1m1_y2020_minCAP_DACL_95 = Case(name = "C_p1l1m1_y2020_minCAP_DACL_95")
C_p1l1m1_y2020_minCAP_DACL_95.description = "PEM, DAC-L, MTS, year = 2020"
C_p1l1m1_y2020_minCAP_DACL_95.de.update({'DAC': DAC_L})
C_p1l1m1_y2020_minCAP_DACL_95.year = '2020'
C_p1l1m1_y2020_minCAP_DACL_95.minCAP.update(dict.fromkeys(["DAC"], 0.95))

C_p1l1m1_y2030_minCAP_DACL_95 = Case(name = "C_p1l1m1_y2030_minCAP_DACL_95")
C_p1l1m1_y2030_minCAP_DACL_95.description = "PEM, DAC-L, MTS, year = 2030"
C_p1l1m1_y2030_minCAP_DACL_95.de.update({'DAC': DAC_L})
C_p1l1m1_y2030_minCAP_DACL_95.year = '2030'
C_p1l1m1_y2030_minCAP_DACL_95.minCAP.update(dict.fromkeys(["DAC"], 0.95))

C_p1l1m1_y2050_minCAP_DACL_95 = Case(name = "C_p1l1m1_y2050_minCAP_DACL_95")
C_p1l1m1_y2050_minCAP_DACL_95.description = "PEM, DAC-L, MTS, year = 2050"
C_p1l1m1_y2050_minCAP_DACL_95.de.update({'DAC': DAC_L})
C_p1l1m1_y2050_minCAP_DACL_95.year = '2050'
C_p1l1m1_y2050_minCAP_DACL_95.minCAP.update(dict.fromkeys(["DAC"], 0.95))

CS_plm_years_minCAP_DACL_95 = CaseStudy(name = 'CS_YEARS_minCAP_DACL_95_p1l1m1')
CS_plm_years_minCAP_DACL_95.description = 'Case study of different minCAP for a 1 unit PEM, DAC-L, MTS design'
CS_plm_years_minCAP_DACL_95.cases = [C_p1l1m1_y2020_minCAP_DACL_95, C_p1l1m1_y2030_minCAP_DACL_95, C_p1l1m1_y2050_minCAP_DACL_95]




# MIN CAPACITY MTS



C_p1s1m1_y2020_minCAP_MTS_25 = Case(name = "C_p1s1m1_y2020_minCAP_MTS_25")
C_p1s1m1_y2020_minCAP_MTS_25.description = "PEM, DAC-S, MTS, year = 2020"
C_p1s1m1_y2020_minCAP_MTS_25.de.update({'DAC': DAC_S})
C_p1s1m1_y2020_minCAP_MTS_25.year = '2020'
C_p1s1m1_y2020_minCAP_MTS_25.minCAP.update(dict.fromkeys(["MTS"], 0.25))

C_p1s1m1_y2030_minCAP_MTS_25 = Case(name = "C_p1s1m1_y2030_minCAP_MTS_25")
C_p1s1m1_y2030_minCAP_MTS_25.description = "PEM, DAC-S, MTS, year = 2030"
C_p1s1m1_y2030_minCAP_MTS_25.de.update({'DAC': DAC_S})
C_p1s1m1_y2030_minCAP_MTS_25.year = '2030'
C_p1s1m1_y2030_minCAP_MTS_25.minCAP.update(dict.fromkeys(["MTS"], 0.25))

C_p1s1m1_y2050_minCAP_MTS_25 = Case(name = "C_p1s1m1_y2050_minCAP_MTS_25")
C_p1s1m1_y2050_minCAP_MTS_25.description = "PEM, DAC-S, MTS, year = 2050"
C_p1s1m1_y2050_minCAP_MTS_25.de.update({'DAC': DAC_S})
C_p1s1m1_y2050_minCAP_MTS_25.year = '2050'
C_p1s1m1_y2050_minCAP_MTS_25.minCAP.update(dict.fromkeys(["MTS"], 0.25))

CS_psm_years_minCAP_MTS_25 = CaseStudy(name = 'CS_YEARS_minCAP_MTS_25_p1s1m1')
CS_psm_years_minCAP_MTS_25.description = 'Case study of different minCAP for a 1 unit PEM, DAC-S, MTS design'
CS_psm_years_minCAP_MTS_25.cases = [C_p1s1m1_y2020_minCAP_MTS_25, C_p1s1m1_y2030_minCAP_MTS_25, C_p1s1m1_y2050_minCAP_MTS_25]



C_p1s1m1_y2020_minCAP_MTS_50 = Case(name = "C_p1s1m1_y2020_minCAP_MTS_50")
C_p1s1m1_y2020_minCAP_MTS_50.description = "PEM, DAC-S, MTS, year = 2020"
C_p1s1m1_y2020_minCAP_MTS_50.de.update({'DAC': DAC_S})
C_p1s1m1_y2020_minCAP_MTS_50.year = '2020'
C_p1s1m1_y2020_minCAP_MTS_50.minCAP.update(dict.fromkeys(["MTS"], 0.50))

C_p1s1m1_y2030_minCAP_MTS_50 = Case(name = "C_p1s1m1_y2030_minCAP_MTS_50")
C_p1s1m1_y2030_minCAP_MTS_50.description = "PEM, DAC-S, MTS, year = 2030"
C_p1s1m1_y2030_minCAP_MTS_50.de.update({'DAC': DAC_S})
C_p1s1m1_y2030_minCAP_MTS_50.year = '2030'
C_p1s1m1_y2030_minCAP_MTS_50.minCAP.update(dict.fromkeys(["MTS"], 0.50))

C_p1s1m1_y2050_minCAP_MTS_50 = Case(name = "C_p1s1m1_y2050_minCAP_MTS_50")
C_p1s1m1_y2050_minCAP_MTS_50.description = "PEM, DAC-S, MTS, year = 2050"
C_p1s1m1_y2050_minCAP_MTS_50.de.update({'DAC': DAC_S})
C_p1s1m1_y2050_minCAP_MTS_50.year = '2050'
C_p1s1m1_y2050_minCAP_MTS_50.minCAP.update(dict.fromkeys(["MTS"], 0.50))

CS_psm_years_minCAP_MTS_50 = CaseStudy(name = 'CS_YEARS_minCAP_MTS_50_p1s1m1')
CS_psm_years_minCAP_MTS_50.description = 'Case study of different minCAP for a 1 unit PEM, DAC-S, MTS design'
CS_psm_years_minCAP_MTS_50.cases = [C_p1s1m1_y2020_minCAP_MTS_50, C_p1s1m1_y2030_minCAP_MTS_50, C_p1s1m1_y2050_minCAP_MTS_50]



C_p1s1m1_y2020_minCAP_MTS_75 = Case(name = "C_p1s1m1_y2020_minCAP_MTS_75")
C_p1s1m1_y2020_minCAP_MTS_75.description = "PEM, DAC-S, MTS, year = 2020"
C_p1s1m1_y2020_minCAP_MTS_75.de.update({'DAC': DAC_S})
C_p1s1m1_y2020_minCAP_MTS_75.year = '2020'
C_p1s1m1_y2020_minCAP_MTS_75.minCAP.update(dict.fromkeys(["MTS"], 0.75))

C_p1s1m1_y2030_minCAP_MTS_75 = Case(name = "C_p1s1m1_y2030_minCAP_MTS_75")
C_p1s1m1_y2030_minCAP_MTS_75.description = "PEM, DAC-S, MTS, year = 2030"
C_p1s1m1_y2030_minCAP_MTS_75.de.update({'DAC': DAC_S})
C_p1s1m1_y2030_minCAP_MTS_75.year = '2030'
C_p1s1m1_y2030_minCAP_MTS_75.minCAP.update(dict.fromkeys(["MTS"], 0.75))

C_p1s1m1_y2050_minCAP_MTS_75 = Case(name = "C_p1s1m1_y2050_minCAP_MTS_75")
C_p1s1m1_y2050_minCAP_MTS_75.description = "PEM, DAC-S, MTS, year = 2050"
C_p1s1m1_y2050_minCAP_MTS_75.de.update({'DAC': DAC_S})
C_p1s1m1_y2050_minCAP_MTS_75.year = '2050'
C_p1s1m1_y2050_minCAP_MTS_75.minCAP.update(dict.fromkeys(["MTS"], 0.75))

CS_psm_years_minCAP_MTS_75 = CaseStudy(name = 'CS_YEARS_minCAP_MTS_75_p1s1m1')
CS_psm_years_minCAP_MTS_75.description = 'Case study of different minCAP for a 1 unit PEM, DAC-S, MTS design'
CS_psm_years_minCAP_MTS_75.cases = [C_p1s1m1_y2020_minCAP_MTS_75, C_p1s1m1_y2030_minCAP_MTS_75, C_p1s1m1_y2050_minCAP_MTS_75]


C_p1s1m1_y2020_minCAP_MTS_95 = Case(name = "C_p1s1m1_y2020_minCAP_MTS_95")
C_p1s1m1_y2020_minCAP_MTS_95.description = "PEM, DAC-S, MTS, year = 2020"
C_p1s1m1_y2020_minCAP_MTS_95.de.update({'DAC': DAC_S})
C_p1s1m1_y2020_minCAP_MTS_95.year = '2020'
C_p1s1m1_y2020_minCAP_MTS_95.minCAP.update(dict.fromkeys(["MTS"], 0.95))

C_p1s1m1_y2030_minCAP_MTS_95 = Case(name = "C_p1s1m1_y2030_minCAP_MTS_95")
C_p1s1m1_y2030_minCAP_MTS_95.description = "PEM, DAC-S, MTS, year = 2030"
C_p1s1m1_y2030_minCAP_MTS_95.de.update({'DAC': DAC_S})
C_p1s1m1_y2030_minCAP_MTS_95.year = '2030'
C_p1s1m1_y2030_minCAP_MTS_95.minCAP.update(dict.fromkeys(["MTS"], 0.95))

C_p1s1m1_y2050_minCAP_MTS_95 = Case(name = "C_p1s1m1_y2050_minCAP_MTS_95")
C_p1s1m1_y2050_minCAP_MTS_95.description = "PEM, DAC-S, MTS, year = 2050"
C_p1s1m1_y2050_minCAP_MTS_95.de.update({'DAC': DAC_S})
C_p1s1m1_y2050_minCAP_MTS_95.year = '2050'
C_p1s1m1_y2050_minCAP_MTS_95.minCAP.update(dict.fromkeys(["MTS"], 0.95))

CS_psm_years_minCAP_MTS_95 = CaseStudy(name = 'CS_YEARS_minCAP_MTS_95_p1s1m1')
CS_psm_years_minCAP_MTS_95.description = 'Case study of different minCAP for a 1 unit PEM, DAC-S, MTS design'
CS_psm_years_minCAP_MTS_95.cases = [C_p1s1m1_y2020_minCAP_MTS_95, C_p1s1m1_y2030_minCAP_MTS_95, C_p1s1m1_y2050_minCAP_MTS_95]











# YEARS maximum capacity scaling

C_p1s1m1_y2020_maxCAPscale = Case(name = "C_p1s1m1_y2020_maxCAPscale")
C_p1s1m1_y2020_maxCAPscale.description = "PEM, DAC-S, MTS, year = 2020, with maximum process capacity scaling"
C_p1s1m1_y2020_maxCAPscale.year = '2020'
C_p1s1m1_y2020_maxCAPscale.switch_capex_max_cap_scaling = 1

C_p1s1m1_y2030_maxCAPscale = Case(name = "C_p1s1m1_y2030_maxCAPscale")
C_p1s1m1_y2030_maxCAPscale.description = "PEM, DAC-S, MTS, year = 2030, with maximum process capacity scaling"
C_p1s1m1_y2030_maxCAPscale.year = '2030'
C_p1s1m1_y2030_maxCAPscale.switch_capex_max_cap_scaling = 1

C_p1s1m1_y2050_maxCAPscale = Case(name = "C_p1s1m1_y2050_maxCAPscale")
C_p1s1m1_y2050_maxCAPscale.description = "PEM, DAC-S, MTS, year = 2050, with maximum process capacity scaling"
C_p1s1m1_y2050_maxCAPscale.year = '2050'
C_p1s1m1_y2050_maxCAPscale.switch_capex_max_cap_scaling = 1

CS_psm_years_maxCAPscale = CaseStudy(name = 'CS_YEARS_p1s1m1_maxCAPscale')
CS_psm_years_maxCAPscale.description = 'Case study of different years for a 1 unit PEM, DAC-S, MTS design, with maximum process capacity scaling'
CS_psm_years_maxCAPscale.cases = [C_p1s1m1_y2020_maxCAPscale, C_p1s1m1_y2030_maxCAPscale, C_p1s1m1_y2050_maxCAPscale]



C_p1l1m1_y2020_maxCAPscale = Case(name = "C_p1l1m1_y2020_maxCAPscale")
C_p1l1m1_y2020_maxCAPscale.description = "PEM, DAC-L, MTS, year = 2020, with maximum process capacity scaling"
C_p1l1m1_y2020_maxCAPscale.year = '2020'
C_p1l1m1_y2020_maxCAPscale.de.update({'DAC': DAC_L})
C_p1l1m1_y2020_maxCAPscale.switch_capex_max_cap_scaling = 1

C_p1l1m1_y2030_maxCAPscale = Case(name = "C_p1l1m1_y2030_maxCAPscale")
C_p1l1m1_y2030_maxCAPscale.description = "PEM, DAC-L, MTS, year = 2030, with maximum process capacity scaling"
C_p1l1m1_y2030_maxCAPscale.year = '2030'
C_p1l1m1_y2030_maxCAPscale.de.update({'DAC': DAC_L})
C_p1l1m1_y2030_maxCAPscale.switch_capex_max_cap_scaling = 1

C_p1l1m1_y2050_maxCAPscale = Case(name = "C_p1l1m1_y2050_maxCAPscale")
C_p1l1m1_y2050_maxCAPscale.description = "PEM, DAC-L, MTS, year = 2050, with maximum process capacity scaling"
C_p1l1m1_y2050_maxCAPscale.year = '2050'
C_p1l1m1_y2050_maxCAPscale.de.update({'DAC': DAC_L})
C_p1l1m1_y2050_maxCAPscale.switch_capex_max_cap_scaling = 1

CS_plm_years_maxCAPscale = CaseStudy(name = 'CS_YEARS_p1l1m1_maxCAPscale')
CS_plm_years_maxCAPscale.description = 'Case study of different years for a 1 unit PEM, DAC-L, MTS design, with maximum process capacity scaling'
CS_plm_years_maxCAPscale.cases = [C_p1l1m1_y2020_maxCAPscale, C_p1l1m1_y2030_maxCAPscale, C_p1l1m1_y2050_maxCAPscale]




@dataclass(kw_only=True)
class GridCase:
    name: str = "-"
    description: str = '-'
    pd_nominal: float = 8   # [MW/km2] nominal installed power density (default = 8 MW/km2)
    N_slices: float = 1     # [-] number of circle slices (1/8th of the circle) the grid consists of (default = 1)
    cable_limit: int = 0    # [-] limiting the number of cables to be maximum of the largest high voltage cable (default = turned off --> maximum number of cables equal to max largest cable for lowest voltage level)
    year: str='2020'        # [-] costing year scenario
    res: dict = field(default_factory=lambda: {})
    time_of_run: str = ''

@dataclass(kw_only=True)
class GridCaseStudy:
    name: str
    description: str = ''
    cases: dict = field(default_factory=lambda: {})  # [-] a dictionary which combines different Cases to construct a CaseStudy



GC_2020_pd_5_Nslice_1_CableLim_0 = GridCase(name = 'GC_2020_pd_5_Nslice_1_CableLim_0')
GC_2020_pd_5_Nslice_1_CableLim_0.pd_nominal = 5 # [MW/km2]

GC_2020_pd_8_Nslice_1_CableLim_0 = GridCase(name = 'GC_2020_pd_8_Nslice_1_CableLim_0')
GC_2020_pd_8_Nslice_1_CableLim_0.pd_nominal = 8

GC_2020_pd_11_Nslice_1_CableLim_0 = GridCase(name = 'GC_2020_pd_11_Nslice_1_CableLim_0')
GC_2020_pd_11_Nslice_1_CableLim_0.pd_nominal = 11

GCS_2020_PDsens_Nslice_1_CableLim_0 = CaseStudy(name = 'GCS_2020_PDsens_Nslice_1_CableLim_0')
GCS_2020_PDsens_Nslice_1_CableLim_0.cases = [GC_2020_pd_5_Nslice_1_CableLim_0, GC_2020_pd_8_Nslice_1_CableLim_0, GC_2020_pd_11_Nslice_1_CableLim_0]


GC_2030_pd_5_Nslice_1_CableLim_0 = GridCase(name = 'GC_2030_pd_5_Nslice_1_CableLim_0')
GC_2030_pd_5_Nslice_1_CableLim_0.pd_nominal = 5 # [MW/km2]
GC_2030_pd_5_Nslice_1_CableLim_0.year = '2030'

GC_2030_pd_8_Nslice_1_CableLim_0 = GridCase(name = 'GC_2030_pd_8_Nslice_1_CableLim_0')
GC_2030_pd_8_Nslice_1_CableLim_0.pd_nominal = 8
GC_2030_pd_8_Nslice_1_CableLim_0.year = '2030'

GC_2030_pd_11_Nslice_1_CableLim_0 = GridCase(name = 'GC_2030_pd_11_Nslice_1_CableLim_0')
GC_2030_pd_11_Nslice_1_CableLim_0.pd_nominal = 11
GC_2030_pd_11_Nslice_1_CableLim_0.year = '2030'

GCS_2030_PDsens_Nslice_1_CableLim_0 = CaseStudy(name = 'GCS_2030_PDsens_Nslice_1_CableLim_0')
GCS_2030_PDsens_Nslice_1_CableLim_0.cases = [GC_2030_pd_5_Nslice_1_CableLim_0, GC_2030_pd_8_Nslice_1_CableLim_0, GC_2030_pd_11_Nslice_1_CableLim_0]


GC_2050_pd_5_Nslice_1_CableLim_0 = GridCase(name = 'GC_2050_pd_5_Nslice_1_CableLim_0')
GC_2050_pd_5_Nslice_1_CableLim_0.pd_nominal = 5 # [MW/km2]
GC_2050_pd_5_Nslice_1_CableLim_0.year = '2050'

GC_2050_pd_8_Nslice_1_CableLim_0 = GridCase(name = 'GC_2050_pd_8_Nslice_1_CableLim_0')
GC_2050_pd_8_Nslice_1_CableLim_0.pd_nominal = 8
GC_2050_pd_8_Nslice_1_CableLim_0.year = '2050'

GC_2050_pd_11_Nslice_1_CableLim_0 = GridCase(name = 'GC_2050_pd_11_Nslice_1_CableLim_0')
GC_2050_pd_11_Nslice_1_CableLim_0.pd_nominal = 11
GC_2050_pd_11_Nslice_1_CableLim_0.year = '2050'

GCS_2050_PDsens_Nslice_1_CableLim_0 = CaseStudy(name = 'GCS_2050_PDsens_Nslice_1_CableLim_0')
GCS_2050_PDsens_Nslice_1_CableLim_0.cases = [GC_2050_pd_5_Nslice_1_CableLim_0, GC_2050_pd_8_Nslice_1_CableLim_0, GC_2050_pd_11_Nslice_1_CableLim_0]




# Cable limit 2020 PDsens
GC_2020_pd_5_Nslice_1_CableLim_1 = GridCase(name = 'GC_2020_pd_5_Nslice_1_CableLim_1')
GC_2020_pd_5_Nslice_1_CableLim_1.pd_nominal = 5 # [MW/km2]
GC_2020_pd_5_Nslice_1_CableLim_1.cable_limit = 1


GC_2020_pd_8_Nslice_1_CableLim_1 = GridCase(name = 'GC_2020_pd_8_Nslice_1_CableLim_1')
GC_2020_pd_8_Nslice_1_CableLim_1.pd_nominal = 8
GC_2020_pd_8_Nslice_1_CableLim_1.cable_limit = 1

GC_2020_pd_11_Nslice_1_CableLim_1 = GridCase(name = 'GC_2020_pd_11_Nslice_1_CableLim_1')
GC_2020_pd_11_Nslice_1_CableLim_1.pd_nominal = 11
GC_2020_pd_11_Nslice_1_CableLim_1.cable_limit = 1

GCS_2020_PDsens_Nslice_1_CableLim_1 = CaseStudy(name = 'GCS_2020_PDsens_Nslice_1_CableLim_1')
GCS_2020_PDsens_Nslice_1_CableLim_1.cases = [GC_2020_pd_5_Nslice_1_CableLim_1, GC_2020_pd_8_Nslice_1_CableLim_1, GC_2020_pd_11_Nslice_1_CableLim_1]


# Cable limit 2030 PDsens
GC_2030_pd_5_Nslice_1_CableLim_1 = GridCase(name = 'GC_2030_pd_5_Nslice_1_CableLim_1')
GC_2030_pd_5_Nslice_1_CableLim_1.pd_nominal = 5 # [MW/km2]
GC_2030_pd_5_Nslice_1_CableLim_1.year = '2030'
GC_2030_pd_5_Nslice_1_CableLim_1.cable_limit = 1

GC_2030_pd_8_Nslice_1_CableLim_1 = GridCase(name = 'GC_2030_pd_8_Nslice_1_CableLim_1')
GC_2030_pd_8_Nslice_1_CableLim_1.pd_nominal = 8
GC_2030_pd_8_Nslice_1_CableLim_1.year = '2030'
GC_2030_pd_8_Nslice_1_CableLim_1.cable_limit = 1

GC_2030_pd_11_Nslice_1_CableLim_1 = GridCase(name = 'GC_2030_pd_11_Nslice_1_CableLim_1')
GC_2030_pd_11_Nslice_1_CableLim_1.pd_nominal = 11
GC_2030_pd_11_Nslice_1_CableLim_1.year = '2030'
GC_2030_pd_11_Nslice_1_CableLim_1.cable_limit = 1

GCS_2030_PDsens_Nslice_1_CableLim_1 = CaseStudy(name = 'GCS_2030_PDsens_Nslice_1_CableLim_1')
GCS_2030_PDsens_Nslice_1_CableLim_1.cases = [GC_2030_pd_5_Nslice_1_CableLim_1, GC_2030_pd_8_Nslice_1_CableLim_1, GC_2030_pd_11_Nslice_1_CableLim_1]


# Cable limit 2050 PDsens
GC_2050_pd_5_Nslice_1_CableLim_1 = GridCase(name = 'GC_2050_pd_5_Nslice_1_CableLim_1')
GC_2050_pd_5_Nslice_1_CableLim_1.pd_nominal = 5 # [MW/km2]
GC_2050_pd_5_Nslice_1_CableLim_1.year = '2050'
GC_2050_pd_5_Nslice_1_CableLim_1.cable_limit = 1

GC_2050_pd_8_Nslice_1_CableLim_1 = GridCase(name = 'GC_2050_pd_8_Nslice_1_CableLim_1')
GC_2050_pd_8_Nslice_1_CableLim_1.pd_nominal = 8
GC_2050_pd_8_Nslice_1_CableLim_1.year = '2050'
GC_2050_pd_8_Nslice_1_CableLim_1.cable_limit = 1

GC_2050_pd_11_Nslice_1_CableLim_1 = GridCase(name = 'GC_2050_pd_11_Nslice_1_CableLim_1')
GC_2050_pd_11_Nslice_1_CableLim_1.pd_nominal = 11
GC_2050_pd_11_Nslice_1_CableLim_1.year = '2050'
GC_2050_pd_11_Nslice_1_CableLim_1.cable_limit = 1

GCS_2050_PDsens_Nslice_1_CableLim_1 = CaseStudy(name = 'GCS_2050_PDsens_Nslice_1_CableLim_1')
GCS_2050_PDsens_Nslice_1_CableLim_1.cases = [GC_2050_pd_5_Nslice_1_CableLim_1, GC_2050_pd_8_Nslice_1_CableLim_1, GC_2050_pd_11_Nslice_1_CableLim_1]




# N slice sens
GC_2020_pd_8_sensNslice_1_CableLim_0 = GridCase(name = 'GC_2020_pd_8_sensNslice_1_CableLim_0')
GC_2020_pd_8_sensNslice_1_CableLim_0.pd_nominal = 8
GC_2020_pd_8_sensNslice_1_CableLim_0.N_slices = 1

GC_2020_pd_8_sensNslice_2_CableLim_0 = GridCase(name = 'GC_2020_pd_8_sensNslice_2_CableLim_0')
GC_2020_pd_8_sensNslice_2_CableLim_0.pd_nominal = 8
GC_2020_pd_8_sensNslice_2_CableLim_0.N_slices = 2

GC_2020_pd_8_sensNslice_4_CableLim_0 = GridCase(name = 'GC_2020_pd_8_sensNslice_4_CableLim_0')
GC_2020_pd_8_sensNslice_4_CableLim_0.pd_nominal = 8
GC_2020_pd_8_sensNslice_4_CableLim_0.N_slices = 4

GC_2020_pd_8_sensNslice_8_CableLim_0 = GridCase(name = 'GC_2020_pd_8_sensNslice_8_CableLim_0')
GC_2020_pd_8_sensNslice_8_CableLim_0.pd_nominal = 8
GC_2020_pd_8_sensNslice_8_CableLim_0.N_slices = 8

GCS_2020_pd_8_sensNslice_CableLim_0 = CaseStudy(name = 'GCS_2020_pd_8_sensNslice_CableLim_0')
GCS_2020_pd_8_sensNslice_CableLim_0.cases = [GC_2020_pd_8_sensNslice_1_CableLim_0, GC_2020_pd_8_sensNslice_2_CableLim_0, GC_2020_pd_8_sensNslice_4_CableLim_0, GC_2020_pd_8_sensNslice_8_CableLim_0 ]


GC_2030_pd_8_sensNslice_1_CableLim_0 = GridCase(name = 'GC_2030_pd_8_sensNslice_1_CableLim_0')
GC_2030_pd_8_sensNslice_1_CableLim_0.pd_nominal = 8
GC_2030_pd_8_sensNslice_1_CableLim_0.year = '2030'
GC_2030_pd_8_sensNslice_1_CableLim_0.N_slices = 1

GC_2030_pd_8_sensNslice_2_CableLim_0 = GridCase(name = 'GC_2030_pd_8_sensNslice_2_CableLim_0')
GC_2030_pd_8_sensNslice_2_CableLim_0.pd_nominal = 8
GC_2030_pd_8_sensNslice_2_CableLim_0.year = '2030'
GC_2030_pd_8_sensNslice_2_CableLim_0.N_slices = 2

GC_2030_pd_8_sensNslice_4_CableLim_0 = GridCase(name = 'GC_2030_pd_8_sensNslice_4_CableLim_0')
GC_2030_pd_8_sensNslice_4_CableLim_0.pd_nominal = 8
GC_2030_pd_8_sensNslice_4_CableLim_0.year = '2030'
GC_2030_pd_8_sensNslice_4_CableLim_0.N_slices = 4

GC_2030_pd_8_sensNslice_8_CableLim_0 = GridCase(name = 'GC_2030_pd_8_sensNslice_8_CableLim_0')
GC_2030_pd_8_sensNslice_8_CableLim_0.pd_nominal = 8
GC_2030_pd_8_sensNslice_8_CableLim_0.year = '2030'
GC_2030_pd_8_sensNslice_8_CableLim_0.N_slices = 8

GCS_2030_pd_8_sensNslice_CableLim_0 = CaseStudy(name = 'GCS_2030_pd_8_sensNslice_CableLim_0')
GCS_2030_pd_8_sensNslice_CableLim_0.cases = [GC_2030_pd_8_sensNslice_1_CableLim_0, GC_2030_pd_8_sensNslice_2_CableLim_0, GC_2030_pd_8_sensNslice_4_CableLim_0, GC_2030_pd_8_sensNslice_8_CableLim_0 ]



GC_2050_pd_8_sensNslice_1_CableLim_0 = GridCase(name = 'GC_2050_pd_8_sensNslice_1_CableLim_0')
GC_2050_pd_8_sensNslice_1_CableLim_0.pd_nominal = 8
GC_2050_pd_8_sensNslice_1_CableLim_0.year = '2050'
GC_2050_pd_8_sensNslice_1_CableLim_0.N_slices = 1

GC_2050_pd_8_sensNslice_2_CableLim_0 = GridCase(name = 'GC_2050_pd_8_sensNslice_2_CableLim_0')
GC_2050_pd_8_sensNslice_2_CableLim_0.pd_nominal = 8
GC_2050_pd_8_sensNslice_2_CableLim_0.year = '2050'
GC_2050_pd_8_sensNslice_2_CableLim_0.N_slices = 2

GC_2050_pd_8_sensNslice_4_CableLim_0 = GridCase(name = 'GC_2050_pd_8_sensNslice_4_CableLim_0')
GC_2050_pd_8_sensNslice_4_CableLim_0.pd_nominal = 8
GC_2050_pd_8_sensNslice_4_CableLim_0.year = '2050'
GC_2050_pd_8_sensNslice_4_CableLim_0.N_slices = 4

GC_2050_pd_8_sensNslice_8_CableLim_0 = GridCase(name = 'GC_2050_pd_8_sensNslice_8_CableLim_0')
GC_2050_pd_8_sensNslice_8_CableLim_0.pd_nominal = 8
GC_2050_pd_8_sensNslice_8_CableLim_0.year = '2050'
GC_2050_pd_8_sensNslice_8_CableLim_0.N_slices = 8

GCS_2050_pd_8_sensNslice_CableLim_0 = CaseStudy(name = 'GCS_2050_pd_8_sensNslice_CableLim_0')
GCS_2050_pd_8_sensNslice_CableLim_0.cases = [GC_2050_pd_8_sensNslice_1_CableLim_0, GC_2050_pd_8_sensNslice_2_CableLim_0, GC_2050_pd_8_sensNslice_4_CableLim_0, GC_2050_pd_8_sensNslice_8_CableLim_0 ]


GCS_2020_pd_8_Nslice_1_sensCableLim = CaseStudy(name = 'GCS_2020_pd_8_Nslice_1_sensCableLim')
GCS_2020_pd_8_Nslice_1_sensCableLim.cases = [GC_2020_pd_8_Nslice_1_CableLim_0, GC_2020_pd_8_Nslice_1_CableLim_1]

GCS_2030_pd_8_Nslice_1_sensCableLim = CaseStudy(name = 'GCS_2030_pd_8_Nslice_1_sensCableLim')
GCS_2030_pd_8_Nslice_1_sensCableLim.cases = [GC_2030_pd_8_Nslice_1_CableLim_0, GC_2030_pd_8_Nslice_1_CableLim_1]

GCS_2050_pd_8_Nslice_1_sensCableLim = CaseStudy(name = 'GCS_2050_pd_8_Nslice_1_sensCableLim')
GCS_2050_pd_8_Nslice_1_sensCableLim.cases = [GC_2050_pd_8_Nslice_1_CableLim_0, GC_2050_pd_8_Nslice_1_CableLim_1]



GC_test = GridCase(name = 'GC_test')
GC_test.pd_nominal = 8
GC_test.year = '2020'
GC_test.N_slices = 1
GC_test.cable_limit = 0

GCS_test= CaseStudy(name = 'GCS_test')
GCS_test.cases = [GC_test]

x=1
