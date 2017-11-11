import re
import pyperclip
import colour


keys = """
[1:ESC] [2:F1][3:F2][4:F3][5:F4] [6:F5][7:F6][8:F7][9:F8] [10:F9][11:F10][12:F11][13:F12]  [14:PRT][15:SCL][16:PAUS]
[17:`][18:1][19:2][20:3][21:4][22:5][23:6][24:7][25:8][26:9][27:0][28:-][29:=][30:BACKSP]  [31:INS][32:HOM][33:PGUP]
[34:TAB ][35:Q][36:W][37:E][38:R][39:T][40:Y][41:U][42:I][43:O][44:P][45:[][46:]][ 47:\ ]  [48:DEL][49:END][50:PGDN]
[ 51:CAPS ][52:A][53:S][54:D][55:F][56:G][57:H][58:J][59:K][60:L][61:;][62:'][ 63:ENTER ]
[  64:LSHIFT  ][65:Z][66:X][67:C][68:V][69:B][70:N][71:M][72:,][73:.][74:/][ 75:RSHIFT  ]          [76:UP]
[77:LCTRL][78:LGUI][79:LALT][       80:SPACE         ][81:RALT][82:FN1][83:APP][84:RCTRL]  [85:LFT][86:DWN][87:RHT]
"""

led_strip = """
[104][105][106][107][108][109][110][111][112][113][114][115][116]
[103]                                                       [117]
[102]                                                       [118]
[101]                                                       [119]
[100][99 ][98 ][97 ][96 ][95 ][94 ][93 ][92 ][91 ][90 ][89 ][88 ] < ---
"""

rainbow_ring_anim_def = [
    (0, (255, 255, 0)),
    (3, (0, 0, 255)),
    (6, (0, 255, 0)),
    (9, (255, 0, 0)),
    (12, (0, 127, 255)),
    (15, (127, 255, 0)),
    (18, (255, 0, 127)),
    (21, (0, 255, 127)),
    (24, (255, 127, 0)),
    (27, (127, 0, 255)),
    (30, (255, 0, 255))
]


col_black = (0, 0, 0)


def col_to_color(col):
    return colour.Color(rgb=tuple(v / 255.0 for v in col))


def color_to_col(color):
    return tuple(int(v * 255.0) for v in color.rgb)


def gradient(col_start, col_end, steps):
    c = col_to_color(col_start)
    g = []
    for color in c.range_to(col_to_color(col_end), steps):
        g.append(color_to_col(color))
    return g


def build_pixel(index, r, g, b):
    return f'P[{index}]({r},{g},{b})'


def finalize_frame(frame, index_start):
    pixels = []
    for i, col in enumerate(frame):
        pixels.append(build_pixel(i + index_start, *col))

    return ',  '.join(pixels) + ';'


def finalize_animation(animation, index_start):
    fin_frames = []
    for frame in animation:
        fin_frames.append(finalize_frame(frame, index_start))
    return '\n'.join(fin_frames)


def set_pixel(frame, index, col):
    if index < 0:
        index = len(frame) - index
    elif index >= len(frame):
        index -= len(frame)
    frame[index] = col


def build_ring_anim(col_static, col_moving_spot, shift):
    start = 88
    end = 120
    length = end - start
    frame = [col_static] * length
    frames = []
    for i in range(length):
        i += shift
        set_pixel(frame, i, col_moving_spot)
        frames.append(list(frame))
        set_pixel(frame, i, col_static)
    return frames


def build_overlay_ring_anim(col_static=col_black, anim_definitions=[(0, (255, 255, 0))]):
    animations = []

    for i, col in anim_definitions:
        animations.append(build_ring_anim(col_static, col, i))

    animation = build_ring_anim(col_static, anim_definitions[0][1], anim_definitions[0][0])
    anim_definitions.pop(0)
    for anim_index, overlay_anim in enumerate(animations):
        for frame_index, overlay_frame in enumerate(overlay_anim):
            for col_index, overlay_col in enumerate(overlay_frame):
                original_col = animation[frame_index][col_index]
                if original_col == col_static:
                    animation[frame_index][col_index] = overlay_col

    return animation


def build_ring_anim_def(cols, length):
    d = []
    for i, c in enumerate(cols):
        index = int((i / len(cols)) * length)
        d.append([index, c])
    return d


def build_full_top_down_key_gradient(col_start, col_end):
    colors = gradient(col_start, col_end, 6)
    rows = [
        [1, 16],
        [17, 33],
        [34, 50],
        [51, 63],
        [64, 76],
        [77, 87],
    ]
    frame = []
    for row_index, row in enumerate(rows):
        for k in range(row[0], row[1] + 1):
            frame.append(colors[row_index])
    return frame


if __name__ == '__main__':
    # ring_anim = build_overlay_ring_anim(col_black, rainbow_ring_anim_def)
    # out = finalize_animation(*ring_anim)
    ring_gradient = gradient((0, 0, 255), (0, 255, 0), 16) + gradient((0, 255, 0), (0, 0, 255), 17)[1:]
    ring_anim = build_overlay_ring_anim(col_black, build_ring_anim_def(ring_gradient, 32))
    out = finalize_animation(ring_anim, 88)
    # out = build_frame(build_full_top_down_key_gradient((0, 0, 255), (0, 255, 0)), 1)
    pyperclip.copy(out)
    print('Animation copied to clipboard!')
