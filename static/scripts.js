// Function to initialize the map
function initMap() {
    var mapDiv = document.getElementById('map');
    if (!mapDiv) return; // Exit if map div is not found

    var map = new google.maps.Map(mapDiv, {
        center: {lat: 39.9526, lng: -75.1652}, // Philadelphia coordinates
        zoom: 12
    });
}

// Function to format duration in a human-readable format
function formatDuration(durationInSeconds) {
    var hours = Math.floor(durationInSeconds / 3600);
    var minutes = Math.floor((durationInSeconds % 3600) / 60);
    return hours + ' hours ' + minutes + ' mins';
}

// Function to update the dashboard with insights data
function updateDashboard(data) {
    var insightsContainer = document.getElementById('insights-container');
    if (!insightsContainer) return; // Exit if insights container is not found

    insightsContainer.innerHTML = ''; // Clear previous content

   // Display error message if present
    if (data.error) {
        var errorMessage = '';
        if (data.invalid_input === 'origin') {
            errorMessage = data.error;
            document.getElementById('origin').focus(); // Focus on origin input field
        } else if (data.invalid_input === 'destination') {
            errorMessage = data.error;
            document.getElementById('destination').focus(); // Focus on destination input field
        } else {
            errorMessage = data.error;
        }
        insightsContainer.innerHTML = '<div class="alert alert-danger" role="alert">' + errorMessage + '</div>';
        return; // Exit function if error exists
    }

    // Display weather data
    var weatherCard = document.createElement('div');
    weatherCard.classList.add('card', 'mb-3');
    weatherCard.innerHTML = `
        <div class="card-header">Weather Data</div>
        <div class="card-body">
            <p>Temperature: ${data.weather_data.temperature}°C</p>
            <p>Weather Conditions: ${data.weather_data.weather_conditions}</p>
            <p>Wind Speed: ${data.weather_data.wind_speed} m/s</p>
            <p>Humidity: ${data.weather_data.humidity}%</p>
            <p>Visibility: ${data.weather_data.visibility}</p>
            <p>Sunrise: ${data.weather_data.sunrise}</p>
            <p>Sunset: ${data.weather_data.sunset}</p>
        </div>
    `;
    insightsContainer.appendChild(weatherCard);

    // Display traffic data
    var trafficCard = document.createElement('div');
    trafficCard.classList.add('card', 'mb-3');
    trafficCard.innerHTML = `
        <div class="card-header">Traffic Data</div>
        <div class="card-body">
            <p>Duration: ${data.traffic_data.duration}</p>
            <p>Distance: ${data.traffic_data.distance}</p>
        </div>
    `;
    insightsContainer.appendChild(trafficCard);

    // Display alternative routes
    var routesCard = document.createElement('div');
    routesCard.classList.add('card', 'mb-3');
    routesCard.innerHTML = `
        <div class="card-header">Alternative Routes</div>
        <div class="card-body">
            <ul>
                ${data.alternative_routes.map(route => `<li>${route.duration} - ${route.distance}</li>`).join('')}
            </ul>
        </div>
    `;
    insightsContainer.appendChild(routesCard);

    // Display traffic incidents if available
    if (data.traffic_incidents && data.traffic_incidents.length > 0) {
        var incidentsCard = document.createElement('div');
        incidentsCard.classList.add('card', 'mb-3');
        incidentsCard.innerHTML = `
            <div class="card-header">Traffic Incidents</div>
            <div class="card-body">
                <ul>
                    ${data.traffic_incidents.map(incident => `<li>${incident.name} - ${incident.location}</li>`).join('')}
                </ul>
            </div>
        `;
        insightsContainer.appendChild(incidentsCard);
    }

    // Display optimal departure time if available
    if (data.optimal_departure_time) {
        var departureCard = document.createElement('div');
        departureCard.classList.add('card', 'mb-3');
        departureCard.innerHTML = `
            <div class="card-header">Optimal Departure Time</div>
            <div class="card-body">
                <p>${data.optimal_departure_time}</p>
            </div>
        `;
        insightsContainer.appendChild(departureCard);
    }

    // Display public transit data if available
    if (data.public_transit_data) {
        var transitCard = document.createElement('div');
        transitCard.classList.add('card', 'mb-3');
        transitCard.innerHTML = `
            <div class="card-header">Public Transit Data</div>
            <div class="card-body">
                <ul id="transit-routes-list"></ul>
            </div>
        `;
        insightsContainer.appendChild(transitCard);

        // Display transit routes and steps
        var transitRoutesList = document.getElementById('transit-routes-list');
        data.public_transit_data.routes.forEach(function (route) {
            var routeSummary = document.createElement('li');
            routeSummary.textContent = 'Transit Route: ' + route.summary;

            var stepsList = document.createElement('ul');
            route.legs[0].steps.forEach(function (step) {
                if ('transit_details' in step) {
                    var transitDetails = step.transit_details;
                    var stepText = 'Take ' + transitDetails.line.name + ' ' +
                        transitDetails.headsign + ' from ' +
                        transitDetails.departure_stop.name + ' to ' +
                        transitDetails.arrival_stop.name;
                    var stepListItem = document.createElement('li');
                    stepListItem.textContent = stepText;
                    stepsList.appendChild(stepListItem);
                }
            });

            routeSummary.appendChild(stepsList);
            transitRoutesList.appendChild(routeSummary);
        });
    }
}


// Form submission event listener
document.addEventListener('DOMContentLoaded', function() {
    var trafficForm = document.getElementById('traffic-form');
    if (!trafficForm) return; // Exit if form is not found

    trafficForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission
        var formData = new FormData(this); // Get form data

        fetch('/insights', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Log the response data
            updateDashboard(data); // Update the dashboard with insights data
        })
        .catch(error => {
            console.error('Error:', error);
            // Display error message on the screen
            document.getElementById('insights-container').innerHTML = '<div class="alert alert-danger" role="alert">An error occurred. Please try again later.</div>';
        });
    });
});


// Ensure map initialization when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initMap();
});
