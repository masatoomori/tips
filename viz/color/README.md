# 色に関するテクニック

## 色のリストを作成する

### グラデーション

出所：[【Python】グラデーションを作る関数を作った](https://qiita.com/78910jqk/items/37f52cbe1571fde75566)

```python
def color_gradation(start="#CCCCCC", end="#00519A", step=5):
  """
    before use it
    import numpy as np

    return like this:
    ['#cccccc', '#bc9aa8', '#b95ba9', '#8b2aa9', '#370e83']
  """
  from colorsys import rgb_to_hls, hls_to_rgb
  if len(start) != 7 or len(end) != 7:
    raise Exception(f"argument length must be 7: now{len(start)}, {len(end)}")

  rgb_s = (int(start[i:i + 2], 16) / 256 for i in range(1, 4))
  rgb_e = (int(end[i:i + 2], 16) / 256 for i in range(1, 4))
  hls_s = np.array(rgb_to_hls(*rgb_s))
  hls_e = np.array(rgb_to_hls(*rgb_e))
  diff_hls = hls_e - hls_s

  # color is circle
  diff_hls[0] = (diff_hls[0] + 0.5) - np.floor(diff_hls[0] + 0.5) - 0.5
  hls_list = [hls_s + diff_hls * i / step for i in range(step)]
  rgb_list = [hls_to_rgb(*p) for p in hls_list]

  # Transform floor rgb to Strings rgb
  str_rgb = []
  for rgb in rgb_list:
    str_rgb.append(f"#{int(rgb[0]* 256):02x}{int(rgb[1]* 256):02x}{int(rgb[2]* 256):02x}")
  return str_rgb


def main():
    nsinx = 5
    x = np.linspace(0, np.pi * 4, 100)
    dx = np.pi / (nsinx)
    sinxes = [np.sin(x - i * dx) for i in range(nsinx)]
    gra = color_gradation(start="#CCCCCC", end="#00519A", step=nsinx)
    for i, sinx in enumerate(sinxes):
        plt.plot(x, sinx, label=f"dx*{i}", lw=3, color=gra[i])
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
```
