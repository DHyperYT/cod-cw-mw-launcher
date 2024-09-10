import tkinter as tk
from tkinter import filedialog, messagebox
import os
import tempfile
import cv2
from PIL import Image, ImageTk
import pygame
import subprocess
import time
import psutil
import webbrowser
import urllib.request
import sys
import pypresence
from tkinter import StringVar, OptionMenu, Button, Label
from tkinter import ttk
import re
import requests

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

class LoadoutEditor:
    PRIMARY_WEAPONS = {
        "Kilo141 (HK433)": "iw8_ar_kilo433",
        "FAL": "iw8_ar_falima",
        "M4A1": "iw8_ar_mike4",
        "FR5.56 (FAMAS)": "iw8_ar_falpha",
        "Oden (ShAK-12)": "iw8_ar_asierra12",
        "M13 (MCX)": "iw8_ar_mcharlie",
        "FNScar17": "iw8_ar_scharlie",
        "Kilo47 (AK-47)": "iw8_ar_akilo47",
        "RAM-7 (Tavor)": "iw8_ar_tango21",
        "Grau (SG552)": "iw8_ar_sierra552",
        "CR 56 AMAX (UNRELEASED)": "iw8_ar_galima",
        "AUG": "iw8_sm_augolf",
        "P90": "iw8_sm_papa90",
        "MP5": "iw8_sm_mpapa5",
        "Uzi": "iw8_sm_uzulu",
        "PP19Bizon": "iw8_sm_beta",
        "MP7": "iw8_sm_mpapa7",
        "Striker45": "iw8_sm_smgolf45",
        "Vector (UNRELEASED)": "iw8_sm_victor",
        "ISO (UNRELEASED)": "iw8_sm_charlie9",
        "Model680": "iw8_sh_romeo870",
        "R9-0": "iw8_sh_dpapa12",
        "725": "iw8_sh_charlie725",
        "Origin12": "iw8_sh_oscar12",
        "VLKRogue": "iw8_sh_mike26",
        "PKM": "iw8_lm_pkilo",
        "SA87": "iw8_lm_lima86",
        "M91 (M240)": "iw8_lm_kilo121",
        "MG34": "iw8_lm_mgolf34",
        "Holger-26 (MG36)": "iw8_lm_mgolf36",
        "BruenMk9 (M249)": "iw8_lm_mkilo3",
        "EBR-14 (M14)": "iw8_sn_golf28",
        "MK2Carbine": "iw8_sn_sbeta",
        "Kar98K": "iw8_sn_kilo98",
        "Bugged EBR-14": "iw8_sn_mike14",
        "Crossbow": "iw8_sn_crossbow",
        "SKS": "iw8_sn_sksierra",
        "Dragunov": "iw8_sn_delta",
        "HDR": "iw8_sn_hdromeo",
        "AX-50": "iw8_sn_alpha50",
        "RiotShield": "iw8_me_riotshield"
    }

    SECONDARY_WEAPONS = {
        "X16 (Glock21)": "iw8_pi_golf21",
        "1911": "iw8_pi_mike1911",
        ".357 (M586)": "iw8_pi_cpapa",
        "M19 (M18)": "iw8_pi_papa320",
        ".50GS (DEagle)": "iw8_pi_decho",
        "Renetti (M9)": "iw8_pi_mike9",
        "PILA": "iw8_la_gromeo",
        "Strela-P (CarlG)": "iw8_la_kgolf",
        "JOKR (Javelin)": "iw8_la_juliet",
        "RPG-7": "iw8_la_rpapa7",
        "Fists": "iw8_fists",
        "CombatKnife": "iw8_knife"
    }

    def __init__(self, master):
        self.master = master
        self.file_path = os.path.join(
            os.getenv('USERPROFILE'), 'Documents', 'Call of Duty Modern Warfare', 'players', 'loadouts.cfg'
        )
        self.weapon_vars = []
        self.setup_gui()
        self.load_loadouts()

    def setup_gui(self):
        self.master.title("Loadout Editor")
        self.master.geometry("650x300")
        self.master.resizable(False, False)

        icon_path = resource_path('icon.ico')
        self.master.iconbitmap(icon_path)
        
        tk.Label(self.master, text="Primary Weapons").grid(row=0, column=0, columnspan=2)
        tk.Label(self.master, text="Secondary Weapons").grid(row=0, column=2, columnspan=2)

        for i in range(10):
            tk.Label(self.master, text=f"Loadout {i+1} Primary Weapon:").grid(row=i+1, column=0)
            primary_var = tk.StringVar()
            secondary_var = tk.StringVar()
            self.weapon_vars.append((primary_var, secondary_var))
            
            primary_menu = ttk.Combobox(
                self.master,
                textvariable=primary_var,
                values=list(self.PRIMARY_WEAPONS.keys()),
                state='readonly'
            )
            primary_menu.grid(row=i+1, column=1)
            primary_menu.current(0)
            
            tk.Label(self.master, text=f"Loadout {i+1} Secondary Weapon:").grid(row=i+1, column=2)
            secondary_menu = ttk.Combobox(
                self.master,
                textvariable=secondary_var,
                values=list(self.SECONDARY_WEAPONS.keys()),
                state='readonly'
            )
            secondary_menu.grid(row=i+1, column=3)
            secondary_menu.current(0)
        
        tk.Button(
            self.master,
            text="Update Loadouts",
            command=self.on_update_loadouts
        ).grid(row=11, column=1, columnspan=2)

    def load_loadouts(self):
        loadouts = self.read_loadouts()
        for i in range(10):
            primary_weapon = loadouts.get(f'Loadout {i+1}', {}).get('Primary', 'None')
            secondary_weapon = loadouts.get(f'Loadout {i+1}', {}).get('Secondary', 'None')
            self.weapon_vars[i][0].set(primary_weapon)
            self.weapon_vars[i][1].set(secondary_weapon)

    def read_loadouts(self):
        loadouts = {}
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    for i in range(10):
                        loadout_key = f'setPrivateLoadout loadouts {i} weaponSetups'
                        primary_match = re.search(f'{loadout_key} 0 weapon (iw8_[^\\s]+)', content)
                        secondary_match = re.search(f'{loadout_key} 1 weapon (iw8_[^\\s]+)', content)
                        
                        primary_weapon_id = primary_match.group(1) if primary_match else None
                        secondary_weapon_id = secondary_match.group(1) if secondary_match else None
                        
                        primary_weapon = next((k for k, v in self.PRIMARY_WEAPONS.items() if v == primary_weapon_id), 'None')
                        secondary_weapon = next((k for k, v in self.SECONDARY_WEAPONS.items() if v == secondary_weapon_id), 'None')
                        
                        loadouts[f'Loadout {i+1}'] = {
                            'Primary': primary_weapon,
                            'Secondary': secondary_weapon
                        }
            except Exception as e:
                print(f"Error reading file: {e}")
        return loadouts

    def save_loadouts(self, loadouts):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                for i in range(10):
                    primary_weapon_id = self.PRIMARY_WEAPONS.get(loadouts[f'Loadout {i+1}']['Primary'], 'iw8_ar_kilo433')
                    secondary_weapon_id = self.SECONDARY_WEAPONS.get(loadouts[f'Loadout {i+1}']['Secondary'], 'iw8_pi_mike1911')
                    
                    file.write(f'setPrivateLoadout loadouts {i} weaponSetups 0 weapon {primary_weapon_id}\n')
                    file.write(f'setPrivateLoadout loadouts {i} weaponSetups 1 weapon {secondary_weapon_id}\n')
                    
        except Exception as e:
            print(f"Error writing file: {e}")

    def on_update_loadouts(self):
        current_loadouts = self.read_loadouts()
        for i in range(10):
            primary_weapon = self.weapon_vars[i][0].get()
            secondary_weapon = self.weapon_vars[i][1].get()
            current_loadouts[f'Loadout {i+1}']['Primary'] = primary_weapon
            current_loadouts[f'Loadout {i+1}']['Secondary'] = secondary_weapon
        self.save_loadouts(current_loadouts)
        
class OperatorEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Operator Editor")
        self.root.resizable(False, False)

        icon_path = resource_path('icon.ico')
        self.root.iconbitmap(icon_path)

        # Data
        self.operators = {
            "Coalition": {
                "default_western": [
                    "Default", "Pararescue1", "Pararescue2", "Pararescue3", "CTFSO1",
                    "CTFSO2", "CTFSO3", "SKSF1", "SKSF2", "SKSF3", "USEF1", "USEF2",
                    "USEF3", "Frogman"
                ],
                "ghost_western": [
                    "Jawbone", "Mandible", "LastBreath", "Ghosted", "DarkVision",
                    "Reckoner", "Frogman", "Classic"
                ],
                "murphy_western": [
                    "Deployment", "DesertRat", "Seafarer", "Marshland", "GreyWolf",
                    "NightRaid", "Security", "LaMuerte", "Solstice", "SAS", "InkedInfil",
                    "Ripcord", "Valor", "Vigilance", "MightyArse"
                ],
                "charly_western": [
                    "Patrol", "Warden", "Scout", "Clouded", "Tundra", "Grassroots",
                    "CarbonAsh", "SAS", "Huntress", "AngelOfD", "TacticalH", "Sinister"
                ],
                "otter_western": [
                    "JungleRaid", "Swampland", "Woodland", "Sandstorm", "Desert",
                    "SAS", "Urban", "CrewExpend", "IPinchBack", "Jungle", "TF141",
                    "DemoExpert", "SnowDrift", "Irradiated"
                ],
                "dday_western": [
                    "OpenSeason", "SageBrush", "Fall", "ArcticOps", "Nightmare", 
                    "Buckshot", "ClippedIn", "DeepPockets", "Nightshift", "DemonDogs",
                    "QuickDraw", "Tailgate", "TrueVictory", "CamoCroc", "Scarecrow",
                    "Bushranger", "LoneStar", "BorderWar"
                ],
                "alice_western": [
                    "Tactical", "Maplewood", "Mechanic", "Muddin", "SmartTactical",
                    "GreyMatter", "DownRange", "StreetSmart", "DemonDogs", "BossLady",
                    "Rime"
                ],
                "raines_western": [
                    "Raider", "StuntDouble", "Touchdown", "Mariner", "RoadRage",
                    "BuffaloHunter", "DarkPacifier", "Evergreen", "DemonDogs", "Outback",
                    "Tactical", "Bunyan"
                ],
                "crowfoot_western": [
                    "Skin2", "Skin3", "Tracker", "GoodMedicine", "ColdCreek", "Scarecrow"
                ],
                "domino_western": [
                    "Commando", "ColdTimber", "Jungle", "Wetworks", "GreenMamba",
                    "UrbanAssault", "Hardened", "BattleReady", "WarcomDomino", "DesertOps",
                    "707thSMB", "SecurityDetail", "SpyGames"
                ],
                "golem_western": [
                    "JungleTerror", "NightRaid", "CounterTerror", "WinterWarrior",
                    "SpectralAss", "Black&Blue", "Minimalist", "Stuntman", "WarcomGolem",
                    "SwampFever", "Foliage", "IceCold", "WinterWarrior2", "JunkPile",
                    "BlackForest"
                ],
                "zedra_western": [
                    "DeathDealer", "ChemDivision", "DesertWork", "GreenDust", "ForestOps",
                    "DigitalDark", "DuneHunter", "Quick-witted", "Valkyrie"
                ],
                "wyatt_western": [
                    "RaidGear", "Remnant", "Sprinter", "UrbanHip", "Digital", "Warcom",
                    "GoingGray", "Run&Gun", "Desperado", "Commander", "WarPig", "Outback",
                    "TheWoodsman", "TheBagger"
                ],
                "ronin_western": ["LoneDragon"],
                "alex_western": [
                    "Indomitable", "LuckyStreak", "BackForMore", "HardWired",
                    "Eliminator", "Automation"
                ],
                "lynch_western": ["Raider"]
            },
            "Allegiance": {
                "default_eastern": ["Default"],
                "minotavr_eastern": [
                    "FullyLoaded", "SunsOut", "BeachDay", "ArmoredUp", "Tactical",
                    "Commando", "AllBusiness", "Spetsnaz", "Smoke", "SmokingOnTheJob",
                    "GunsOut", "Hidden", "Scales", "SquadLeader", "Valentaur"
                ],
                "bale_eastern": [
                    "Spetz", "Riot", "TwilightP", "UrbanCasualty", "Bleached",
                    "Sokoly", "TaskForce", "Brawler", "SnowForce", "Spetsnaz",
                    "AgentOrange", "Darkness", "Protectorate", "StoneFaced"
                ],
                "rodion_eastern": [
                    "HollywoodH", "Gungho", "NightRaid", "Recon", "WinterWear",
                    "HeavyDuty", "CasualFriday", "ShortSummers", "BurgerTown",
                    "Spetsnaz", "Incognito", "Infiltration", "Seaweed", "DeepSnow"
                ],
                "spetsnaz_eastern": ["Fixer"],
                "metalghost_eastern": [
                    "MetalPhantom", "Tombstone"
                ],
                "azur_eastern": [
                    "Smoked", "GreyedOut", "UrbanAssault", "Security", "Sheik",
                    "Nightshade", "DesertBandit", "SunBleached", "DuneBreaker",
                    "Jackals", "ArmsDealer", "Brawler", "RedReptile", "GreyMatter",
                    "BrothersKeeper"
                ],
                "grinch_eastern": [
                    "WarFace", "Wayward", "Feral", "JackalsGrinch", "Overgrowth",
                    "Webfoot", "Armadillo", "Bog", "MuddyWaters", "AllGhilliedUp",
                    "BloodInTheWater", "Nightfang"
                ],
                "zane_eastern": [
                    "Crusade", "Shades", "FatherTreason", "ZebraPrint", "Glitch",
                    "Vigilante", "Gbosa Green", "GreyedOut", "Polarized", "Striker",
                    "Jackals", "PepperDonRed", "MonsoonSeason", "Militant", "HoneyBadger"
                ],
                "yegor_eastern": [
                    "Cerulean", "Emerald", "Ruby", "OutOfTown", "SundayBest",
                    "Athleisure", "SuperStar", "BlackDrab", "Chimera", "TrackStar",
                    "NightLife", "FishBowl", "ChilledOut", "CoolBlue", "Commuter",
                    "Drawstring", "HardLabor", "ThiefInLaw", "ServiceRecord"
                ],
                "kreuger_eastern": [
                    "Phantom", "Shrouded", "SilentSigma", "Bandit", "Plague",
                    "MarshDemon", "Chimera", "Reaper", "Chemist", "Hazmat",
                    "ChemicalWarfare", "Waster", "Firestarter"
                ],
                "syd_eastern": [
                    "Mantis", "Embedded", "Judge", "Mariner", "Sahara", "Bluejacket",
                    "Chimera", "Thunderbird", "WoodlandCover", "Wetfoot", "Marathon"
                ],
                "iskra_eastern": ["Saboteur"]
            }
        }

        self.skins = {
            "default_western": [274, 816, 817, 818, 819, 820, 821, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836],
            "ghost_western": [136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153],
            "murphy_western": [154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171],
            "charly_western": [172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189],
            "otter_western": [190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207],
            "dday_western": [208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225],
            "alice_western": [226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243],
            "raines_western": [244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261],
            "crowfoot_western": [262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279],
            "domino_western": [280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297],
            "golem_western": [298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315],
            "zedra_western": [316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333],
            "wyatt_western": [334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351],
            "ronin_western": [352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369],
            "alex_western": [370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387],
            "lynch_western": [388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405],
            "default_eastern": [406],
            "minotavr_eastern": [407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424],
            "bale_eastern": [425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442],
            "rodion_eastern": [443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460],
            "spetsnaz_eastern": [461],
            "metalghost_eastern": [462, 463],
            "azur_eastern": [464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481],
            "grinch_eastern": [482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499],
            "zane_eastern": [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517],
            "yegor_eastern": [518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535],
            "kreuger_eastern": [536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553],
            "syd_eastern": [554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571],
            "iskra_eastern": [572]
        }

        self.finishing_moves = {
            "Bag'Em": 107,
            "ChipShot": 105,
            "CrickInTheNeck": 104,
            "FangsOut": 102,
            "Gutted": 93,
            "HelloStranger": 97,
            "Low Rise": 92,
            "Perforate": 94,
            "SpinCycle": 98,
            "ThreeStrikes": 91,
            "TopDog": 95,
            "UV09": 99,
            "UV10 (BushLeague)": 100,
            "UV11 (Karambit2)": 101,
            "UV13 (Payback)": 103,
            "UV16 (Bag'Em2)": 106,
            "WatchThis": 96
        }

        self.skin_name_to_id = {name: skin_id for category, skin_ids in self.skins.items() for name in self.operators.get(category, {}).get(category, []) for skin_id in skin_ids}

        self.create_ui()

    def create_ui(self):
        coalition_frame = tk.Frame(self.root)
        coalition_frame.grid(row=0, column=0, padx=10, pady=10)
        allegiance_frame = tk.Frame(self.root)
        allegiance_frame.grid(row=0, column=1, padx=10, pady=10)

        # Coalition operators
        coalition_label = tk.Label(coalition_frame, text="Select Coalition Operator")
        coalition_label.pack(padx=5, pady=5)

        self.coalition_operator_combobox = ttk.Combobox(coalition_frame, values=list(self.operators["Coalition"].keys()))
        self.coalition_operator_combobox.pack(padx=5, pady=5)
        self.coalition_operator_combobox.bind("<<ComboboxSelected>>", self.update_coalition_skins)

