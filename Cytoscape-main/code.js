var cy = cytoscape({
  container: document.getElementById('cy'),
  elements: [
  // nodes
  { data: { id: 'Kanyakumari'},position:{x: -215.4187962413053,y: 1348.1750790521237}},
  { data: { id: 'Nagarcoil'},position: {x: -247.55036593669726,y: 1325.1284884433087}},
  { data: { id: 'Srivaikuntam'},position: {x: -39.59549170631298,y: 1258.2368026368888}},
  { data: { id: 'Tirunelveli'},position: {x: -173.5149154795372,y: 1254.560983639972}},
  { data: { id: 'Tenkashi'},position: {x: -272.50384982285607,y: 1213.5209733763365}},
  { data: { id: 'Tuticorin'},position: {x: 9.234544127120419,y: 1240.2564279902608}},
  { data: { id: 'Chennai'},position: {x: 223.83204254777985,y: 742.2300863371852}},
  { data: { id: 'Kovilpatti'},position: {x: -81.8745342744307,y: 1199.9766249074698}},
  { data: { id: 'Virudunagar'},position: {x: -172.98361267598182,y: 1157.7787359635938}},
  { data: { id: 'Rameshwaram'},position: {x: 96.50745080650097,y: 1192.304281463129}},
  { data: { id: 'Ramanathapuram'},position: {x: 77.78820965849212,y: 1173.6053654956243}},
  { data: { id: 'Paramakuddi'},position: {x: 56.32514808699366,y: 1159.296657781292}},
  { data: { id: 'Sivagangai'},position: {x: 23.847846190553852,y: 1113.6944170988652}},
  { data: { id: 'Madurai'},position: {x: -140.70229252426773,y: 1111.3096324798098}},
  { data: { id: 'Tirumangalam'},position: {x: -155.01100023860005,y: 1130.387909432253}},
  { data:{  id: "Teni"},position: {x: -262.3263080960924,y: 1097.000924765477}},
  { data:{  id: "Dindugal"},position: {x: -155.872542805859,y: 1060.5572934048566}},
  { data:{  id: "Kodaikanal"},position: {x: -274.7938661931468,y: 1056.721121682686}},
  { data:{  id: "Tirumayam"},position: {x: 84.8472327603445,y: 1093.1647530433065}},
  { data:{  id: "Pudukottai"},position: {x: 76.21584638546068,y: 1058.6392075437714}},
  { data:{  id: "Pollachi"},position: {x: -335.21357081733333,y: 1020.2774903220657}},
  { data:{  id: "Tiruchirapalli"},position: {x: -56.132078029424136,y: 993.4242882668716}},
  { data:{  id: "Thanjavur"},position: {x: 29.22274278887116,y: 984.7929018919878}},
  { data:{  id: "Karur"},position: {x: -177.9305302083398,y: 986.7109877530731}},
  { data:{  id: "Tiruppur"},position: {x: -288.2204672207437,y: 968.4891720727629}},
  { data:{  id: "Coimbatore"},position: {x: -379.329545622295,y: 982.8748160309026}},
  { data:{  id: "Kumbakonam"},position: {x: 104.02809137119725,y: 963.6939574200499}},
  { data:{  id: "Erode"},position: {x: -256.5720505128366,y: 935.881712434313}},
  { data:{  id: "Thiruvarur"},position: {x: 137.59459394018987,y: 1011.6461039471818}},
  { data:{  id: "Nagapattinam"},position: {x: 175.95631116189554,y: 1016.4413185998951}},
  { data:{  id: "Karaikal"},position: {x: 165.40683892592645,y: 994.3833311974143}},
  { data:{  id: "Ariyalur"},position: {x: 81.0110610381739,y: 939.7178841564836}},
  { data:{  id: "Mayiladuthurai"},position: {x: 157.73449548158538,y: 946.431184670282}},
  { data:{  id: "Chidambaram"},position: {x: 180.75152581460884,y: 925.3322401983439}},
  { data:{  id: "Attur"},position: {x: -181.76670193051038,y: 919.5779826150881}},
  { data:{  id: "Salem"},position: {x: -216.2922474300455,y: 904.2332957264058}},
  { data:{  id: "Omalur"},position: {x: -234.51406311035578,y: 875.4620078101266}},
  { data:{  id: "Dharmapuri"},position: {x: -230.67789138818517,y: 849.5678486854752}},
  { data:{  id: "Cuddalore"},position: {x: 175.9563111618956,y: 891.7657376293514}},
  { data:{  id: "Villupuram"},position: {x: 140.47172273181778,y: 875.4620078101265}},
  { data:{  id: "Tirupattur"},position: {x: -106.00231041764158,y: 812.165174394312}},
  { data:{  id: "Arani"},position: {x: 22.509442275072647,y: 824.6327324913664}},
  { data:{  id: "Vellore"},position: {x: -47.50069165454031,y: 779.5577147558621}},
  { data:{  id: "Chengalpattu"},position: {x: 175.95631116189557,y: 836.141247657878}},
  { data:{  id: "Arakkonam"},position: {x: 44.5674296775535,y: 776.6805859642341}},
  { data:{  id: "Tiruvallur"},position: {x: 125.12703584313547,y: 777.6396288947767}},
  { data:{  id: "Udagamandalam"},position: {x: -451.25776541299325,y: 924.3731972678013}},




  //edges
  {data: {id: 'cape-ncj', source: 'Kanyakumari', target: 'Nagarcoil', "weight": 20.2}},
  {data: {id: 'cape-ten', source: 'Kanyakumari', target: 'Tirunelveli', "weight": 76.04}},
  {data: {id: 'ten-sri', source: 'Tirunelveli', target: 'Srivaikuntam', "weight": 22.2}},
  {data: {id: 'ten-tsi', source: 'Tirunelveli', target: 'Tenkashi', "weight": 60.2}},
  {data: {id: 'ten-tn', source: 'Tirunelveli', target: 'Tuticorin', "weight": 51.2}},
  {data: {id: 'ten-cvp', source: 'Tirunelveli', target: 'Kovilpatti', "weight": 61.6}},
  {data: {id: 'cvp-vpt', source: 'Kovilpatti', target: 'Virudunagar', "weight": 50.7}},
  {data: {id: 'vpt-tmq', source: 'Virudunagar', target: 'Tirumangalam', "weight": 32.9}},
  {data: {id: 'vpt-svg', source: 'Virudunagar', target: 'Sivagangai', "weight": 98.4}},
  {data: {id: 'vpt-pmk', source: 'Virudunagar', target: 'Paramakuddi', "weight": 80.8}},
  {data: {id: 'tmq-mdu', source: 'Tirumangalam', target: 'Madurai', "weight": 23.3}},
  {data: {id: 'mdu-tni', source: 'Madurai', target: 'Teni', "weight": 76.4}},
  {data: {id: 'mdu-svg', source: 'Madurai', target: 'Sivagangai', "weight": 44.9}},
  {data: {id: 'svg-pmk', source: 'Sivagangai', target: 'Paramakuddi', "weight": 49.1}},
  {data: {id: 'pmk-rmp', source: 'Paramakuddi', target: 'Ramanathapuram', "weight": 39.5}},
    //{data: {id: 'rmp-mpm', source: 'Ramanathapuram', target: 'mandapam', "weight": }},
    //{data: {id: 'mpm-rmw', source: 'Mandapam', target: 'Rameshwaram', "weight": 10}},
    {data: {id: 'mdu-dn', source: 'Madurai', target: 'Dindugal', "weight": 64.4}},
    {data: {id: 'dn-knl', source: 'Madurai', target: 'Kodaikanal', "weight": 116.2}},
    {data: {id: 'dn-tri', source: 'Dindugal', target: 'Tiruchirapalli', "weight": 99.2}},
    {data: {id: 'tri-tnj', source: "Tiruchirapalli", target: 'Thanjavur', "weight": 47}},
    {data: {id: 'tnj-pdk', source: 'Thanjavur', target: 'Pudukottai', "weight": 62.7}},
    {data: {id: 'tnj-kmb', source: 'Thanjavur', target: 'Kumbakonam', "weight": 39.1}},
    {data: {id: 'tnj-ero', source: 'Thanjavur', target: 'Erode', "weight": 205}},
    {data: {id: 'trp-ero', source: 'Tiruppur', target: 'Erode', "weight": 54}},
    {data: {id: 'cmb-trp', source: 'Coimbatore', target: 'Tiruppur', "weight": 55.7}},
    {data: {id: 'pol-cmb', source: 'Pollachi', target: 'Coimbatore', "weight": 43.4}},
    {data: {id: 'cmb-udm', source: 'Coimbatore', target: 'Udagamandalam', "weight": 84.8}},
    {data: {id: 'ero-slm', source: 'Erode', target: 'Salem', "weight": 63.3}},
    {data: {id: 'slm-atr', source: 'Salem', target: 'Attur', "weight": 55.9}},
    {data: {id: 'slm-olr', source: 'Salem', target: 'Omalur', "weight": 15.5}},
    {data: {id: 'olr-dmr', source: 'Omalur', target: 'Dharmapuri', "weight": 52.3}},
    {data: {id: 'atr-cdl', source: 'Attur', target: 'Cuddalore', "weight": 145.1}},
    {data: {id: 'kmb-mld', source: 'Kumbakonam', target: 'Mayiladuthurai', "weight": 35.5}},
    {data: {id: 'mld-cdm', source: 'Mayiladuthurai', target: 'Chidambaram', "weight": 46.5}},
    {data: {id: 'cdm-cdl', source: 'Chidambaram', target: 'Cuddalore', "weight": 43}},
    {data: {id: 'cdl-vpm', source: 'Cuddalore', target: 'Villupuram', "weight": 44.1}},
    {data: {id: 'vpm-arn', source: 'Villupuram', target: 'Arani', "weight": 94.4}},
    {data: {id: 'arn-vle', source: 'Arani', target: 'Vellore', "weight": 37.5}},
    {data: {id: 'vle-arm', source: 'Vellore', target: 'Arakkonam', "weight": 79.3}},
    {data: {id: 'vpm-cpt', source: 'Villupuram', target: 'Chengalpattu', "weight": 105.7}},
    {data: {id: 'cpt-chn', source: 'Chengalpattu', target: 'Chennai', "weight": 59.9}},
    {data: {id: 'tri-kr', source: 'Tiruchirapalli', target: 'Karur', "weight": 82}},
    {data: {id: 'kr-ero', source: 'Karur', target: 'Erode', "weight": 66.8}},
    {data: {id: 'pol-knl', source: 'Pollachi', target: 'Kodaikanal', "weight": 129.1}},
    {data: {id: 'arm-tvl', source: 'Arakkonam', target: 'Tiruvallur', "weight": 34.6}},
    {data: {id: 'tvl-chn', source: 'Tiruvallur', target: "Chennai", "weight": 44.7}},
    {data: {id: 'slm-tpr', source: 'Salem', target: "Tirupattur", "weight": 44.7}},
    {data: {id: 'tpr-cvle', source: 'Tirupattur', target: "Vellore", "weight": 44.7}},
    {data: {id: 'mld-kal', source: 'Mayiladuthurai', target: "Karaikal", "weight": 41.9}},
    {data: {id: 'kmb-nag', source: 'Kumbakonam', target: "Nagapattinam", "weight": 70.4}},
    {data: {id: 'svg-trm', source: 'Sivagangai', target: "Tirumayam", "weight": 61.3}},
    {data: {id: 'trm-pdk', source: 'Tirumayam', target: "Pudukottai", "weight": 19.1}},
    {data: {id: 'tri-arl', source: 'Tiruchirapalli', target: "Ariyalur", "weight": 19.1}},
    {data: {id: "arl-vpm", source: 'Ariyalur', target:"Villupuram", "weight": 19.1}}




],




    layout:{
      name:"preset"
    },
    style:[
        {
            selector:"node",
            style: {
                "shape":"star",
                height:"15px",
                width:"15px",
                "background-color":"blue",
                label:"data(id)"
            }
        },
        {
            selector: "edge",
            style: {
                "curve-style": "straight",
                "//curve-style": "hay-stack",
                //"control-point-distance":"20px",
                //"control-point-weight":"0.7",
                "line-color":"black"
                
            }
        },
        {
            selector: ".highlighted",
            style: {
                "background-color":"green",
                "line-color":"red"
            }
        },
    ]

});
cy.once("tap", "node", function (evt) {
    start = evt.target.id()
    console.log("START")
    cy.once("tap", "node", function (evt) {
    end = evt.target.id()
    console.log("END")
    var dijkstra = cy.elements().dijkstra("#"+start, function (edge) {
        return edge.data("weight")
    }, false)
    var bfs = dijkstra.pathTo(cy.$("#"+end))
    var x = 0
    var highlight = function () {
        var el = bfs[x]
        el.addClass("highlighted")
        if (x < bfs.length) {
            x++
            setTimeout(highlight, 500)
        }
    }
    highlight()


})


})



