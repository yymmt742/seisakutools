import numpy as np
import pandas as pd
import colour
import matplotlib.pyplot as plt


class AnimalVision:
    """
    Animal colour vision model.

    Parameters
    ----------
    cone_csv : str
        CSV containing
            wavelength,dog_S,dog_L,...
    illuminant : str
        CIE illuminant (default D65)
    observer : str
        CIE observer
    """

    def __init__(
        self,
        cone_csv,
        illuminant="D65",
        observer="CIE 1931 2 Degree Standard Observer",
    ):
        self.cones = pd.read_csv(cone_csv)

        self.wavelength = self.cones.iloc[:, 0].to_numpy()
        self.cone_names = list(self.cones.columns[1:])
        self.cone_sens = self.cones.iloc[:, 1:].to_numpy().T

        self.shape = colour.SpectralShape(
            int(self.wavelength[0]),
            int(self.wavelength[-1]),
            int(self.wavelength[1] - self.wavelength[0]),
        )

        #
        # CIE data
        #
        self.cmfs = colour.MSDS_CMFS[observer].copy().align(self.shape)
        self.illuminant = colour.SDS_ILLUMINANTS[illuminant].copy().align(self.shape)
        self._build_matrices()

    def _build_matrices(self):

        dl = self.shape.interval

        xyz = self.cmfs.values.T
        illum = self.illuminant.values

        #
        # spectrum -> XYZ
        #
        A = xyz * illum * dl

        #
        # spectrum -> cone
        #
        B = self.cone_sens * illum * dl

        self.M_xyz_to_cone = B @ np.linalg.pinv(A)

        #
        # IEC61966-2-1
        #
        self.M_rgb_to_xyz = np.array(
            [
                [0.4124564, 0.3575761, 0.1804375],
                [0.2126729, 0.7151522, 0.0721750],
                [0.0193339, 0.1191920, 0.9503041],
            ]
        )

        self.M_xyz_to_rgb = np.linalg.inv(self.M_rgb_to_xyz)
        self.M_rgb_to_cone = self.M_xyz_to_cone @ self.M_rgb_to_xyz

    def plot_cones(
        self,
        normalize=True,
        ax=None,
    ):
        """
        Plot cone spectral sensitivities.

        Parameters
        ----------
        normalize : bool
            Normalize each cone to peak = 1.
        ax : matplotlib.axes.Axes or None
        """

        if ax is None:
            fig, ax = plt.subplots(figsize=(7, 4))

        for name, sens in zip(self.cone_names, self.cone_sens):

            y = sens.copy()

            if normalize:
                y /= np.max(y)

            ax.plot(
                self.wavelength,
                y,
                label=name,
                linewidth=2,
            )

        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Relative sensitivity")
        ax.set_xlim(
            self.wavelength[0],
            self.wavelength[-1],
        )

        ax.set_ylim(0, 1.05)

        ax.grid(True, alpha=0.3)
        ax.legend()

        return ax

    def rgb_to_cones(self, rgb):
        rgb = np.asarray(rgb)
        return rgb @ self.M_rgb_to_cone.T

    def opponent(self, cones):

        cones = np.asarray(cones)

        if cones.shape[-1] != 2:
            raise ValueError("Opponent implemented only for dichromats.")

        S = cones[..., 0]
        L = cones[..., 1]

        Y = S + L
        C = L - S

        return np.stack([Y, C], axis=-1)

    def print_matrix(self):

        print("RGB -> Cone")
        print(
            pd.DataFrame(
                self.M_rgb_to_cone,
                index=self.cone_names,
                columns=["R", "G", "B"],
            )
        )

    def cones_to_opponent(self, cones):
        """
        Cone responses -> opponent space

        Returns
        -------
        (...,2)

        [:,0] brightness
        [:,1] blue-yellow
        """

        cones = np.asarray(cones)

        S = cones[..., 0]
        L = cones[..., 1]

        Y = S + L
        C = L - S

        return np.stack([Y, C], axis=-1)

    def opponent_to_lab(
        self,
        opponent,
        chroma=80,
    ):
        """
        Opponent -> CIELab

        Parameters
        ----------
        opponent : (...,2)

        Returns
        -------
        (...,3)
        """

        opponent = np.asarray(opponent)

        Y = opponent[..., 0]
        C = opponent[..., 1]

        #
        # normalize brightness
        #
        Y = np.clip(Y, 0, None)

        if Y.max() > 0:
            Y = Y / Y.max()

        # L = 100 * Y
        L = 116 * Y - 16

        a = np.zeros_like(L)

        b = chroma * C

        return np.stack([L, a, b], axis=-1)

    def opponent_to_rgb(
        self,
        opponent,
        chroma=0.8,
    ):
        """
        Opponent -> RGB visualization
        """

        opponent = np.asarray(opponent)

        Y = opponent[..., 0]
        C = opponent[..., 1]

        R = Y + chroma * C
        G = Y
        B = Y - chroma * C

        rgb = np.stack([R, G, B], axis=-1)

        #
        # normalize
        #
        rgb -= rgb.min()

        if rgb.max() > 0:
            rgb /= rgb.max()

        return np.clip(rgb, 0, 1)

    def lab_to_rgb(self, lab):

        xyz = colour.Lab_to_XYZ(lab)

        rgb = colour.XYZ_to_sRGB(xyz)

        return np.clip(rgb, 0, 1)

    def von_kries(self, cones, background=None, eps=1e-8):
        """
        von Kries adaptation.

        Parameters
        ----------
        cones : (..., n_cones)

        background : (n_cones,) or None
            Cone response of adapting background.

            None -> image average
        """

        cones = np.asarray(cones)

        if background is None:
            #
            # image average
            #
            background = cones.reshape(-1, cones.shape[-1]).mean(axis=0)

        background = np.maximum(background, eps)

        return cones / background

    def render_image(
        self,
        image,
        gamma=True,
        background=None,
    ):
        """
        Simulate animal vision.

        Parameters
        ----------
        image
            RGB uint8 or float

        Returns
        -------
        RGB float
        """

        img = image.astype(float)

        if img.max() > 1:
            img /= 255.0

        #
        # sRGB -> linear
        #
        if gamma:
            img = colour.cctf_decoding(img)

        #
        # RGB -> cone
        #
        cone = img @ self.M_rgb_to_cone.T
        #
        # von Kries adaptation
        #
        cone = self.von_kries(
            cone,
            background=background,
        )

        #
        # opponent
        #
        opp = self.cones_to_opponent(cone)

        #
        # visualize
        #
        # out = self.opponent_to_rgb(opp)
        lab = self.opponent_to_lab(opp)
        out = self.lab_to_rgb(lab)

        #
        # linear -> sRGB
        #
        if gamma:
            out = colour.cctf_encoding(out)

        return np.clip(out, 0, 1)