#        self.coalition_skin_combobox = ttk.Combobox(coalition_frame)
#        self.coalition_skin_combobox.pack(padx=5, pady=5)

        self.coalition_finishing_move_combobox = ttk.Combobox(coalition_frame, values=list(self.finishing_moves.keys()))
        self.coalition_finishing_move_combobox.pack(padx=5, pady=5)

        # Allegiance operators
        allegiance_label = tk.Label(allegiance_frame, text="Select Allegiance Operator")
        allegiance_label.pack(padx=5, pady=5)

        self.allegiance_operator_combobox = ttk.Combobox(allegiance_frame, values=list(self.operators["Allegiance"].keys()))
        self.allegiance_operator_combobox.pack(padx=5, pady=5)
        self.allegiance_operator_combobox.bind("<<ComboboxSelected>>", self.update_allegiance_skins)

#        self.allegiance_skin_combobox = ttk.Combobox(allegiance_frame)
#        self.allegiance_skin_combobox.pack(padx=5, pady=5)

        self.allegiance_finishing_move_combobox = ttk.Combobox(allegiance_frame, values=list(self.finishing_moves.keys()))
        self.allegiance_finishing_move_combobox.pack(padx=5, pady=5)

        save_button = tk.Button(self.root, text="Save", command=self.save_selection)
        save_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def get_skin_name_from_id(self, skin_id):
        for name, id_ in self.skin_name_to_id.items():
            if id_ == skin_id:
                return name
        return str(skin_id)

    def update_coalition_skins(self, event):
        operator = self.coalition_operator_combobox.get()
        if operator in self.operators["Coalition"]:
            skin_ids = self.skins.get(operator, [])
            skin_names = [self.get_skin_name_from_id(skin_id) for skin_id in skin_ids]

    def update_allegiance_skins(self, event):
        operator = self.allegiance_operator_combobox.get()
        if operator in self.operators["Allegiance"]:
            skin_ids = self.skins.get(operator, [])
            skin_names = [self.get_skin_name_from_id(skin_id) for skin_id in skin_ids]

