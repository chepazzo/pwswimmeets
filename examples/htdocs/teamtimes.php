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
    <style>
 .title {
    text-align: center;
    font-size: 3em;
 }
 #slides {
    width: 912px;
    margin:auto;
 }
    </style>
 </head>
  <body>
    <h1><?php echo $title; ?></h1>
    <div id=slides>
      <div id='slidestroke'>
        <div id='stroketimestable' style='width:900px;height:400px'></div>
      </div><!-- id='slidestroke' -->
      <div id='slideswimmers'>
        <div id='swimmertimestable' style='width:900px;height:400px'></div>
      </div><!-- id='slideswimmers' -->
    </div><!-- id=slides -->
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
    var name = '<?php echo $name; ?>';
    var loaded = { 'googlechart':false,'chartdata':false,'teamtimes':false };
    var chartdata = [];
    var charthead = [];
    var GLOBALS = [];
    var teamtimes = {'data':[],'head':['Season Seed','Season Best','Improved (secs)','Improved (%)','Improved (secs/meter)','# of Best Times']};
    var swimmertimes = {'data':[],'head':['Improved (secs)','# of Best Times']};

    function INIT() {
        initTabs();
        google.load("visualization", "1", {packages:["corechart","table"]});
        google.setOnLoadCallback(function(){loadData();});
    }

    function loadData() {
        console.log('sending /cgi-bin/getteambesttimedata.py?team='+team);
        getJSON('/cgi-bin/getteambesttimedata.py','team='+team,gotTeamTimes);
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
            'improveperc':impperc,
            'improveperm':impperm,
            'numbest':numbest
        }
        */
        loaded.teamtimes = true;
        //var dataobjsort = obj.sort(eventsort);
        for (var e in obj.bystroke) {
            var eobj = obj.bystroke[e];
            var row = [eobj['name'],eobj['stroke']];
            var seed = {'f':eobj['seed']['hmstime'],'v':eobj['seed']['fintime']};
            var best = {'f':eobj['best']['hmstime'],'v':eobj['best']['fintime']};
            var imp = eobj['improve'];
            var impcstr = eobj['improveperc'];
            var impmstr = eobj['improveperm'];
            if (imp == null) { imp = 0; }
            if (impcstr == null) { impcstr = 0; }
            if (impmstr == null) { impmstr = 0; }
            var impc = {'v':eobj['improveperc'],'f':impcstr.toString()+" %"};
            var impm = {'v':eobj['improveperm'],'f':impmstr.toString()+" sec/m"};
            var numb = eobj['numbest'];
            row.push(seed);
            row.push(best);
            row.push(imp);
            row.push(impc);
            row.push(impm);
            row.push(numb);
            teamtimes.data.push(row);
        }
        drawTimesTable();
        for (var e in obj.byswimmer) {
            var eobj = obj.byswimmer[e];
            var row = [eobj['name']];
            var numb = eobj['numbest'];
            var imp = eobj['totimp'];
            if (numb == null) { numb = 0; }
            if (imp == null) { imp = 0; }
            row.push(imp);
            row.push(numb);
            swimmertimes.data.push(row);
        }
        drawSwimmerTable();
    }

    function drawTimesTable() {
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
        var options = {
            'title':'Best Times By Stroke',
            'showRowNumber':true,
            'sortColumn':4,
            'sortAscending':false
        };
        TEAMCHART = new google.visualization.Table(document.getElementById('stroketimestable'));
        google.visualization.events.addListener(TEAMCHART, 'select', onSelectRow);
        TEAMCHART.draw(dataTable,options);
    }

    function drawSwimmerTable() {
        var dataTable = new google.visualization.DataTable();
        MISHAP.TimesTable = dataTable;
        dataTable.addColumn('string', 'Swimmer');
        for (var i=0;i<swimmertimes.head.length; i++) {
            header = swimmertimes.head[i];
            dataTable.addColumn('number', header)
        }
        for (i=0;i<swimmertimes.data.length;i++) {
            dataTable.addRow(swimmertimes.data[i]);
        }
        var options = {
            'title':'Best Times By Swimmer',
            'showRowNumber':true,
            'sortColumn':1,
            'sortAscending':false
        };
        SWIMMERCHART = new google.visualization.Table(document.getElementById('swimmertimestable'));
        google.visualization.events.addListener(SWIMMERCHART, 'select', onSelectRowSwimmer);
        SWIMMERCHART.draw(dataTable,options);//, options);
        //chart.draw(dataView, options);
    }

    function onSelectRow() {
        _onSelectRow(TEAMCHART);
    }

    function onSelectRowSwimmer() {
        _onSelectRow(SWIMMERCHART);
    }

    function _onSelectRow(chart) {
        var selection = chart.getSelection();
        for (var i = 0; i < selection.length; i++) {
            var item = selection[i];
            console.log(item);
            var swimmer = MISHAP.TimesTable.getValue(item.row, 0);
            var link = document.createElement('a');
            link.href = '/swimtimes.php?name='+swimmer;
            link.target = '_blank';
            document.getElementsByTagName('body')[0].appendChild(link);
            link.click();
        }
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
