<?php

 $name = 'phelps, michael';

 if (isset($_GET['name'])) {
    $name = $_GET['name'];
 }
 $title = "Swim Stats for $name";

 ?>
<html>
  <head>
    <title><?php echo $title; ?></title>
 </head>
  <body>
    <h1><?php echo $title; ?></h1>
    <div id='slides' style="width: 900px; height: 500px;">
        <div id='slidechart'><div id="chart_div" style="width: 900px; height: 500px;"></div></div>
        <div id='slidetable'><div id="table_div" style="width: 900px; height: 500px;"></div></div>
        <div id='slidetimes'><div id="times_div" style="width: 900px; height: 500px;"></div></div>
    </div><!-- id='slides' -->
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
    var name = '<?php echo $name; ?>';
    var loaded = { 'googlechart':false,'chartdata':false,'besttimes':false };
    var chartdata = [];
    var charthead = [];
    var besttimes = {'data':[],'head':['Best Ever','Most Recent','Most Recent Seed','Season Seed','Meet Improved','Year Improved']};

    function INIT() {
        initTabs();
        google.load("visualization", "1", {packages:["corechart","table"]});
        google.setOnLoadCallback(function(){loadData();});
    }

    function loadData() {
        console.log('sending /cgi-bin/getchartdata.py?name='+name);
        getJSON('/cgi-bin/getchartdata.py','name='+name,gotChartData);
        console.log('sending /cgi-bin/getbesttimedata.py?name='+name);
        getJSON('/cgi-bin/getbesttimedata.py','name='+name,gotBestTimes);
    }

    function datesort(a,b) { 
        return new Date(a['date']) - new Date(b['date']);
        //return (new Date(b['date'].replace(/-/g,'/')) < new Date(a['date'].replace(/-/g,'/')))
    }

    function eventsort(a,b) { 
        return (a['event'] < b['event']);
    }

    function gotBestTimes(obj) {
        loaded.besttimes = true;
        var dataobjsort = obj.sort(eventsort);
        for (var e in dataobjsort) {
            var eobj = dataobjsort[e];
            var row = [eobj['event']];
            var yearbest = eobj['seasonbest']['fintime'];
            var best = eobj['best']['fintime'];
            var last = eobj['last']['fintime'];
            var prev = eobj['prev']['fintime'];
            var seed = eobj['seed']['fintime'];
            var changed = null;
            var improved = null;
            var lastdate = new Date(eobj['last']['date']);
            var today = new Date();
            if (lastdate.getFullYear() == today.getFullYear()) {
                if (prev) {
                    changed = prev - last;
                    changed = changed.toFixed(2);
                }
                if (seed) {
                    improved = seed - best;
                    improved = improved.toFixed(2);
                }
            }
            var bestf = null;
            var lastf = null;
            var prevf = null;
            var seedf = null;
            var changedf = null;
            var improvedf = null;
            if (best) { bestf = {'f':eobj['best']['hmstime'],'v':eobj['best']['fintime']}; }
            if (last) { lastf = {'f':eobj['last']['hmstime'],'v':eobj['last']['fintime']}; }
            if (prev) { prevf = {'f':eobj['prev']['hmstime'],'v':eobj['prev']['fintime']}; }
            if (seed) { seedf = {'f':eobj['seed']['hmstime'],'v':eobj['seed']['fintime']}; }
            if (changed) { changedf = {'f':changed,'v':parseFloat(changed)}; }
            if (improved) { improvedf = {'f':improved,'v':parseFloat(improved)}; }
            row.push(bestf);
            row.push(lastf);
            row.push(prevf);
            row.push(seedf);
            row.push(changedf);
            row.push(improvedf);
            besttimes.data.push(row);
        }
        drawTimesTable();
    }
    function gotChartData(obj) {
        loaded.chartdata = true;
        var dataobj = [];
        for (var d in obj['data']) { dataobj.push(obj.data[d]); }
        for (var d in obj['events']) { charthead.push(obj.events[d]); }
        var dataobjsort = dataobj.sort(datesort);
        //console.log(dataobjsort);
        for (var d in dataobjsort) {
        //for (var d=0;d<keys.length; d++) {
            //console.log(dataobjsort[d]);
            var evobj = dataobjsort[d];
            if (typeof(evobj['date']) == 'undefined') { continue; }
            var row = [evobj['date']]
            for (var i=0;i<charthead.length; i++) {
                var e = charthead[i];
                //console.log(e);
                if (typeof(evobj[e]) == 'undefined') {
                    row.push(null);
                    continue;
                }
                var vtime = evobj[e]['fintime'];
                var ftime = evobj[e]['hmstime'];
                var pwtime = evobj[e]['PWT'];
                if (pwtime) {
                    ftime = "("+pwtime+") "+ftime;
                }
                row.push({'v':vtime,'f':ftime});
                //row.push(evobj[e]);
            }
            //row = [evobj['date'],evobj.IM,evobj.Back,evobj.Breast,evobj.Fly,evobj.Free];
            chartdata.push(row);
        }
        //for (var d in dataobj) { console.log('nosrt: '+dataobj[d]['date']); }
        //console.log(chartdata);
        drawChart()
        drawHistoryTable()
    }

    function drawChart() {
        //if (!(loaded.googlechart && loaded.chartdata)) { console.log('Chart data not ready yet.'); return; }
        var dataTable = new google.visualization.DataTable();
        dataTable.addColumn('string', 'Date');
        for (var i=0;i<charthead.length; i++) {
            var stroke = charthead[i];
            dataTable.addColumn('number', stroke)
        }
        for (i=0;i<chartdata.length;i++) {
            dataTable.addRow(chartdata[i]);
        }
        var dataView = new google.visualization.DataView(dataTable);
        var options = {
            title: 'Swim Times - '+name,
            //legend:{position:'in'},
            //curveType: 'function',
            interpolateNulls: true,
            hAxis: { slantedText: true }
        };
        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(dataView, options);
    }

    function drawHistoryTable() {
        //if (!(loaded.googlechart && loaded.besttimes)) { console.log('History Table data not ready yet.'); return; }
        var dataTable = new google.visualization.DataTable();
        dataTable.addColumn('string', 'Date');
        for (var i=0;i<charthead.length; i++) {
            var stroke = charthead[i];
            dataTable.addColumn('number', stroke)
        }
        for (i=0;i<chartdata.length;i++) {
            dataTable.addRow(chartdata[i]);
        }
        /*
        var dataView = new google.visualization.DataView(dataTable);
        var options = {
            title: 'Abbica\'s Swim Times',
            //legend:{position:'in'},
            //curveType: 'function',
            interpolateNulls: true,
            hAxis: { slantedText: true }
        };
        */
        var chart = new google.visualization.Table(document.getElementById('table_div'));
        chart.draw(dataTable);//, options);
        //chart.draw(dataView, options);
    }

    function drawTimesTable() {
        //if (!(loaded.googlechart && loaded.besttimes)) { console.log('Times Table data not ready yet.'); return; }
        var dataTable = new google.visualization.DataTable();
        dataTable.addColumn('string', 'Stroke');
        for (var i=0;i<besttimes.head.length; i++) {
            header = besttimes.head[i];
            dataTable.addColumn('number', header)
        }
        //dataTable.addColumn('number', 'Best');
        //dataTable.addColumn('number', 'Last');
        //dataTable.addColumn('number', 'Meet Improved');
        //dataTable.addColumn('number', 'Year Improved');
        for (i=0;i<besttimes.data.length;i++) {
            dataTable.addRow(besttimes.data[i]);
        }
        /*
        var dataView = new google.visualization.DataView(dataTable);
        var options = {
            title: 'Abbica\'s Swim Times',
            //legend:{position:'in'},
            //curveType: 'function',
            interpolateNulls: true,
            hAxis: { slantedText: true }
        };
        */
        var chart = new google.visualization.Table(document.getElementById('times_div'));
        chart.draw(dataTable);//, options);
        //chart.draw(dataView, options);
    }

    function getJSON(script,formData,callback,instance) {
        var req    = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (req.readyState == 4) { if (req.status == 200) {
                if (typeof(instance) == 'undefined') {
                    callback(JSON.parse(req.responseText));
                } else {
                    callback.call(instance,JSON.parse(req.responseText));
                }
            } }
        };
        req.open('POST', script, true);
        if (isString(formData)) {
            req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        }
        req.send(formData);
    }
    function isString(o) { return Object.prototype.toString.call(o) === '[object String]'; }

    INIT();
    </script>
  </body>
