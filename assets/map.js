var map = null;
var infoWindow = null;
var prevNext = null;
var zoomFit = null;

function init() {
    var InfoWindow = L.Control.extend({
        options: {
            position: 'bottomleft'
        },

        initialize: function () {
            //this.toggleButton = null;

            this.startTime = null;
            this.endTime = null;
            this.location = null;
            this.distance = null;
            this.elapsedTime = null;
            this.timerTime = null;
            this.activityType = null;
            this.poi = null;

            this.tr_startTime = null;
            this.tr_location = null;
            this.tr_distance = null;
            this.tr_elapsedTime = null;
            this.tr_timerTime = null;
            this.tr_activityType = null;
            this.tr_poi = null;
        },

        onAdd: function (map) {
            var self = this;
            var container = L.DomUtil.create('div', 'leaflet-bar infowindow');

            var table = L.DomUtil.create('table', 'infowindow-table', container);

            this.tr_startTime = this.createTr(table, "Time:", this.startTime);
            this.tr_location = this.createTr(table, "Location:", this.location);
            this.tr_poi = this.createTr(table, "POI:", this.poi);
            this.tr_activityType = this.createTr(table, "Type:", this.activityType);
            this.tr_distance = this.createTr(table, "Distance:", this.distance);
            this.tr_timerTime = this.createTr(table, "Timer:", this.timerTime);
            this.tr_elapsedTime = this.createTr(table, "Elapsed:", this.elapsedTime);
            return container;
        },

        createTr: function(table, key, value) {
            var tr = L.DomUtil.create('tr', 'row', table);
            var td1 = L.DomUtil.create('th', 'key', tr);
            td1.innerHTML = key;
            var td2 = L.DomUtil.create('td', 'value', tr);
            if (value !== null) {
                td2.innerHTML = value;
            } else {
                td2.innerHTML = "n/a";
            }
            return tr;
        },

        updateTr: function(tr, value) {
            if (tr === null) {
                return;
            }
            var td = tr.childNodes[1];

            if (value !== null) {
                td.innerHTML = value;
            } else {
                td.innerHTML = "n/a";
            }
        },

        setLocation: function (location) {
            this.location = location;
            this.updateTr(this.tr_location, location);
        },

        setStartTime: function (time) {
            this.startTime = time;
            this.updateTr(this.tr_startTime, time);
        },

        setEndTime: function (time) {
        },

        setType: function (t) {
            this.activityType = t;
            this.updateTr(this.tr_activityType, t);
        },

        setPOI: function (p) {
            this.poi = p;
            this.updateTr(this.tr_poi, p);
        },

        setDistance: function (distance) {
            this.distance = distance;
            this.updateTr(this.tr_distance, distance);
        },

        setElapsedTime: function (duration) {
            this.elapsedTime = duration;
            this.updateTr(this.tr_elapsedTime, duration);
        },

        setTimerTime: function (duration) {
            this.timerTime = duration;
            this.updateTr(this.tr_timerTime, duration);
        },
    });



    var PrevNextControl = L.Control.extend({
        options: {
            position: 'topright'
        },

        initialize: function () {
            this.prev = '#';
            this.prevButton = null;
            this.next = '#';
            this.nextButton = null;
        },

        onAdd: function (map) {
            var self = this;
            var container = L.DomUtil.create('div', 'leaflet-prevnext leaflet-bar');

            this.prevButton = L.DomUtil.create('a', 'leaflet-prevnext-button', container);
            this.prevButton.setAttribute('role', 'button');
            this.prevButton.innerHTML = '<';
            this.prevButton.href = this.prev;
            if (this.prev == '#') {
                L.DomUtil.addClass(this.prevButton, 'leaflet-disabled');
            }

            this.nextButton = L.DomUtil.create('a', 'leaflet-prevnext-button', container);
            this.nextButton.setAttribute('role', 'button');
            this.nextButton.innerHTML = '>';
            this.nextButton.href = this.next;
            if (this.next == '#') {
                L.DomUtil.addClass(this.nextButton, 'leaflet-disabled');
            }

            return container;
        },

        setPrev: function(url) {
            this.prev = url;
            if (this.prevButton) {
                L.DomUtil.removeClass(this.prevButton, 'leaflet-disabled');
                this.prevButton.href = url;
            }
        },

        setNext: function(url) {
            this.next = url;
            if (this.nextButton) {
                L.DomUtil.removeClass(this.nextButton, 'leaflet-disabled');
                this.nextButton.href = url;
            }
        },
    });

    var ZoomFitControl = L.Control.extend({
        options: {
            position: 'topleft'
        },

        initialize: function () {
            this.button = null;
            this.function = null;
        },

        onAdd: function (map) {
            var self = this;
            var container = L.DomUtil.create('div', 'leaflet-bar');

            this.button = L.DomUtil.create('a', 'leaflet-zoomfit-button', container);
            this.button.setAttribute('role', 'button');
            this.button.innerHTML = 'F';

            if (this.function === null) {
                L.DomUtil.addClass(this.button, 'leaflet-disabled');
            } else {
                this.button.onclick = this.function;
            }

            return container;
        },

        setFunction: function(f) {
            this.function = f;
            if (this.button) {
                L.DomUtil.removeClass(this.button, 'leaflet-disabled');
                this.button.onclick = f;
            }
        },
    });

    var stamen_terrain = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg', {
        attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
        maxZoom: 14,
        subdomains: 'abcd'
    });

    var opentopomap = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        attribution: 'Map tiles by <a href="http://opentopomap.org">OpenTopoMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
        maxZoom: 15,
        subdomains: 'abc'
    });

    map = L.map('map', {zoomDelta: 0.25, zoomSnap: 0, layers: [stamen_terrain]});

    //var baseMaps = {'Terrain': stamen_terrain};
    //L.control.layers(baseMaps).addTo(map);

    zoomFit = new ZoomFitControl();
    map.addControl(zoomFit);

    prevNext = new PrevNextControl();
    map.addControl(prevNext);

    infoWindow = new InfoWindow();
    map.addControl(infoWindow);
}
