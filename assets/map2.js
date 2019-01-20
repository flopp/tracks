var map = null;
var polyline = null;
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
                        load(hash);
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
        console.log('activate', hash);
        tracksList.children('li').each(function (i) {
            var li_hash = $(this).data('id');
            console.log(li_hash);
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


function load(hash) {
    url = '/assets/track-' + hash + '.json';
    $.getJSON('/assets/track-' + hash + '.json')
        .done(function(data) {
            tracks.activateTrack(hash);
            if (polyline === null) {
                polyline = L.polyline(data.polyline, {color: 'red'});
                polyline.addTo(map);
            } else {
                polyline.setLatLngs(data.polyline);
            }
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
    stamen_terrain.addTo(map);
    map.setView([47.985285, 7.908278], 13);

    var sidebar = L.sidebar('#map-ui')
        .addTo(map);

    tracks = L.tracks({
         position: 'topright',
         sidebar: sidebar
    }).addTo(map);

    L.zoom({
         position: 'topright',
         sidebar: sidebar
    }).addTo(map);

    load(data[0].hash);
}