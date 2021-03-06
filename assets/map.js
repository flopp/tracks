var map = null;
var polyline = null;
var circles = null;
var tracks = null;

function zoomFit() {
    if (!map || !polyline) {
        return;
    }
    map.fitBounds(polyline.getBounds(), {padding: [16, 16]});
}

L.sidebar = function(selector) {
    var control = {},
        sidebar = $(selector),
        current = $(),
        currentButton  = $(),
        map;

    control.addTo = function (_) {
        map = _;
        return control;
    };

    control.addPane = function(pane) {
        pane
            .hide()
            .appendTo(sidebar);
    };

    control.togglePane = function(pane, button) {
        current
            .hide()
            .trigger('hide');

        currentButton
            .removeClass('active');

        if (current === pane) {
            $(sidebar).hide();
            current = currentButton = $();
        } else {
            $(sidebar).show();
            current = pane;
            currentButton = button || $();
        }

        map.invalidateSize({pan: false, animate: false});

        current
            .show()
            .trigger('show');

        currentButton
            .addClass('active');
    };

    return control;
};

L.tracks = function (options) {
    var control = L.control(options),
        tracksList = null;


    control.onAdd = function (map) {
        var $container = $('<div>')
            .attr('class', 'control-tracks');

        var button = $('<a>')
            .attr('class', 'control-button')
            .attr('href', '#')
            .html('<span class="icon"><i class="fas fa-list-ul"></i></span>')
            //.html('<span class="icon tracks"></span>')
            .on('click', toggle)
            .appendTo($container);

        var $ui = $('<div>')
            .attr('class', 'tracks-ui');

        $('<div>')
            .attr('class', 'sidebar_heading')
            .appendTo($ui)
            .append(
                $('<span>')
                    .attr('class', 'close')
                    .html('<i class="fas fa-times"></i>')
                    .bind('click', toggle))
            .append(
                $('<h4>')
                .text('Tracks'));

        tracksList = $('<ul>')
            .attr('class', 'track-items')
            .appendTo($ui);

        data.forEach(function(track) {
            var $li = $('<li>')
                .attr('class', 'track-item')
                .attr('data-id', track.hash)
                .on('click', (function() {
                    var hash = track.hash;
                    return function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        load(hash, track.pois);
                    }
                 })())
                .appendTo(tracksList);

            $('<span>')
                .text(track.start_time)
                .appendTo($li);
            $('<br>').appendTo($li);
            $('<span>')
                .text(track.type)
                .appendTo($li);
            $('<br>').appendTo($li);
            $('<span>')
                .text(track.location)
                .appendTo($li);
            if (track.pois.length > 0) {
                $('<br>').appendTo($li);
                $('<span>')
                    .text(track.pois.map(p => p.name).join(', '))
                    .appendTo($li);
            }
            $('<br>').appendTo($li);
            $('<span>')
                .text(track.distance)
                .appendTo($li);
        });
        options.sidebar.addPane($ui);

        $ui
            .on('show', shown)
            .on('hide', hidden);

        map.on('baselayerchange', updateButton);

        updateButton();

        function shown() {
            map.on('zoomend baselayerchange', update);
            //$section.load('/key', update);
        }

        function hidden() {
            map.off('zoomend baselayerchange', update);
        }

        function toggle(e) {
            e.stopPropagation();
            e.preventDefault();
            if (!button.hasClass('disabled')) {
                options.sidebar.togglePane($ui, button);
            }
            //$('.leaflet-control .control-button').tooltip('hide');
        }

        function updateButton() {
        }

        function update() {
        }

        return $container[0];
    };

    control.activateTrack = function (hash) {
        tracksList.children('li').each(function (i) {
            var li_hash = $(this).data('id');
            if (li_hash == hash) {
                $(this).addClass('active');
            } else {
                $(this).removeClass('active');
            }
        });
    };

    return control;
};

