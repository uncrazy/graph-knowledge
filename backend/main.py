from fastapi import FastAPI
from fastapi.responses import FileResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from backend.graph_actions import get_graph
from backend.dashapp import create_dash_app
from resources.utils import plot
from starlette.responses import RedirectResponse
import uvicorn
import flask
from flask_cors import CORS, cross_origin


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


app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:8000/",
    "http://localhost:8000/data",
    "http://localhost:8000/dash",
    "http://localhost:8050/"
    "http://localhost:3000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# figure = plot(G)
dash_app = create_dash_app(G=G,
                           requests_pathname_prefix="/dash/")


@app.get('/nodes/{name}')
def get_node_by_name(name):
    return ORJSONResponse(nodes_data[name])


@app.get("/data")
def get_data():
    return ORJSONResponse(nodes_data_arr)


# Place After All Other Routes
app.mount("/dash", WSGIMiddleware(dash_app.server))
app.mount("/images", StaticFiles(directory="frontend/images"), name="images")
app.mount("", StaticFiles(directory="frontend/public", html=True), name="build")


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
