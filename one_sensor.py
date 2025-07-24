import tomli
from pathlib import Path
import time
from waveline import SpotWave
import numpy as np

HERE = Path(__file__).parent

def convert_to_csv_string(arr: np.ndarray) -> str:
    return ", ".join(map(str, arr.tolist()))

def measuring(*, name: str = "measurement", config_name: str = "config.toml", count: int = 10):
    CSV_DIR = HERE / name
    CSV_DIR.mkdir(exist_ok=True)
    config_path = Path(HERE) / "config" / config_name
    with open(config_path, mode="rb") as f:
        config = tomli.load(f)
    ports = SpotWave.discover()
    if not ports:
        raise RuntimeError("No SpotWave device connected or found.")
    print(f"Discovered spotWave devices: {ports}")
    port = ports[0]

    # setup & start logging using toml config
    with SpotWave(port) as sw:
        highpass_ = config["acq"]["filter"]["highpass"]
        lowpass_ = config["acq"]["filter"]["lowpass"]
        order_ = config["acq"]["filter"]["order"]
        sw.set_filter(highpass=highpass_, lowpass=lowpass_, order=order_)
        #print(sw.get_setup())
        sw.set_threshold(config["acq"]["threshold"])
        sw.set_ddt(config["acq"]["ddt"])
        #sw.set_filter(highpass=["acq"]["filter"]{highpass})
        sw.set_status_interval(config["acq"]["status_interval"])

        sw.set_continuous_mode(config["acq"]["continuous_mode"])
        sw.set_tr_enabled(config["acq"]["tr_enabled"])
        sw.set_tr_decimation(config["acq"]["set_tr_decimation"])
        sw.set_tr_enabled(config["acq"]["set_tr_enabled"])
        sw.set_tr_postduration(config["acq"]["set_tr_postduration"])
        sw.set_tr_pretrigger(config["acq"]["set_tr_pretrigger"])
        #print(config["acq"])
        sw.start_acquisition()
        #print(sw.get_status())

        #print(CSV_DIR.resolve())
        #writes a Headzeile and overwrites an existing "records.csv"
        with open(CSV_DIR/"records.csv", "w") as f:
            print("Time[s], Record", file=f)

        print("Start")
        if count is None:
            while True:
                time.sleep(0.1)
                #records_ae = sw.get_ae_data()
                records = sw.get_tr_data()
                if records:
                    print(f"{len(records)} new records")

                    with open(CSV_DIR/"records.csv", "a") as f:
                        for record in records:
                            print(convert_to_csv_string(record.data), file=f)
        else:
            a = 0
            for a in range(count*10):
                time.sleep(0.1)
                #records_ae = sw.get_ae_data()
                records = sw.get_tr_data()
                if records:
                    print(f"{len(records)} new records")

                    with open(CSV_DIR/"records.csv", "a") as f:
                        for record in records:
                            print(convert_to_csv_string(record.data), file=f)
            print("done")
            return(CSV_DIR)

def main():
    measuring(config_name="config.toml", count=None)

if __name__ == "__main__":
    main()