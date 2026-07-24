import sys
import numpy as np
import pandas as pd
import colour
from PIL import Image
import matplotlib.pyplot as plt
from animalvision import *
from pathlib import Path

dogvis = AnimalVision("dog_cones.csv")
# dogvis.plot_cones()
# plt.savefig("cones.png")
# plt.close()

rgb = np.array([1.0, 0.2, 0.1])

cones = dogvis.rgb_to_cones(rgb)
opps = dogvis.opponent(cones)

impath = Path(sys.argv[1])

image = Image.open(impath).convert("RGB")
image = np.asarray(image, dtype=np.float32) / 255.0
dogim = dogvis.render_image(image)

out = (255 * np.clip(dogim, 0, 1)).astype(np.uint8)
Image.fromarray(out).save(str(impath.with_suffix("")) + "_dog.png")
