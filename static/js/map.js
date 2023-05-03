function loadGoogleMapsAPI() {
    let script = document.createElement('script');
    script.type = 'text/javascript';
    script.async = true;
    script.defer = true;
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&callback=initMap&libraries=geometry`;
    document.body.appendChild(script);
}
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 53.52656767335504, lng: -113.5255622404301 },
    zoom: 15,
    styles: [
        { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
        { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
        { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
        {
          featureType: "administrative.locality",
          elementType: "labels.text.fill",
          stylers: [{ color: "#d59563" }],
        },
        {
          featureType: "poi",
          elementType: "labels.text.fill",
          stylers: [{ color: "#d59563" }],
        },
        {
          featureType: "poi.park",
          elementType: "geometry",
          stylers: [{ color: "#263c3f" }],
        },
        {
          featureType: "poi.park",
          elementType: "labels.text.fill",
          stylers: [{ color: "#6b9a76" }],
        },
        {
          featureType: "road",
          elementType: "geometry",
          stylers: [{ color: "#38414e" }],
        },
        {
          featureType: "road",
          elementType: "geometry.stroke",
          stylers: [{ color: "#212a37" }],
        },
        {
          featureType: "road",
          elementType: "labels.text.fill",
          stylers: [{ color: "#9ca5b3" }],
        },
        {
          featureType: "road.highway",
          elementType: "geometry",
          stylers: [{ color: "#746855" }],
        },
        {
          featureType: "road.highway",
          elementType: "geometry.stroke",
          stylers: [{ color: "#1f2835" }],
        },
        {
          featureType: "road.highway",
          elementType: "labels.text.fill",
          stylers: [{ color: "#f3d19c" }],
        },
        {
          featureType: "transit",
          elementType: "geometry",
          stylers: [{ color: "#2f3948" }],
        },
        {
          featureType: "transit.station",
          elementType: "labels.text.fill",
          stylers: [{ color: "#d59563" }],
        },
        {
          featureType: "water",
          elementType: "geometry",
          stylers: [{ color: "#17263c" }],
        },
        {
          featureType: "water",
          elementType: "labels.text.fill",
          stylers: [{ color: "#515c6d" }],
        },
        {
          featureType: "water",
          elementType: "labels.text.stroke",
          stylers: [{ color: "#17263c" }],
        },
    ]});
    polyline = new google.maps.Polyline({
        geodesic: true,
        strokeColor: "#FF0000",
        strokeWeight: 2,
        strokeOpacity: 1.0,
        map: map
    });
    adjustMapHeight()
}
function adjustMapHeight() {
    mapContainer.style.height = `calc(100% - (${navbar.offsetHeight}px))`;
}

let polyline;
GOOGLE_MAPS_API_KEY = document.getElementById('GOOGLE_MAPS_API_KEY').value
navbar = document.getElementById('navbar')
mapContainer = document.getElementById('map-container')
form = document.getElementById('search-form')
start = document.getElementById('from')
end = document.getElementById('to')
myModal = new bootstrap.Modal(document.getElementById('duplicateLocationModal'))
loadGoogleMapsAPI()
window.initMap = initMap;

window.addEventListener('resize', adjustMapHeight, false)
const resize_ob = new ResizeObserver(adjustMapHeight)
resize_ob.observe(navbar)

// Handle the click and submit event and disable the browsers default action
// Make calls to our backend and then handle the response.
const formSubmitHandler = (event) => {
    event.preventDefault()
    api_endpoint = window.location.origin
    if (start.value === end.value) {
        myModal.toggle()
        return
    }
    try {
        fetch(`${api_endpoint}/api/?start=${start.value}&end=${end.value}`)
        .then((res ) => res.json())
        .then((res) => {
            polyline.setPath(google.maps.geometry.encoding.decodePath(res["polyline"]))
            console.log('from: ', start.value, 'to: ', end.value)
        })
    }
    catch (err) {
        console.log(err)
        myModal.toggle()
    }
}

form.addEventListener('submit', formSubmitHandler, false)