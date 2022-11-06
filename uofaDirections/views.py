from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect
from .edgeCalculator import *
from django.templatetags.static import static
import polyline
def home(request):
    return render(request, 'index.html')
def routeResponse(request):
    start = request.GET.get('start')
    end = request.GET.get("end")
    iweight = request.GET.get("iweight")
    if iweight == None:
        iweight = 1
    iweight=float(iweight)

    doors, N = generateJson("./static/MapData-Buildings.csv")

    peds = getPedways("./static/MapData-Pedways.csv")
    ped_edges = addPeds(peds,doors,N,iweight)


    name_to_door = { d["name"]:d["id"] for reg in doors for d in doors[reg]}
    N = len(name_to_door)

    int_edges = interalDist(doors,iweight)
    with open("./static/ex_edges.json","r+") as rf:
        ext_edges=json.load(rf)

    all_edges = reid_edges(int_edges,name_to_door) + ext_edges + ped_edges
    with open("all_edges.json","w+") as wf:
        json.dump(all_edges,wf,indent=4)


    route = search(all_edges, doors[start][0]["id"], doors[end][0]["id"], N)
    route["polyline"] =  polyline.encode([ p for x in route["route"] for p in polyline.decode(x["polyline"])])
    route["actual_dist"] =  route_dist(route)


    if route["route"][0]["pt1"]["name"].split("-")[0] == route["route"][0]["pt1"]["name"].split("-")[0]:
        route["route"].pop(0)
    
    if route["route"][-1]["pt1"]["name"].split("-")[0] == route["route"][-1]["pt1"]["name"].split("-")[0]:
        route["route"].pop()

    return JsonResponse(route,json_dumps_params={'indent': 4})