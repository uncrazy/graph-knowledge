window.addEventListener("message", receiveMessage, false);

function receiveMessage(event)
{
    let origin = event.origin || event.originalEvent.origin;
    // For Chrome, the origin property is in the event.originalEvent object.

    console.log(event.data);

    let inIds = event.data['inIds'];
    let outIds = event.data['outIds'];
    let metric = event.data['metric'];

    inIds.forEach((el, index) => {
       inIds[index] = el['name'];
    });

    outIds.forEach((el, index) => {
       outIds[index] = el['name'];
    });

    document.getElementById("inIds").value = inIds.join('%');
    document.getElementById("outIds").value = outIds.join('%');
    document.getElementById("metric").value = metric;

    console.log("values")
    console.log(document.getElementById("outIds").value);
    let button = document.getElementById("button");
    if (event.data){
        document.getElementById("button").click();
        console.log("clicked");
    }

}