#    def get_selected_coalition_skin_id(self):
#        selected_skin = self.coalition_skin_combobox.get()
#        return self.skin_name_to_id.get(selected_skin, None)

#    def get_selected_allegiance_skin_id(self):
# doesnt work        selected_skin = self.allegiance_skin_combobox.get()
#        return self.skin_name_to_id.get(selected_skin, None)

    def save_selection(self):
        file_path = os.path.expandvars(r'%USERPROFILE%\Documents\Call of Duty Modern Warfare\players\operators.cfg')
        
        selected_coalition_operator = self.coalition_operator_combobox.get()
# doesnt work        selected_coalition_skin_id = self.get_selected_coalition_skin_id()
        selected_coalition_finishing_move = self.coalition_finishing_move_combobox.get()
        
        selected_allegiance_operator = self.allegiance_operator_combobox.get()
# doesnt work        selected_allegiance_skin_id = self.get_selected_allegiance_skin_id()
        selected_allegiance_finishing_move = self.allegiance_finishing_move_combobox.get()
        
        with open(file_path, 'w') as file:
            if selected_coalition_operator:
                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operators 0 {selected_coalition_operator}\n")
#doesnt work            if selected_coalition_skin_id:
#doesnt work                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operatorCustomization {selected_coalition_operator} skin {selected_coalition_skin_id}\n")
            if selected_coalition_finishing_move:
                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operatorCustomization {selected_coalition_operator} execution {self.finishing_moves.get(selected_coalition_finishing_move, '')}\n")
            
            if selected_allegiance_operator:
                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operators 1 {selected_allegiance_operator}\n")
# doesnt work           if selected_allegiance_skin_id:
#                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operatorCustomization {selected_allegiance_operator} skin {selected_allegiance_skin_id}\n")
            if selected_allegiance_finishing_move:
                file.write(f"setPrivateLoadoutsPlayerData customizationSetup operatorCustomization {selected_allegiance_operator} execution {self.finishing_moves.get(selected_allegiance_finishing_move, '')}\n")
    
