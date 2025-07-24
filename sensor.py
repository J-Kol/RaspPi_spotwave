import tomli
from pathlib import Path
import time
from waveline import SpotWave
import numpy as np

#csv_file = Path("records.csv")
HERE = Path(__file__).parent

def measure(*, name: str = "csv_data", samples_rate: int = 1000, averages_rate: int = 100, config_name:str = "config.toml", stop_measurement=None, count=None):
    CSV_DIR = HERE / name
    CSV_DIR.mkdir(exist_ok=True)
    with open(HERE / "config" /config_name, mode="rb") as f:
        config = tomli.load(f)
    ports = SpotWave.discover()
    if not ports:
        raise RuntimeError("No SpotWave device connected or found.")
    print(f"Discovered spotWave devices: {ports}")
    port = ports[0]
    print(port)

    # setup & start logging using toml config
    with SpotWave(port) as sw:
        #sw.identify()
        highpass_ = config["acq"]["filter"]["highpass"]
        lowpass_ = config["acq"]["filter"]["lowpass"]
        order_ = config["acq"]["filter"]["order"]
        sw.set_filter(highpass=highpass_, lowpass=lowpass_, order=order_)
        sw.set_tr_decimation(1)
        sw.set_cct(-1)

        #print("Start Recording")
        samples = samples_rate
        a = 0
        averages = averages_rate
        #print(sw.get_setup())

        if count is None:
            while True:
                if stop_measurement and stop_measurement.is_set():
                    print("Messung gestoppt!")
                    break
                values_matrix = np.empty((samples, averages))
                for i in range(averages):
                    record = sw.get_tr_snapshot(samples)
                    values_matrix[:, i] = record.data
                    time.sleep(0.01)                

                values_avg = np.mean(values_matrix, axis=1)
                print(values_avg.shape)

                times = np.arange(samples) / sw.CLOCK
                csv_data = np.stack((times, values_avg)).T
                np.savetxt(CSV_DIR / f"waveform_{a}.csv", csv_data, delimiter=",", header="Time[s], Amplitude[v]")

                time.sleep(0.1)
                a += 1

        else:
            for a in range(count):
                if stop_measurement and stop_measurement.is_set():
                    print("Messung gestoppt!")
                    break
                values_matrix = np.empty((samples, averages))
                for i in range(averages):
                    record = sw.get_tr_snapshot(samples)
                    values_matrix[:, i] = record.data
                    time.sleep(0.01)                

                values_avg = np.mean(values_matrix, axis=1)
                print(values_avg.shape)

                times = np.arange(samples) / sw.CLOCK
                csv_data = np.stack((times, values_avg)).T
                np.savetxt(CSV_DIR / f"waveform_{a}.csv", csv_data, delimiter=",", header="Time[s], Amplitude[v]")

                time.sleep(0.1)
                a += 1
            print("done")
            return(CSV_DIR)

def main():
    measure(config_name="config.toml")

if __name__ == "__main__":
    main()