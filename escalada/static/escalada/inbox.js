document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.enroll-link').forEach(link => {
        link.onclick = function(){
            enrollButton('/enroll', link.dataset.climbclass)
        }
    })
})

function enrollButton(url, classSelected){
    let request = new XMLHttpRequest();
    let method = 'GET';
    request.open(method, url);
    request.onload = function () {
        // the response is the rendered HTML
        // which django sends as return render(response, "your_template.html", context)
        document.querySelector('#index').style.display = 'none';
        var formDiv = document.querySelector('#enroll-buy-form');
        formDiv.innerHTML = request.response;
        formDiv.innerHTML = document.querySelector('#enroll').innerHTML;
        formDiv.querySelector('#id_climbClass').value = classSelected;
        // This is the important part
        // Set that HTML to the new, templated HTML returned by the server
      };
      request.send();
}