L.layers = function (options) {
    var control = L.control(options),
        layersList = null;


    control.onAdd = function (map) {
        var $container = $('<div>')
            .attr('class', 'layers-tracks');

        var button = $('<a>')
            .attr('class', 'control-button')
            .attr('href', '#')
            .html('<span class="icon"><i class="fas fa-layer-group"></i></span>')
            .on('click', toggle)
            .appendTo($container);

        var $ui = $('<div>')
            .attr('class', 'layers-ui');

        $('<div>')
            .attr('class', 'sidebar_heading')
            .appendTo($ui)
            .append(
                $('<span>')
                    .attr('class', 'close')
                    .html('<i class="fas fa-times"></i>')
                    .bind('click', toggle))
            .append(
                $('<h4>')
                .text('Layers'));

        layersList = $('<ul>')
            .attr('class', 'layers-items')
            .appendTo($ui);

        options.layers.forEach(function(layer) {
            var $li = $('<li>')
                .attr('class', 'layers-item')
                .on('click', (function() {
                    var all = options.layers;
                    var lay = layer;
                    return function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        console.log(lay);
                        all.forEach(function(other) {
                            if (other['layer'] == lay['layer']) {
                                map.addLayer(other['layer'])
                            } else {
                                map.removeLayer(other['layer'])
                            }
                        });
                        map.fire('baselayerchange', {layer: lay['layer']});
                    }
                 })())
                .appendTo(layersList);

            $('<span>')
                .text(layer['name'])
                .appendTo($li);

            map.on('layeradd layerremove', function() {
                $li.toggleClass('active', map.hasLayer(layer['layer']));
            });
        });
        options.sidebar.addPane($ui);

        map.addLayer(options.layers[0].layer)

        function toggle(e) {
            e.stopPropagation();
            e.preventDefault();
            if (!button.hasClass('disabled')) {
                options.sidebar.togglePane($ui, button);
            }
        }

        return $container[0];
    };

    control.activateTrack = function (hash) {
        tracksList.children('li').each(function (i) {
            var li_hash = $(this).data('id');
            if (li_hash == hash) {
                $(this).addClass('active');
            } else {
                $(this).removeClass('active');
            }
        });
    };

    return control;
};

L.zoom = function (options) {
    var control = L.control(options);

    control.onAdd = function (map) {
        var $container = $('<div>')
            .attr('class', 'control-zoom');

        $('<a>')
            .attr('class', 'control-button zoomin')
            .attr('href', '#')
            .html('<span class="icon"><i class="fas fa-plus"></i></span>')
            .on('click', click_zoomIn)
            .on('dblclick', click_zoomIn)
            .appendTo($container);

        $('<a>')
            .attr('class', 'control-button zoomout')
            .attr('href', '#')
            .html('<span class="icon"><i class="fas fa-minus"></i></span>')
            .on('click', click_zoomOut)
            .on('dblclick', click_zoomOut)
            .appendTo($container);

        $('<a>')
            .attr('class', 'control-button zoomfit')
            .attr('href', '#')
            .html('<span class="icon"><i class="fas fa-expand-arrows-alt"></i></span>')
            .on('click', click_zoomFit)
            .on('dblclick', click_zoomFit)
            .appendTo($container);

        function click_zoomIn(e) {
            e.stopPropagation();
            e.preventDefault();
            map.zoomIn();
        }

        function click_zoomOut(e) {
            e.stopPropagation();
            e.preventDefault();
            map.zoomOut();
        }

        function click_zoomFit(e) {
            e.stopPropagation();
            e.preventDefault();
            zoomFit();
        }

        return $container[0];
    };

    return control;
};


function load(hash, pois) {
    url = '/assets/tracks/' + hash + '.json';
    $.getJSON(url)
        .done(function(data) {
            tracks.activateTrack(hash);
            if (polyline === null) {
                polyline = L.polyline(data.polyline, {color: 'red'});
                polyline.addTo(map);
            } else {
                polyline.setLatLngs(data.polyline);
            }

            if (circles) {
                circles.forEach(function(circle) {
                    map.removeLayer(circle);
                });
                circles = null;
            }

            circles = [];
            pois.forEach(function(poi) {
                circle = L.circle(L.latLng(poi.lat, poi.lng), {radius: 100, color: 'blue'});
                circle.addTo(map);
                circles.push(circle);
            });

            zoomFit();
        })
        .fail(function() {
            console.log("error");
        });
}

function init() {
    map = L.map('map', {zoomControl: false, zoomDelta: 0.25, zoomSnap: 0});

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

    var baseLayers = [
        {name: 'Stamen/Terrain', layer: stamen_terrain},
        {name: 'OpenTopoMap', layer: opentopomap}
    ];

    map.setView([47.985285, 7.908278], 13);

    var sidebar = L.sidebar('#map-ui')
        .addTo(map);

    tracks = L.tracks({
         position: 'topright',
         sidebar: sidebar
    }).addTo(map);

    L.layers({
        position: 'topright',
        sidebar: sidebar,
        layers: baseLayers
    }).addTo(map);

    L.zoom({
         position: 'topright',
         sidebar: sidebar
    }).addTo(map);

    load(data[0].hash, data[0].pois);
}
