from fastapi import FastAPI
from pathlib import Path
import tomli
from pydantic import BaseModel, Field
import tomlkit
from sensor import measure
from one_sensor import measuring
from analyzer import analyzer
from datetime import date
import json

class FilterModel(BaseModel):
    highpass: int = 100 
    lowpass: int = 200000
    order: int = 4

class ConfigModel(BaseModel):
    threshold: int = 60000
    ddt: int = 1000
    continuous_mode: bool = False
    tr_enabled: bool = True
    set_tr_decimation: int = 1
    set_tr_enabled: bool = True
    set_tr_postduration: int = 1500
    set_tr_pretrigger: int = 2000
    status_interval: int = 0

class ConfigandFilter(BaseModel):
    config: ConfigModel
    filter: FilterModel

class MeasurementModel(BaseModel):
    name: str = "csv_data"
    config_name: str = "config.toml"
    date_of_measurement: date = Field(default_factory=lambda: date.today(), validate_default=True)
    #exact_time: date = Field(default_factory=lambda: date.now, validate_default=True)
    description: str = None
    count: int = 10
    # only for 2 sensor
    samples_rate: int = 1000
    averages_rate: int = 100

app = FastAPI()

@app.get("/")
def main_func():
    return {"Welcome"}

#@app.get("/example/{name}/{id}")
#async def example_func(id: int, name: str):
#    return {"name": name, "id": id}

@app.get("/config")
def get_config(name: str):
    config_dir = Path(__file__).parent / "config"
    config_path = (config_dir / name).resolve()
    
    with open(config_path, mode="rb") as f:
        config_data = tomli.load(f)

    return config_data

@app.post("/config")
def post_config(name: str, data: ConfigandFilter):
    config = data.config
    filter = data.filter

    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)

    if name[-4:] == "toml":
        config_path = (config_dir / name).resolve()
    else:
        config_path = (config_dir / name).with_suffix(".toml").resolve()

    config_dict = config.model_dump()
    filter_dict = filter.model_dump()
    
    doc = tomlkit.document()

    for key, value in config_dict.items():
        doc[key] = value

    filter_oneline = ", ".join(f"{k}={v}" for k, v in filter_dict.items())

    toml_data = tomlkit.dumps(doc)

    with open(config_path, "w") as f:
        f.write("[acq]\n\n")
        f.write(toml_data)
        f.write("\nfilter = { ")
        f.write(filter_oneline)
        f.write("}")

    return str(config_path)

@app.post("/measurement")
def get_measurement(data: MeasurementModel):
    path_measured = measure(samples_rate=data.samples_rate, averages_rate=data.averages_rate, config_name=data.config_name, count=data.count)
    save_metadata(data, path_measured)

@app.post("/one_sensor")
def post_measurement_with_one_sensor(data: MeasurementModel):
    path_measured = measuring(config_name=data.config_name, count=data.count)
    data.samples_rate = None
    data.averages_rate = None
    save_metadata(data, path_measured)

def save_metadata(data: MeasurementModel, path: Path):
    data_dict = data.dict()
    data_dict['date_of_measurement'] = data_dict['date_of_measurement'].isoformat()
    path =  path / "metadata.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data_dict, f)
    return "success"

@app.get("/analyzer")
def post_analyzer(datapath: Path = Path("2_sensor_measurments/20250527_plexiglass/csv_data_2"), *, plot: bool = False, sensor_distance: float = None, timepicker: str = "aic", material: str = None, threshold: float = 10e-6):
    data = analyzer(datapath=datapath, plot=plot, sensor_distance=sensor_distance, timepicker=timepicker, material=material, threshold=threshold)
    print("Analyzer output:", data)
    return data