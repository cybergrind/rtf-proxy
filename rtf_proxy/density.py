import math
import numpy as np
import time


def dist(pos1, pos2):
    tx, ty = pos1
    x, y = pos2
    return math.sqrt((tx - x) ** 2 + (ty - y) ** 2)


def draw_mask(density_radius, step=0.1):
    circle_side = int(density_radius * 2 / step) + 1
    circle_radius = int(circle_side / 2)
    circle = np.zeros((circle_side, circle_side), int)
    midpoint = int(circle_side / 2)
    xx = np.arange(circle.shape[0])
    yy = np.arange(circle.shape[1])
    inside = (xx[:,None] - midpoint) ** 2 + (yy[None, :] - midpoint) ** 2 <= (circle_radius ** 2)
    mask = circle | inside
    return mask


def shift(mypos, nextpos, step):
    x1, y1 = mypos
    x2, y2 = nextpos
    # print(f'Shift calc: {x2} - {x1} = {x2 - x1} ; {y2} - {y1} = {y2 - y1} : {dist(mypos, nextpos)}')
    return int((x2 - x1) / step), int((y2 - y1) / step)


def plot_density(mypos, points, distance, density_radius, step=0.1):
    side = int(distance * 6 / step) + 1
    center = int(side / 2)
    main = np.zeros((side, side), int)
    circle = draw_mask(density_radius, step)
    csize = circle.shape[0]
    for point in points:
        dx, dy = shift(mypos, point, step)
        sx, sy = center + dx, center + dy
        sx, sy = sx - int(csize / 2), sy - int(csize / 2)
        # s1 = sx:sx+csize, sy:sy+csize
        # print(f'SX/SY: {sx}/{sy} [{dx}/{dy}] {mypos}  => {circle.shape} / {csize} / {main.shape}')
        # main[sx:sx+csize, sy:sy+csize] = main[sx:sx+csize, sy:sy+csize] + circle
        main[sy:sy+csize, sx:sx+csize] = main[sy:sy+csize, sx:sx+csize] + circle
    return main


def timeit(fun):
    def _wrapped(*args, **kwargs):
        t = time.time()
        try:
            return fun(*args, **kwargs)
        finally:
            delta = time.time() - t
            print(f'Total time for call: {delta:.4f}')
    return _wrapped


# @timeit
def max_density(mypos, points, distance, density_radius, step=0.1):
    density_map = plot_density(mypos, points, distance, density_radius, step)
    y, x = np.unravel_index(np.argmax(density_map), density_map.shape)
    center = int(density_map.shape[0] / 2)
    # print(f'X/Y: {x}/{y} : max: {np.max(density_map)} Center: {center}')
    dx, dy = x - center, y - center
    # print(f'Dx/Dy: {dx}/{dy}')
    mx, my = mypos
    return (mx + dx * step), (my + dy * step)


def main():
    import matplotlib.pyplot as plt
    args = ([1927.2440185546875, 972.4502563476562],
            [(1929.205810546875, 970.8523559570312), (1931.6553955078125, 975.1654052734375), (1931.5374755859375, 977.6070556640625), (1924.19775390625, 963.9127807617188), (1936.61865234375, 971.6074829101562), (1917.362060546875, 974.93994140625)],
            14, 4.5)
    arr = plot_density(*args)
    print(arr)
    # print(np.max(arr))
    # print(np.unravel_index(np.argmax(arr), arr.shape))
    pos = max_density(*args)

    step = 0.1
    circle = draw_mask(4.5, 0.1)
    x0, y0 = args[0]
    x, y = pos
    center = int(arr.shape[0] / 2)
    dx, dy = x - x0, y - y0
    cx, cy = center + int(dx/step), center + int(dy/step)
    csize = circle.shape[0]
    cx, cy = cx - int(csize / 2), cy - int(csize / 2)
    for i in range(10):
        # arr[cx:cx+csize, cy:cy+csize] = arr[cx:cx+csize, cy:cy+csize] + circle
        arr[cy:cy+csize, cx:cx+csize] = arr[cy:cy+csize, cx:cx+csize] + circle
        pass
    
    print(f'Max: {pos} Dist: {dist(args[0], pos)}')
    plt.imshow(arr)
    plt.show()


if __name__ == '__main__':
    main()
