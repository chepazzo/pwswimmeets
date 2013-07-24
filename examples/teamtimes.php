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
    <div id='teamtimestable' style="width: 900px; height: 500px;">
    </div><!-- id='teamtimestable' -->
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
    var name = '<?php echo $name; ?>';
    var loaded = { 'googlechart':false,'chartdata':false,'teamtimes':false };
    var chartdata = [];
    var charthead = [];
    var teamtimes = {'data':[],'head':['Season Best','Season Seed','Improved','Number of Best Times']};

    function INIT() {
        initTabs();
        google.load("visualization", "1", {packages:["corechart","table"]});
        google.setOnLoadCallback(function(){loadData();});
    }

    function loadData() {
        console.log('sending /cgi-bin/getteambesttimedata.py?team='+team);
        getJSON('/cgi-bin/getteambesttimedata.py','team='+team,gotBestTimes);
    }

    function datesort(a,b) { 
        return new Date(a['date']) - new Date(b['date']);
        //return (new Date(b['date'].replace(/-/g,'/')) < new Date(a['date'].replace(/-/g,'/')))
    }

    function eventsort(a,b) { 
        return (a['event'] < b['event']);
    }

    function gotTeamTimes(obj) {
        /*
        res = {
            'name':swim_name,
            'stroke':stroke_name,
            'best':{'date':bestdate,'fintime':finbest,'hmstime':secs2hms(finbest)},
            'seed':{'date':seeddate,'fintime':finseed,'hmstime':secs2hms(finseed)},
            'improve':imp,
            'numbest':numbest
        }
        */
        loaded.teamtimes = true;
        //var dataobjsort = obj.sort(eventsort);
        for (var e in obj) {
            var eobj = obj[e];
            var row = [eobj['name'],eobj['stroke']];
            var best = {'f':eobj['best']['hmstime'],'v':eobj['best']['fintime']};
            var seed = {'f':eobj['seed']['hmstime'],'v':eobj['seed']['fintime']};
            var imp = eobj['improve'];
            var numb = eobj['numbest'];
            row.push(best);
            row.push(seed);
            row.push(imp);
            row.push(numb);
            teamtimes.data.push(row);
        }
        drawTimesTable();
    }

    function drawTimesTable() {
        //if (!(loaded.googlechart && loaded.teamtimes)) { console.log('Times Table data not ready yet.'); return; }
        var dataTable = new google.visualization.DataTable();
        MISHAP.TimesTable = dataTable;
        dataTable.addColumn('string', 'Swimmer');
        dataTable.addColumn('string', 'Stroke');
        for (var i=0;i<teamtimes.head.length; i++) {
            header = teamtimes.head[i];
            dataTable.addColumn('number', header)
        }
        for (i=0;i<teamtimes.data.length;i++) {
            dataTable.addRow(teamtimes.data[i]);
        }
        var chart = new google.visualization.Table(document.getElementById('teamtimestable'));
        chart.draw(dataTable);//, options);
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
