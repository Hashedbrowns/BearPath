from django.http import JsonResponse
from django.shortcuts import render
from .edgeCalculator import *
import polyline
from dotenv import load_dotenv
import os

load_dotenv()


def home(request):
    return render(request, 'index.html', context={"GOOGLE_MAPS_API_KEY": os.environ.get("GOOGLE_MAPS_API_KEY")})


def routeResponse(request):
    start = request.GET.get('start')
    end = request.GET.get("end")
    iweight = request.GET.get("iweight")
    if iweight is None:
        iweight = 1
    iweight = float(iweight)

    doors, n = generateJson("./static/data/MapData-Buildings.csv")
    peds = getPedways('./static/data/MapData-Pedways.csv')
    ped_edges = addPeds(peds, doors, n, iweight)

    name_to_door = {d["name"]: d["id"] for reg in doors for d in doors[reg]}
    n = len(name_to_door)

    int_edges = interalDist(doors, iweight)
    with open("./static/data/ex_edges.json", "r+") as rf:
        ext_edges = json.load(rf)

    all_edges = reid_edges(int_edges, name_to_door) + ext_edges + ped_edges
    with open("./static/data/all_edges.json", "w+") as wf:
        json.dump(all_edges, wf, indent=4)

    route = search(all_edges, doors[start][0]["id"], doors[end][0]["id"], n)
    route["polyline"] = polyline.encode([p for x in route["route"] for p in polyline.decode(x["polyline"])])

    if route["route"][0]["pt1"]["name"].split("-")[0] == route["route"][0]["pt2"]["name"].split("-")[0]:
        route["route"].pop(0)

    if route["route"][-1]["pt1"]["name"].split("-")[0] == route["route"][-1]["pt2"]["name"].split("-")[0]:
        route["route"].pop()

    route["actual_dist"] = route_dist(route)

    res = JsonResponse(route, json_dumps_params={'indent': 4})
    res["Access-Control-Allow-Origin"] = "*"
    res["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    res["Access-Control-Max-Age"] = "1000"
    res["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

    return res
