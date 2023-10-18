from pathlib import Path
import pandas as pd
from pandas import DataFrame


SYMBOLS = {
    "SPACE": "␣",
    "SPACERIGHT": "␣",
    "SHIFT": "⇧",
    "RIGHT_SHIFT": "⇧",
    "LEFT_SHIFT": "⇧",
    "LEFT_CTRL": "▵",
    "RIGHT_CTRL": "▵",
    "LEFT_ALT": "⎇",
    "RIGHT_ALT": "⎇",
    "LEFT_GUI": "L⃢ ",
    "RIGHT_GUI": "R⃢ ",
    "DEL": "␡",
    "ESC": "␛",
    "ENTER": "⏎",
    "TAB": "⇥",
    "DUP": "DUP",
    "AMBIRIGHT": "AR",
    "AMBILEFT": "AL",
    # "RIGHT_ARROW": "➔",
    "ARROW_LF": "←",
    "ARROW_RT": "→",
    "ARROW_UP": "↑",
    "ARROW_DN": "↓",
    "MS_": "🐁",
    "MS_MOVE_LF": "m←",
    "MS_MOVE_RT": "m→",
    "MS_MOVE_UP": "m↑",
    "MS_MOVE_DN": "m↓",
    "MS_CLICK_LF": "ʘR",
    "MS_CLICK_RT": "Lʘ",
    "MS_SCRL_LF": "⇳←",
    "MS_SCRL_RT": "⇳→",
    "MS_SCRL_UP": "⇳↑",
    "MS_SCRL_DN": "⇳↓",
    "EMPTY": "☐",
    "BKSP": "⇤",
    "3D": "⟀",
    "KM_1_L": "K1",
    "KM_1_R": "K1",
    "KM_2_L": "K2",
    "KM_2_R": "K2",
    "KM_3_L": "K3",
    "KM_3_R": "K3",
}

MAX_SW_NUM = 89
# %%


def _main():
    # %%
    runfile("translate_layout.py")
    layout_df2 = load_enriched_layout('data/layout-default.csv')

    rendered = { km:  draw_layout_for_km(layout_df2, km=km)
                 for km in ['A1', 'A2', 'A3']}

    with open("layouts2.txt", "wt") as f_out:
        for km, layout in rendered.items():
            print(f"{km}:\n{layout}\n\n", file=f_out)
    # %%


def draw_layout_for_km(layout_df2: DataFrame, *,  km: str) -> str:
    coords = build_sw_num_coords()
    max_row = max(tup[0] for tup in coords.values())
    max_col = max(tup[1] for tup in coords.values())

    canvas = AsciiCanvas(n_rows=max_row + 1,  n_cols=max_col + 2)

    key_map = layout_df2[ layout_df2['key_map'] == km]

    for _, rec in key_map.iterrows():
        sw_num = rec['switch']
        row, col = coords[sw_num]
        canvas.draw(row, col, rec['repr2'])

    return canvas.render()
    # %%


def build_sw_num_coords() -> dict[int, tuple[int, int]]:
    sw_loc_lines = Path('data/switch-locations.txt').read_text().split("\n")

    coords: dict[int, tuple[int, int]] = {}
    for sw_num in range(MAX_SW_NUM + 1):
        coords[sw_num] = find_coords(sw_loc_lines, sw_num)

    return coords
    # %%


def find_coords(sw_loc_lines: list[str], sw_num: int) -> tuple[int, int]:
    a_str = "%02d" % sw_num

    for i, line in enumerate(sw_loc_lines):
        j = line.find(a_str)
        if j >= 0:
            return i, j

    raise ValueError(f"Could not find: a_str={a_str}")
    # %%


class AsciiCanvas:
    def __init__(self, n_rows: int, n_cols: int):

        self.rows = [ [' '] * n_cols for _ in range(n_rows)]

    def draw(self, row_idx: int, col_idx: int, what: str):
        for i, ch in enumerate(what):
            self.rows[row_idx][col_idx + i] = ch

    def render(self) -> str:
        return "\n".join("".join(row) for row in self.rows)
    # %%

def load_enriched_layout(csv_path: str) -> DataFrame:
    layout_df = pd.read_csv(csv_path, header=None)
    layout_df.columns = ["key_map", "switch", "action_code"]

    action_codes = (pd.read_csv('data/action-codes.csv', na_values='')
                    .fillna(''))

    layout_df2 = (layout_df.merge(action_codes, left_on='action_code',
                                  right_on='code_id')
                  .sort_values(['key_map', 'switch']))

    layout_df2['repr2'] = layout_df2['utf8_repr'].apply(repr2)

    return layout_df2
    # %%


def repr2(repr1: str) -> str:

    if repr1 == '':
        return SYMBOLS['EMPTY']
    if len(repr1) == 1:
        return repr1

    if repr1.startswith('F') and len(repr1) <= 3:
        return repr1

    if repr1 in SYMBOLS:
        return SYMBOLS[repr1]

    if repr1.endswith('_3D'):
        return SYMBOLS['3D']

    print(f'Error: {repr(repr1)}')
# %%