class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.rpc = None
        self.root.title("Call of Duty Launcher")
        self.root.geometry("960x540")
        self.root.resizable(False, False)

        icon_path = resource_path('icon.ico')
        self.root.iconbitmap(icon_path)

        pygame.mixer.init()
        self.muted = False
        self.play_music(resource_path("mw.mp3"))

        self.overlay_frame = tk.Frame(root, bg="#000000", bd=5)
        self.overlay_frame.place(relwidth=1, relheight=1)

        self.sidebar = tk.Frame(self.overlay_frame, width=300, bg="#000000", height=600, relief="raised", borderwidth=2)
        self.sidebar.pack(side="left", fill="y")

        self.button_frame = tk.Frame(self.sidebar, bg="#000")
        self.button_frame.pack(pady=10)

        self.mw_img = Image.open(resource_path("mw.png"))
        self.mw_img = self.mw_img.resize((60, 60), Image.Resampling.LANCZOS)
        self.mw_photo = ImageTk.PhotoImage(self.mw_img)
        self.mw_button = tk.Button(self.button_frame, image=self.mw_photo, command=self.show_mw_launcher, bg="#000", bd=0)
        self.mw_button.pack(pady=10)

        self.cw_img = Image.open(resource_path("cw.png"))
        self.cw_img = self.cw_img.resize((60, 60), Image.Resampling.LANCZOS)
        self.cw_photo = ImageTk.PhotoImage(self.cw_img)
        self.cw_button = tk.Button(self.button_frame, image=self.cw_photo, command=self.show_cw_launcher, bg="#000", bd=0)
        self.cw_button.pack(pady=10)

        self.mw2_img = Image.open(resource_path("mw2.png"))
        self.mw2_img = self.mw2_img.resize((60, 60), Image.Resampling.LANCZOS)
        self.mw2_photo = ImageTk.PhotoImage(self.mw2_img)
        self.mw2_button = tk.Button(self.button_frame, image=self.mw2_photo, command=self.show_mw2_launcher, bg="#000", bd=0)
        self.mw2_button.pack(pady=10)
        
        self.settings_img = Image.open(resource_path("settings.png"))
        self.settings_img = self.settings_img.resize((50, 50), Image.Resampling.LANCZOS)
        self.settings_photo = ImageTk.PhotoImage(self.settings_img)
        self.settings_button = tk.Button(self.sidebar, image=self.settings_photo, command=self.open_settings, bg="#000", bd=0)
        self.settings_button.pack(side="bottom", pady=10)

        self.mute_img = Image.open(resource_path("mute.png"))
        self.mute_img = self.mute_img.resize((50, 50), Image.Resampling.LANCZOS)
        self.mute_photo = ImageTk.PhotoImage(self.mute_img)
        self.mute_button = tk.Button(self.sidebar, image=self.mute_photo, command=self.toggle_mute, bg="#000", bd=0)
        self.mute_button.pack(side="bottom", pady=10)

        self.git_img = Image.open(resource_path("git.png"))
        self.git_img = self.git_img.resize((40, 40), Image.Resampling.LANCZOS)
        self.git_photo = ImageTk.PhotoImage(self.git_img)
        self.git_button = tk.Button(self.sidebar, image=self.git_photo, command=self.open_github, bg="#000", bd=0)
        self.git_button.pack(side="bottom", pady=10)

        self.main_frame = tk.Frame(self.overlay_frame, width=700, height=600, bg="#000000")
        self.main_frame.pack(side="right", fill="both", expand=True)
        self.video_label = tk.Label(self.main_frame)
        self.video_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.mw_video_path = resource_path("mw.mp4")
        self.cw_video_path = resource_path("cw.mp4")
        self.mw2_video_path = resource_path("mw2.mp4")

        self.mw_cap = None
        self.cw_cap = None
        self.mw2_cap = None
        self.current_launcher = None
        self.launch_button = None
        self.dll_button = None

        self.current_mission_label = tk.Label(self.main_frame, text="Current Campaign Missions", bg="#000", fg="white", font=("Arial", 12))
        self.save1_label = tk.Label(self.main_frame, text="", bg="#000", fg="white", font=("Arial", 12))
        self.save2_label = tk.Label(self.main_frame, text="", bg="#000", fg="white", font=("Arial", 12))
        self.save3_label = tk.Label(self.main_frame, text="", bg="#000", fg="white", font=("Arial", 12))

        self.hide_mission_labels()

        self.initialize_rpc()
        self.show_mw_launcher()
        
    def is_game_running(self, process_name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                return True
        return False

    def initialize_rpc(self):
        if any(proc.name() == "Discord.exe" for proc in psutil.process_iter()):
            try:
                self.rpc = pypresence.Presence(client_id='779362523388313612')
                self.rpc.connect()
                self.update_rpc("Idle", "In the Modern Warfare Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
            except Exception as e:
                print(f"Failed to initialize RPC: {e}")
        else:
            print("Discord is not running. Skipping RPC initialization.")
            self.rpc = None

    def update_rpc(self, state, details, button_label, button_url):
        if self.rpc:
            try:
                self.rpc.update(
                    state=state,
                    details=details,
                    large_image="icon1",
                    buttons=[{"label": button_label, "url": button_url}]
                )
            except Exception as e:
                print(f"Failed to update RPC: {e}")
        else:
            print("RPC not initialized, skipping update.")

    def play_music(self, music_file):
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)

    def show_mw_launcher(self):
        if self.current_launcher == 'mw':
            return

        self.current_launcher = 'mw'
        if self.cw_cap:
            self.cw_cap.release()
        if self.mw2_cap:
            self.mw2_cap.release()

        self.play_video(self.mw_video_path, 'mw')
        self.play_music(resource_path("mw.mp3"))

        if self.launch_button:
            self.launch_button.destroy()

        self.launch_button = tk.Button(self.main_frame, text="LAUNCH", command=self.launch_mw_game, bg="#000", fg="white", font=("Impact", 20))
        self.launch_button.pack(pady=250)

        if self.dll_button:
            self.dll_button.destroy()

        self.dll_button = tk.Button(self.main_frame, text="Download DLL", command=self.download_mw_dll, bg="#FF4500", fg="white", font=("Arial", 12))
        self.dll_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

        if not hasattr(self, 'weapon_button') or not self.weapon_button.winfo_ismapped():
            self.weapon_button = tk.Button(self.main_frame, text="Weapon Editor (autoexec.cfg with loadouts.cfg needed)", command=self.open_weapon_editor, bg="#000", fg="white", font=("Arial", 12))
            self.weapon_button.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-60)

        if not hasattr(self, 'editor_button') or not self.editor_button.winfo_ismapped():
            self.editor_button = tk.Button(self.main_frame, text="Operator Editor (autoexec.cfg with operators.cfg needed)", command=self.open_loadout_editor, bg="#000", fg="white", font=("Arial", 12))
            self.editor_button.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-100)

        if not hasattr(self, 'download_button') or not self.download_button.winfo_ismapped():
            self.download_button = tk.Button(self.main_frame, text="Download .cfg Files", command=self.download_config_files, bg="#000", fg="white", font=("Arial", 12))
            self.download_button.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-140)

        if not hasattr(self, 'gsc_button') or not self.download_button.winfo_ismapped():
            self.gsc_button = tk.Button(self.main_frame, text="Add unreleased gun support", command=self.download_gscbin, bg="#000", fg="white", font=("Arial", 12))
            self.gsc_button.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-180)

        if not hasattr(self, 'delete_button') or not self.delete_button.winfo_ismapped():
            self.delete_button = tk.Button(self.main_frame, text="Load editor changes (DELETES YOUR SAVED DATA)", command=self.delete_inventory_file, bg="#000", fg="white", font=("Arial", 12))
            self.delete_button.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-20)

        self.hide_mission_labels()
        if hasattr(self, 'koala_button'):
            self.koala_button.place_forget()
        if hasattr(self, 'greenluma_button'):
            self.greenluma_button.place_forget()
        if hasattr(self, 'guide_button'):
            self.guide_button.place_forget()


        self.update_rpc("Idle", "In the Modern Warfare Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")

    def show_cw_launcher(self):
        if self.current_launcher == 'cw':
            return

        self.current_launcher = 'cw'
        if self.mw_cap:
            self.mw_cap.release()
        if self.mw2_cap:
            self.mw2_cap.release()
        

        self.play_video(self.cw_video_path, 'cw')
        self.play_music(resource_path("cw.mp3"))

        if self.launch_button:
            self.launch_button.destroy()

        self.launch_button = tk.Button(self.main_frame, text="LAUNCH", command=self.launch_cw_game, bg="#000", fg="white", font=("Impact", 20))
        self.launch_button.pack(pady=250)

        if self.dll_button:
            self.dll_button.destroy()

        self.dll_button = tk.Button(self.main_frame, text="Download DLL", command=self.download_cw_dll, bg="#FF4500", fg="white", font=("Arial", 12))
        self.dll_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

        if hasattr(self, 'editor_button'):
            self.editor_button.place_forget()
        if hasattr(self, 'weapon_button'):
            self.weapon_button.place_forget()
        if hasattr(self, 'download_button'):
            self.download_button.place_forget()
        if hasattr(self, 'delete_button'):
            self.delete_button.place_forget()
        if hasattr(self, 'gsc_button'):
            self.gsc_button.place_forget()
        if hasattr(self, 'koala_button'):
            self.koala_button.place_forget()
        if hasattr(self, 'greenluma_button'):
            self.greenluma_button.place_forget()
        if hasattr(self, 'guide_button'):
            self.guide_button.place_forget()

        self.update_mission_display()
        self.show_mission_labels()

        self.update_rpc("Idle", "In the Black Ops Cold War Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")

    def on_enter(self, event):
        event.widget.config(bg='#76d22d')

    def on_leave(self, event):
        event.widget.config(bg='#656a61')
        
    def show_mw2_launcher(self):
        if self.current_launcher == 'mw2':
            return

        self.current_launcher = 'mw2'

        if hasattr(self, 'mw_cap') and self.mw_cap:
            self.mw_cap.release()
        if hasattr(self, 'cw_cap') and self.cw_cap:
            self.cw_cap.release()

        if hasattr(self, 'mw2_video_path') and self.mw2_video_path:
            self.play_video(self.mw2_video_path, 'mw2')
            
        self.play_music(resource_path("mw2.mp3"))

        if self.launch_button:
            self.launch_button.destroy()

        self.launch_button = tk.Button(self.main_frame, text="LAUNCH MWII CAMPAIGN", command=self.launch_mw2_game, bg="#656a61", fg="white", font=("Impact", 20))
        self.launch_button.place(x=300, y=380)
        self.launch_button.bind("<Enter>", self.on_enter)
        self.launch_button.bind("<Leave>", self.on_leave)

        if hasattr(self, 'dll_button'):
            self.dll_button.destroy()

        self.dll_button = tk.Button(self.main_frame, text="DOWNLOAD MWII CAMPAIGN", command=self.download_mw2c, bg="#656a61", fg="white", font=("Arial", 12))
        self.dll_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
        self.dll_button.bind("<Enter>", self.on_enter)
        self.dll_button.bind("<Leave>", self.on_leave)

        self.greenluma_button = tk.Button(self.main_frame, text="Download Greenluma", command=self.download_greenluma, bg="#656a61", fg="white", font=("Arial", 12))
        self.greenluma_button.place(relx=0.5, rely=1.0, anchor="s", x=0, y=-20)
        self.greenluma_button.bind("<Enter>", self.on_enter)
        self.greenluma_button.bind("<Leave>", self.on_leave)

        self.koala_button = tk.Button(self.main_frame, text="Install Koalageddon", command=self.download_koala, bg="#656a61", fg="white", font=("Arial", 12))
        self.koala_button.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-20)
        self.koala_button.bind("<Enter>", self.on_enter)
        self.koala_button.bind("<Leave>",self. on_leave)

        self.guide_button = tk.Button(self.main_frame, text="INSTALL GUIDE", command=self.show_guide, bg="#656a61", fg="white", font=("Arial", 14))
        self.guide_button.place(relx=0.0, rely=0.0, anchor="nw", x=20, y=2)
        self.guide_button.bind("<Enter>", self.on_enter)
        self.guide_button.bind("<Leave>", self.on_leave)
        
        if hasattr(self, 'editor_button'):
            self.editor_button.place_forget()
        if hasattr(self, 'weapon_button'):
            self.weapon_button.place_forget()
        if hasattr(self, 'download_button'):
            self.download_button.place_forget()
        if hasattr(self, 'delete_button'):
            self.delete_button.place_forget()
        if hasattr(self, 'gsc_button'):
            self.gsc_button.place_forget()

        self.hide_mission_labels()
        self.update_rpc("Idle", "In the Modern Warfare II Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")

    def hide_mission_labels(self):
        self.current_mission_label.place_forget()
        self.save1_label.place_forget()
        self.save2_label.place_forget()
        self.save3_label.place_forget()

    def show_mission_labels(self):
        self.current_mission_label.place(x=10, y=420)
        self.save1_label.place(x=10, y=450)
        self.save2_label.place(x=10, y=480)
        self.save3_label.place(x=10, y=510)   

    def update_mission_display(self):
        self.mission_map = {
            'cp_rus_amerika': 'Redlight, Greenlight',
            'cp_rus_yamantau': 'Echoes of a Cold War',
            'cp_ger_hub_post_yamantau': 'Safehouse: Lubyanka Briefing',
            'cp_rus_kgb': 'Desperate Measures',
            'cp_takedown': 'Nowhere Left to Run',
            'cp_ger_hub': 'CIA Safehouse E9',
            'cp_nam_armada': 'Fracture Jaw',
            'cp_ger_hub_post_armada': 'Safehouse: East Berlin Briefing',
            'cp_ger_stakeout': 'Brick in the Wall',
            'cp_sidemission_takedown': 'Operation Chaos',
            'cp_sidemission_tundra': 'Operation Red Circus',
            'cp_ger_hub_post_kgb': 'Safehouse: Cuba Briefing',
            'cp_nic_revolucion': 'End of the Line',
            'cp_ger_hub_post_cuba': 'Interrogation',
            'cp_nam_prisoner': 'Break on Through',
            'cp_ger_hub8': 'Identity Crisis',
            'cp_rus_siege': 'The Final Countdown',
            'cp_rus_duga': 'Ashes to Ashes',
        }

        save1_mission = self.get_mission_from_save_file('cp_savegame.cgp')
        save2_mission = self.get_mission_from_save_file('cp_savegame_1.cgp')
        save3_mission = self.get_mission_from_save_file('cp_savegame_2.cgp')

        self.save1_label.config(text=f"Save 1: {save1_mission}")
        self.save2_label.config(text=f"Save 2: {save2_mission}")
        self.save3_label.config(text=f"Save 3: {save3_mission}")


    def get_mission_from_save_file(self, save_file):
        save_directory = os.path.join(os.getenv('USERPROFILE'), 'Documents', 'Call Of Duty Black Ops Cold War', 'player')
        save_file_path = os.path.join(save_directory, save_file)

        try:
            with open(save_file_path, 'rb') as file:
                first_line = file.readline().decode('utf-8', errors='ignore')

                for mission_id in self.mission_map:
                    if mission_id in first_line:
                        return self.mission_map[mission_id]

            return "No active mission"
        except Exception as e:
            return "Error"

    def open_loadout_editor(self):
        self.update_rpc("Editing Operators", "In the Modern Warfare Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
        editor_window = tk.Toplevel(self.root)
        OperatorEditor(editor_window)

    def open_weapon_editor(self):
        self.update_rpc("Editing Weapons", "In the Modern Warfare Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
        editor_window = tk.Toplevel(self.root)
        LoadoutEditor(editor_window)

    def play_video(self, video_path, launcher_type):
        if launcher_type == 'mw':
            self.mw_cap = cv2.VideoCapture(video_path)
            self.update_video(self.mw_cap)
        elif launcher_type == 'cw':
            self.cw_cap = cv2.VideoCapture(video_path)
            self.update_video(self.cw_cap)
        elif launcher_type == 'mw2':
            self.mw2_cap = cv2.VideoCapture(video_path)
            self.update_video(self.mw2_cap)

    def update_video(self, cap):
        if cap is not None:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (960, 540))
                img = ImageTk.PhotoImage(Image.fromarray(frame))
                self.video_label.config(image=img)
                self.video_label.image = img
                self.root.after(10, lambda: self.update_video(cap))
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.update_video(cap)

    def load_game_path(self):
        temp_dir = tempfile.gettempdir()
        path_file = os.path.join(temp_dir, f"cod_{self.current_launcher}_path.txt")
        if os.path.exists(path_file):
            with open(path_file, 'r') as file:
                return file.read().strip()
        return ""

    def save_game_path(self, path):
        temp_dir = tempfile.gettempdir()
        path_file = os.path.join(temp_dir, f"cod_{self.current_launcher}_path.txt")
        with open(path_file, 'w') as file:
            file.write(path)

    def open_settings(self):
        new_path = filedialog.askdirectory(title="Select Game Folder (Choose Steam folder for MW2)")
        if new_path:
            if self.current_launcher == 'mw':
                exe_path = os.path.join(new_path, "game_dx12_ship_replay.exe")
                if os.path.exists(exe_path):
                    self.save_game_path(new_path)
                    messagebox.showinfo("Path Saved", "Modern Warfare path has been saved.")
                else:
                    download = messagebox.askyesno("Executable Not Found", "Game not found in the selected path. Do you want to download it?")
                    if download:
                        webbrowser.open("https://gofile.io/d/r4XRqA")
            elif self.current_launcher == 'cw':
                exe_path = os.path.join(new_path, "BlackOpsColdWar.exe")
                if os.path.exists(exe_path):
                    self.save_game_path(new_path)
                    messagebox.showinfo("Path Saved", "Black Ops Cold War path has been saved.")
                else:
                    download = messagebox.askyesno("Executable Not Found", "Game not found in the selected path. Do you want to download it?")
                    if download:
                        webbrowser.open("https://gofile.io/d/s9r66f")
            elif self.current_launcher == 'mw2':
                exe_path = os.path.join(new_path, "Steam.exe")
                if os.path.exists(exe_path):
                    self.save_game_path(new_path)
                    messagebox.showinfo("Path Saved", "Steam path has been saved.")
                else:
                    download = messagebox.showinfo("Steam Not Found", "Steam not found in the selected path. Please download Steam.")

    def launch_mw_game(self):
        game_path = self.load_game_path()
        if game_path:
            exe_path = os.path.join(game_path, "game_dx12_ship_replay.exe")
            if os.path.exists(exe_path):
                self.pause_music()
                subprocess.Popen(exe_path, cwd=game_path)
                self.update_rpc("Playing", "Modern Warfare", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
                self.wait_for_process_termination("game_dx12_ship_replay.exe")
                self.toggle_mute()
                self.resume_music() 
                self.update_rpc("Just finished playing", "In the Modern Warfare Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
            else:
                download = messagebox.askyesno("Executable Not Found", "Game not found in the selected path. Do you want to download it?")
                if download:
                    webbrowser.open("https://gofile.io/d/r4XRqA")
        else:
            messagebox.showerror("Error", "Game path not set. Please set the game path in Settings.")

    def launch_cw_game(self):
        game_path = self.load_game_path()
        if game_path:
            exe_path = os.path.join(game_path, "BlackOpsColdWar.exe")
            if os.path.exists(exe_path):
                self.pause_music()
                subprocess.Popen(exe_path, cwd=game_path)
                self.update_rpc("Playing", "Black Ops Cold War", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
                self.wait_for_process_termination("BlackOpsColdWar.exe")
                self.toggle_mute() 
                self.resume_music()
                self.update_rpc("Just finished playing", "In the Black Ops Cold War Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
                self.update_mission_display()
            else:
                download = messagebox.askyesno("Executable Not Found", "Game not found in the selected path. Do you want to download it?")
                if download:
                    webbrowser.open("https://gofile.io/d/s9r66f")
        else:
            messagebox.showerror("Error", "Game path not set. Please set the game path in Settings.")

    def launch_mw2_game(self):
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == 'Steam.exe':
                process.kill()
                messagebox.showinfo("Steam", "Steam has been closed.")
                break
            
        game_path = self.load_game_path()
        if game_path:
            messagebox.showinfo("WARNING", "PLEASE BE AWARE THAT PROCEEDING WILL GET YOU SHADOWBANNED FROM WZ, MWII, MWIII, AND BO6 FOR A WEEK.")
            messagebox.showinfo("READ", "Press Yes in the next window and open the game from Library. If it stops working download Greenluma again.")
            exe_path = os.path.join(game_path, "DllInjector.exe")
            if os.path.exists(exe_path):
                self.pause_music()
                subprocess.Popen(exe_path, cwd=game_path)
                self.update_rpc("Playing Campaign", "Modern Warfare II", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")
                self.wait_for_process_termination("DLLInjector.exe")
                self.toggle_mute()
                self.resume_music() 
                self.update_rpc("Just finished playing", "In the Modern Warfare II Menu", "GitHub", "https://github.com/DHyperYT/cod-cw-mw-launcher/")

            else:
                download = messagebox.showinfo("Greenluma Not Found", "Greenluma not found in the selected path. Press Download Greenluma to download it.")
     
    def toggle_mute(self):
        if self.muted:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.muted = not self.muted

    def wait_for_process_termination(self, process_name):
        while any(proc.name() == process_name for proc in psutil.process_iter()):
            time.sleep(1)

    def pause_music(self):
        if not self.muted:
            pygame.mixer.music.pause()

    def resume_music(self):
        if not self.muted:
            pygame.mixer.music.unpause()

    def show_guide(self):
        messagebox.showinfo("Install Guide", 
            "1. Press the settings icon and choose your Steam path.\n"
            "2. Download and install COD HQ from Steam (WARZONE NOT NEEDED).\n"
            "3. Install MWII Campaign and extract the rar at the root folder of COD HQ.\n"
            "4. (Its a good idea to add an exclusion to your Steam folder in your antivirus before this) Press Download Greenluma.\n"
            "5. Press Install Koalageddon and finish the setup.\n"
            "6. Run Koalageddon and select Steam -> Install platform integrations.\n"
            "7. Come back to this launcher and press Launch."
        )
        
    def download_mw_dll(self):
        game_path = self.load_game_path()
        if game_path:
            dll_url = "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/discord_game_sdk%20(1).dll"
            dll_path = os.path.join(game_path, "discord_game_sdk.dll")
            urllib.request.urlretrieve(dll_url, dll_path)
            messagebox.showinfo("DLL Downloaded", "DLL installed successfully.")
        else:
            messagebox.showerror("Error", "Game path not set. Please set the game path in Settings.")

    def download_cw_dll(self):
        game_path = self.load_game_path()
        if game_path:
            dll_url = "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/discord_game_sdk.dll"
            dll_path = os.path.join(game_path, "discord_game_sdk.dll")
            urllib.request.urlretrieve(dll_url, dll_path)
            messagebox.showinfo("DLL Downloaded", "DLL installed successfully.")
        else:
            messagebox.showerror("Error", "Game path not set. Please set the game path in Settings.")

    def download_mw2c(self):
        messagebox.showinfo("READ THIS", "First install COD HQ from Steam and then move sp22 to its root folder.")
        webbrowser.open("https://qiwi.gg/file/hfqJ6031-sp22GameDrive")

    def open_github(self):
        webbrowser.open("https://github.com/DHyperYT/cod-cw-mw-launcher/")

    def delete_inventory_file(self):
        file_path = os.path.join(os.getenv('USERPROFILE'), 'Documents', 'Call of Duty Modern Warfare', 'players', 'inventory.json')
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                messagebox.showinfo("File Deleted", "inventory.json has been deleted.")
            else:
                messagebox.showwarning("File Not Found", "inventory.json does not exist.")
        except Exception:
            messagebox.showerror("Deletion Error", f"Failed to delete inventory.json.")
    
    def download_config_files(self):
        urls = {
            "autoexec.cfg": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/autoexec.cfg",
            "loadouts.cfg": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/loadouts.cfg",
            "operators.cfg": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/operators.cfg"
        }

        save_directory = os.path.join(os.getenv('USERPROFILE'), 'Documents', 'Call of Duty Modern Warfare', 'players')
        os.makedirs(save_directory, exist_ok=True)

        for file_name, url in urls.items():
            file_path = os.path.join(save_directory, file_name)
            try:
                urllib.request.urlretrieve(url, file_path)
            except Exception:
                messagebox.showerror("Download Error", f"Failed to download {file_name}.")
        
        messagebox.showinfo("Download Complete", "Configuration files downloaded successfully.")

    def download_gscbin(self):
        local_appdata = os.getenv('LOCALAPPDATA')
        game_path_file = os.path.join(local_appdata, 'temp', 'cod_mw_path.txt')
        
        try:
            with open(game_path_file, 'r') as file:
                game_path = file.read().strip()
        except FileNotFoundError:
            messagebox.showinfo("Failed to find the game's path", f"Please select the Modern Warfare path by clicking on settings.")
            return

        target_directory = os.path.join(game_path, 'donetsk', 'scripts')
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        file_url = 'https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/1922.gscbin'
        target_file_path = os.path.join(target_directory, '1922.gscbin')

        try:
            response = requests.get(file_url)
            response.raise_for_status() 
            
            with open(target_file_path, 'wb') as file:
                file.write(response.content)

            messagebox.showinfo("Download Finished", f"Successfully added unreleased gun support to your game.")
        except requests.exceptions.RequestException:
            messagebox.showerror("Download Error", f"Failed to download the gsc.")

    def download_greenluma(self):
        path_file = os.path.expandvars(r"%localappdata%\Temp\cod_mw2_path.txt")

        if not os.path.exists(path_file):
            messagebox.showerror("Error", f"Path file not found: {path_file}")
            return

        with open(path_file, 'r') as file:
            saved_path = file.readline().strip()

        greenluma_files = {
            "DLLInjector.exe": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/greenluma/DLLInjector.exe",
            "DLLInjector.ini": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/greenluma/DLLInjector.ini",
            "GreenLumaSettings_2024.exe": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/greenluma/GreenLumaSettings_2024.exe",
            "GreenLuma_2024_x64.dll": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/greenluma/GreenLuma_2024_x64.dll",
            "GreenLuma_2024_x86.dll": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/greenluma/GreenLuma_2024_x86.dll",
            "x64launcher.exe": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/greenluma/bin/x64launcher.exe"
        }

        applist_files = {
            "0.txt": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/AppList/0.txt",
            "1.txt": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/AppList/1.txt",
            "2.txt": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/AppList/2.txt",
            "3.txt": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/AppList/3.txt",
            "4.txt": "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/AppList/4.txt"
        }

        download_success = True

        for filename, url in greenluma_files.items():
            file_path = os.path.join(saved_path, filename)
            
            if filename == "x64launcher.exe":
                bin_folder = os.path.join(saved_path, "bin")
                if not os.path.exists(bin_folder):
                    os.makedirs(bin_folder)
                file_path = os.path.join(bin_folder, filename)
            
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
            
            except Exception:
                download_success = False

        # Download AppList files
        app_list_folder = os.path.join(saved_path, "AppList")
        if not os.path.exists(app_list_folder):
            os.makedirs(app_list_folder)

        for filename, url in applist_files.items():
            file_path = os.path.join(app_list_folder, filename)
            
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
            
            except Exception:
                download_success = False

        # Show result message
        if download_success:
            messagebox.showinfo("Greenluma", "Download Completed")
        else:
            messagebox.showerror("Greenluma", "Download Failed")

    def download_koala(self):
        url = "https://github.com/DHyperYT/cod-cw-mw-launcher/raw/main/KoalageddonInstaller.exe"
        try:
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, "KoalageddonInstaller.exe")

            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            subprocess.Popen(file_path, shell=True)
            messagebox.showinfo("Download Complete", "Koalageddon Installer has been downloaded.")

        except requests.RequestException as e:
            messagebox.showerror("Download Error", f"Failed to download the file: {e}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()
