import argparse
from pathlib import Path
import numpy as np

CLOCK = 2000000

def discrete_fourier_transform(signal):
    return np.fft.rfft(signal)

def _hinkley_numpy(arr: np.ndarray, alpha: int = 5) -> tuple[np.ndarray, int]:
    n = len(arr)
    energy_cum = np.cumsum(arr**2, dtype=np.float64)
    negative_trend = energy_cum[-1] / (alpha * n)
    result = energy_cum - (np.arange(n, dtype=np.float32) * negative_trend)
    return result, np.argmin(result)

def _aic_numpy(arr: np.ndarray) -> tuple[np.ndarray, int]:
    n = len(arr)
    safety_eps = np.finfo(np.float32).tiny

    l_sum = np.cumsum(arr, dtype=np.float64)
    l_squaresum = np.cumsum(arr**2, dtype=np.float64)
    r_sum = l_sum[-1] - l_sum
    r_squaresum = l_squaresum[-1] - l_squaresum

    index = np.arange(n)
    l_len = index + 1
    r_len = n - index - 1

    with np.errstate(divide="ignore", invalid="ignore"):
        l_variance = (1 / l_len) * l_squaresum - ((1 / l_len) * l_sum) ** 2
        r_variance = (1 / r_len) * r_squaresum - ((1 / r_len) * r_sum) ** 2

    # catch negative and very small values < safety_eps
    np.maximum(l_variance, safety_eps, out=l_variance)
    np.maximum(r_variance, safety_eps, out=r_variance)

    result = (index + 1) * np.log10(l_variance) + (n - index - 2) * np.log10(r_variance)
    return result, np.nanargmin(result)

def analyzer(datapath: Path, *, plot: bool, sensor_distance: float, timepicker: str = "aic", material: str, threshold: float = 10e-6):
    """
    Analyzes waveform data from CSV files.

    Parameters:
        datapath (Path): Path to the folder containing CSV files(navigates two directory up).
        plot (bool): Whether to plot the waveform and spectrum.
        sensor_distance (float): Distance between sensors in meters.
        timepicker (str): Method for picking time-of-arrival ('hinkley', 'aic', 'threshold').
        material (str): Material name for labeling plots.
        threshold (float): Threshold for signal detection.
    """

    print(f"Sensor Distance: {sensor_distance} m")
    print(f"Material: {material}")

    csv_path = Path(__file__).parent.parent.parent / datapath
    if not csv_path.exists():
        raise ValueError(csv_path)
    csv_files = list(csv_path.glob("*.csv"))
    print("Measurments:", len(csv_files))
    waveforms = []
    #print(csv_files)
    for csv_file in csv_files:
        data = np.loadtxt(csv_file, skiprows=1, delimiter=",")
        waveforms.append(data[:,1])

    waveform_matrix = np.vstack(waveforms)
    waveform_mean = np.mean(waveform_matrix, axis=0)
    samples = len(waveform_mean)

    if timepicker == 'hinkley':
        timepicker_detection, timepicker_index = _hinkley_numpy(waveform_mean)
    elif timepicker == 'aic':
        timepicker_detection, timepicker_index = _aic_numpy(waveform_mean)
    else:
        timepicker_index = np.where(np.abs(waveform_mean) > threshold)[0][0]
        timepicker_detection = np.zeros(samples)
        timepicker_detection[timepicker_index:] = 1

    #indices = np.where(np.abs(waveform_mean) > threshold)[0]
    #toa_index = indices[0] if indices.size > 0 else samples
    toa_time = timepicker_index / CLOCK
    print("Index:\t", timepicker_index)
    print("Time:\t", toa_time * 1e6, "µs")

    if sensor_distance:
        speed = sensor_distance/toa_time
        print("Speed:\t", speed, "m/s")

    if plot:
        import matplotlib.pyplot as plt
        times = np.arange(samples) / CLOCK

        fig, axes = plt.subplots(2, tight_layout=True, figsize=(12, 8))

        for waveform in waveform_matrix:
            axes[0].plot(times, waveform, linewidth = 0.5)

        axes[0].plot(times, waveform_mean, "-", linewidth = 1.0, label="Waveform", color='red')
        axes[0].set(xlabel = "time [µs]", ylabel="volt [V]")
        axes[0].set_ylim(np.min(waveform_matrix), np.max(waveform_matrix))
        axes[0].scatter(toa_time, waveform_mean[timepicker_index],color='red', s = 30)

        if timepicker == 'threshold':
            axes[0].axhline(threshold, color='red', linestyle='--', linewidth=0.7)
            axes[0].axhline(-threshold, color='red', linestyle='--', linewidth=0.7)
        else:
            ax2 = axes[0].twinx()
            ax2.plot(times, timepicker_detection, "-", linewidth = 1.0, label="Waveform", color='blue')

        spectrum = discrete_fourier_transform(waveform_mean)
        freqs = np.fft.rfftfreq(samples, d=1/CLOCK)
        axes[1].semilogy(freqs, np.abs(spectrum), "-", linewidth = 0.5, label="Waveform")
        axes[1].set(xlabel="Frequency (Hz)", ylabel="Amplitude")

        if material:
            plt.title(material)

        #with open("analyzer_data.txt", "w") as f:
        #    f.write(f"Index:\t{timepicker_index}\nTime:\t{toa_time * 1e6:.3f} µs\nSpeed:\t{speed:.2f} m/s")

        plt.show()
    if sensor_distance:
        return {"measurements": len(csv_files), "index": int(timepicker_index), "time_us": float(round(toa_time * 1e6, 2)), "speed": float(round(speed, 3))}
    else:
        if toa_time is None or toa_time == "":
            return {"measurements": len(csv_files), "index": int(timepicker_index)}
        else:
            return {"measurements": len(csv_files), "index": int(timepicker_index), "time_us": float(round(toa_time * 1e6, 2))}

def main():
    parser = argparse.ArgumentParser(
                        prog='csv analyzer',
                        description='Analyzes the chosen CSV data')

    parser.add_argument('datapath', type=Path, help='path with the csv')#, required=True)
    parser.add_argument('-p', '--plot', action='store_true', help='to get a visualisation of the data')
    parser.add_argument('-d', '--sensor-distance', type=float, help='the distance between the two sensors( in meter)')
    parser.add_argument('-m', '--material', help='the material that was measuered')
    #parser.add_argument('-f', '--fft', action='store_true', help='to get a FFT(only with plot not recommended and maybe even off)')
    parser.add_argument('-t', '--timepicker', help='chose a timepicker(hinkley, aic or threshold)', default='aic')
    parser.add_argument('-th', '--threshold', type=float, default=10e-6, help='The threshold is the minimum value at which the signal occurs')

    #parser.print_help()
    args = parser.parse_args()

    analyzer(datapath=args.datapath, 
            plot=args.plot,
            sensor_distance=args.sensor_distance,
            material=args.material,
            timepicker=args.timepicker,
            threshold=args.threshold)

if __name__ == "__main__":
    main()