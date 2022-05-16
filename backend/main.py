from fastapi import FastAPI
from fastapi.responses import FileResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import sys
sys.path.append('./../')
print(sys.path)


from backend.graph_actions import get_graph


rename_keys = {
    "Описание ": "Description"
}

G = get_graph()
nodes_data = {}
nodes_data_arr = []
for node in G.nodes(data=True):
    node_data = node[1]
    if 'MODEL' in node_data.keys() or 'Тип данных' not in node_data.keys():
        continue
    search_str = " ".join(str(el) for el in node_data.values())
    temp = node_data.copy()
    temp.update({'searchStr': search_str})
    for k, v in rename_keys.items():
        temp[v] = temp.pop(k)  # Renaming keys
    nodes_data_arr.append(temp)
    nodes_data[node_data['name']] = node_data
#%%

app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
        "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/nodes/{name}')
def get_node_by_name(name):
    return ORJSONResponse(nodes_data[name])


@app.get("/data")
def get_data():
    return ORJSONResponse(nodes_data_arr)


@app.get("/testdata")
def get_testdata():
    data = [
        {
            "id": 1,
            "name": "Asia",
            "population": "4,624,520,000",
            "no_of_countries": 50,
            "area": "44,579,000"
        },
        {
            "id": 2,
            "name": "Africa",
            "population": "1,327,042,300",
            "no_of_countries": 54,
            "area": "30,370,000"
        },
        {
            "id": 3,
            "name": "North America",
            "population": "590,176,500",
            "no_of_countries": 23,
            "area": "24,709,000"
        },
        {
            "id": 4,
            "name": "South America",
            "population": "429,276,300",
            "no_of_countries": 12,
            "area": "17,840,000"
        },
        {
            "id": 5,
            "name": "Antartica",
            "population": "No real data on populants",
            "no_of_countries": 0,
            "area": "14,000,000"
        },
        {
            "id": 6,
            "name": "Europe",
            "population": "747,447,200",
            "no_of_countries": 51,
            "area": "10,180,000"
        },
        {
            "id": 7,
            "name": "Australia",
            "population": "42,448,700",
            "no_of_countries": 14,
            "area": "8,600,000"
        }
    ]
    return ORJSONResponse(data)


# Place After All Other Routes
app.mount('', StaticFiles(directory="./../frontend/public/", html=True), name="static")
