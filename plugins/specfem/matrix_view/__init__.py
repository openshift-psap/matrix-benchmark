from ui.table_stats import TableStats

import plugins.adaptive.matrix_view
from plugins.adaptive.matrix_view import parse_data, all_records, get_record

def rewrite_properties(params_dict):
    if "mpi-slots" not in params_dict:
        params_dict["mpi-slots"] = "999"

    NB_CORE_ON_MACHINES = 8
    
    machines = int(int(params_dict["processes"]) / int(params_dict["mpi-slots"]))
    if machines * int(params_dict["mpi-slots"]) != int(params_dict["processes"]):
        machines += 1
    params_dict["machines"] = str(machines)

    if "network" in params_dict:
        network = params_dict["network"]
        del params_dict["network"]
        if network != "default":
            params_dict["platform"] += f"_{network}"

    if params_dict["platform"] == "podman":
        params_dict["platform"] = "baremetal_podman"
        
    del params_dict["processes"]

    if "gpu" in params_dict:
        if params_dict['gpu'].isdigit():
            params_dict["gpu"] = f":{int(params_dict['gpu']):02d}"
        else:
            params_dict['gpu'] = ":"+params_dict['gpu']
    else:
        params_dict['gpu'] = 'off'


    if "relyOnSharedFS" not in params_dict:
        params_dict["relyOnSharedFS"] = "False"
    
    params_dict["run"] = "2"
    params_dict["relyOnSharedFS"] = params_dict["relyOnSharedFS"].lower()
    return params_dict

plugins.adaptive.matrix_view.rewrite_properties = rewrite_properties

def register():
    TableStats.Average("total_time", "Total time", "?.timing",
                       "timing.total_time", ".0f", "s")


