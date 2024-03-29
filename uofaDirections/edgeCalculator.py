import pandas as pd
import json
from math import sin, cos, sqrt, atan2, radians
import polyline
from heapq import *


def generateJson(filename):
    doors = {}
    sheets = pd.read_csv(filename)
    for i in range(len(sheets)):
        loc = sheets["Building"][i]
        if loc not in doors:
            doors[loc] = []
        doors[loc].append({"id": i, "name": loc + "-" + sheets["Door Name"][i], "loc": (
            sheets["Latitude"][i], sheets["Longitude"][i])})

    with open("./static/data/doors.json", "w+") as wf:
        json.dump(doors, wf, indent=4)

    return doors, len(sheets)


def getPedways(filename):
    fpeds = []
    peds = pd.read_csv(filename)
    for i in range(len(peds)):
        start = {"bldg": peds["Start"][i], "lat": peds["SLatitude"][i], "lon": peds["SLongitude"][i]}
        end = {"bldg": peds["End"][i], "lat": peds["ELatitude"][i], "lon": peds["ELongitude"][i]}
        fpeds.append([start, end])

    with open("./static/data/peds.json", "w+") as wf:
        json.dump(fpeds, wf, indent=4)
    return fpeds


def distPoints(lat1, lon1, lat2, lon2):
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def addPeds(peds, doors, n, weight=0.3):
    ped_edges = []

    k = n
    for i in range(len(peds)):
        s, e = peds[i]
        s_bldg = {"id": k, "name": f"{s['bldg']}-ped_{e['bldg']}", "loc": [s["lat"], s["lon"]]}
        k += 1
        e_bldg = {"id": k, "name": f"{e['bldg']}-ped_{s['bldg']}", "loc": [e["lat"], e["lon"]]}
        k += 1

        if s['bldg'] not in doors:
            doors[s['bldg']] = []

        if e['bldg'] not in doors:
            doors[e['bldg']] = []

        for d in doors[s['bldg']]:
            s_edge = {"pt1": s_bldg, "pt2": d, "dist": distPoints(s["lat"], s["lon"], *d["loc"]),
                      "polyline": polyline.encode([[s["lat"], s["lon"]], d["loc"]])}

            ped_edges.append(s_edge)

        for d in doors[e['bldg']]:
            e_edge = {"pt1": e_bldg, "pt2": d, "dist": distPoints(e["lat"], e["lon"], *d["loc"]) * weight,
                      "polyline": polyline.encode([[e["lat"], e["lon"]], d["loc"]])}

            ped_edges.append(e_edge)

        ped_edge = {"pt1": s_bldg, "pt2": e_bldg, "dist": distPoints(s["lat"], s["lon"], e["lat"], e["lon"]) * weight,
                    "polyline": polyline.encode([[s["lat"], s["lon"]], [e["lat"], e["lon"]]])}
        ped_edges.append(ped_edge)

        doors[s['bldg']].append(s_bldg)
        doors[e['bldg']].append(e_bldg)
    return ped_edges


def interalDist(sheets, weight=0.3):
    int_edges = []
    visted = set()
    for reg in sheets:
        for pt1 in sheets[reg]:
            for pt2 in sheets[reg]:
                if pt1["id"] != pt2["id"] and (pt2["id"], pt1["id"]) not in visted:
                    visted.add((pt1["id"], pt2["id"],))
                    edge = {"pt1": pt1, "pt2": pt2,
                            "dist": distPoints(pt1["loc"][0], pt1["loc"][1], pt2["loc"][0], pt2["loc"][1]) * weight,
                            "polyline": polyline.encode([pt1["loc"], pt2["loc"]])}
                    int_edges.append(edge)

    return int_edges


def externalDist(sheets):
    edges = []
    visted = set()
    for reg1 in sheets:
        for pt1 in sheets[reg1]:
            for reg2 in sheets:
                for pt2 in sheets[reg2]:
                    if pt1["id"] != pt2["id"] and (pt2["id"], pt1["id"]) not in visted and reg1 != reg2:
                        visted.add((pt1["id"], pt2["id"]))
                        edge = {"pt1": pt1, "pt2": pt2,
                                "dist": distPoints(pt1["loc"][0], pt1["loc"][1], pt2["loc"][0], pt2["loc"][1]),
                                "polyline": polyline.encode([pt1["loc"], pt2["loc"]])}
                        edges.append(edge)

    with open("./static/data/ex_edges.json", "w+") as wf:
        json.dump(edges, wf, indent=4)

    return edges


def getEdge(edges, p1, p2):
    for e in edges:
        if e["pt1"]["id"] == p1 and e["pt2"]["id"] == p2:
            return e
        if e["pt1"]["id"] == p2 and e["pt2"]["id"] == p1:
            e["polyline"] = polyline.encode(list(reversed(polyline.decode(e["polyline"]))))
            temp = e["pt1"]
            e["pt1"] = e["pt2"]
            e["pt2"] = temp
            return e
    return -1


def search(edges, start, end, N):
    INF = int(1e9)

    adj = [[] for _ in range(N)]
    for e in edges:
        adj[e["pt1"]["id"]].append([e["dist"], e["pt2"]["id"]])
        adj[e["pt2"]["id"]].append([e["dist"], e["pt1"]["id"]])

    dist = [INF for _ in range(N)]
    prev = [None for _ in range(N)]

    dist[start] = 0
    pq = []
    visited = set()

    heappush(pq, (0, start))

    while pq:  # main loop
        cd, u = heappop(pq)  # shortest unvisited u
        if u in visited:
            continue
        visited.add(u)
        for d, v in adj[u]:
            if v in visited:
                continue
            if dist[v] > dist[u] + d:
                dist[v] = dist[u] + d
                prev[v] = u
                heappush(pq, (dist[v], v))

    route = []
    cur = end
    while cur is not None:
        route.append(cur)
        cur = prev[cur]

    route.reverse()
    r_route = []
    for i in range(len(route) - 1):
        r_route.append(getEdge(edges, route[i], route[i + 1]))

    return {"total_dist": dist[end], "route": r_route}


def reid_edges(edges, name_to_door):
    for e in edges:
        e["pt1"]["id"] = name_to_door[e["pt1"]["name"]]
        e["pt2"]["id"] = name_to_door[e["pt2"]["name"]]

    return edges


def route_dist(route):
    dist = 0
    for e in route["route"]:
        t_dist = distPoints(*e["pt1"]["loc"], *e["pt2"]["loc"])
        dist += t_dist
    return dist
