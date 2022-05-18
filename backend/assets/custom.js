window.addEventListener("message", receiveMessage, false);

var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;

function receiveMessage(event)
{
    console.log(event.data);

    var inIds = event.data['inIds'];
    var outIds = event.data['outIds'];
    var metric = event.data['metric'];

    inIds.forEach((el, index) => {
       inIds[index] = el['name'];
    });

    outIds.forEach((el, index) => {
       outIds[index] = el['name'];
    });

    var input_in = document.getElementById("inIds");
    var input_out = document.getElementById("outIds");
    var input_metric = document.getElementById("metric");

    setter.call(input_in, inIds.join('%'));
    setter.call(input_out, outIds.join('%'));
    setter.call(input_metric, metric);

    console.log("values")
    console.log(document.getElementById("inIds").value);
    console.log(document.getElementById("outIds").value);

    var ev = new Event('input', { bubbles: true });
    input_in.dispatchEvent(ev);
    input_out.dispatchEvent(ev);
    input_metric.dispatchEvent(ev);

    if (event.data){
        document.getElementById("button").click();
        console.log("clicked");
    }

}
