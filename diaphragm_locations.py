def find_diaphragm_height(x):
    if x < 51 or x >= 1200:
        result_height = 116.19
    elif x < 626:
        result_height = 116.19 + ((20.0 / 575) * (x - 50))
    else:
        result_height = 136.19 - ((20.0 / 575) * (x - 625))
    print(result_height)

if __name__ == "__main__":
    locs = [0, 60, 150, 270, 430, 820, 980, 1100, 1190, 1250]

    for loc in locs:
        find_diaphragm_height(loc)