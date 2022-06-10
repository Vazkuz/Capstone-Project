document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.enroll-link').forEach(link => {
        link.onclick = function(){
            buyButton('/enroll', '#enroll', '#buy-form', '#id_climbClass', link.dataset.climbclass, true)
        }
    })
    document.querySelectorAll('.buy-coupon-link').forEach(link => {
        link.onclick = function(){
            buyButton('/buyCoupon', '#buy-coupon', '#buy-form', '#id_coupon', link.dataset.climbclass, false)
        }
    })
})

function buyButton(url, buyDiv, divToPlace, formSelect, classSelected, prePopulate){
    let request = new XMLHttpRequest();
    let method = 'GET';
    request.open(method, url);
    request.onload = function () {
        // the response is the rendered HTML
        // which django sends as return render(response, "your_template.html", context)
        document.querySelector('#index').style.display = 'none';
        var formDiv = document.querySelector(divToPlace);
        formDiv.innerHTML = request.response;
        formDiv.innerHTML = document.querySelector(buyDiv).innerHTML;
        if (prePopulate){
            formDiv.querySelector(formSelect).value = classSelected;
        }
        // This is the important part
        // Set that HTML to the new, templated HTML returned by the server
      };
      request.send();
}