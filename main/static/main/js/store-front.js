document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.sidenav');
    var instances = M.Sidenav.init(elems, {/*options*/});
});

$(document).ready(function(){
    $('.sidenav').sidenav();
});
//
<div class="modal" id="search-preloader" style="height: auto;">
    <div class="modal-content">
        <div class="loader"></div>
    </div>
</div>
// Initialize modal box for messages
document.addEventListener('DOMContentLoaded', function() {
    var elems = document.getElementById('search-preloader');
    var instances = M.Modal.init(elems, {});
});
// Function to show search-preloader
function show_search_preloader() {
    var elem = document.getElementById('search-preloader');
    var instance = M.Modal.getInstance(elem);
    instance.open();
}
// Function to hide search-preloader
function close_search_preloader() {
    var elem = document.getElementById('search-preloader');
    var instance = M.Modal.getInstance(elem);
    instance.close();
}
// Perform search query
function search_product(search_text) {
    $.ajax({
        headers: {'X-CSRFToken': '{{ csrf_token }}'},
        url: "/search_query",
        type: "POST",
        dataType: "json",
        data: {
            search_text: search_text
        },
        beforeSend: function() {
            show_search_preloader();
        },
        success: function(){
            close_search_preloader();
            console.log('El exitoooo');
            //location.reload();
            ;
        },
        error: function(){
            close_search_preloader();
            console.log('Siguie intentando');
            //location.reload();
            ;
        }
    });

/*
    // Look for those words in current object
    var product_faltante = [];
    var dict = {};
    {% for product_faltante in ProductosAprobados_missing %}
        search_score = 0;
        for (i = 0; i < search_words.length; i++) {
            // Normalize string (eliminates accents)
            string_producto = String("{{ product_faltante.pa_product }}");
            string_producto = string_producto.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
            search_w = search_words[i];
            search_w = search_w.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
            
            // Look for matching word
            reg_ex = new RegExp('^(.*?(' + search_w + ')[^$]*)$', 'i');
            n = string_producto.search(reg_ex);
            search_score += n;
        };
        if (search_score == 0) {
            dict = {
                id: "{{ product_faltante.pa_ID }}",
                product: "{{ product_faltante.pa_product }}",
                img: "{{ product_faltante.pa_image.url }}",
                brand: "{{ product_faltante.pa_brand }}",
                score: search_score
            };
            product_faltante.push(dict);
        }
    {% endfor %}

    // Print remove current results and add new search results
    $("tr").remove(".c_products_to_add");
    {% for product_faltante in ProductosAprobados_missing %}
        for (i = 0; i < product_faltante.length; i++) {
            if (String("{{ product_faltante.pa_ID }}") == String(product_faltante[i].id)) {
                $("#products_to_add_container").append('<tr name="missing_products" class="c_products_to_add"><td><input type="checkbox" name="item_to_add" id="'+String(product_faltante[i].id)+'" class="form-check-input"></td><td><div class="m-r-10"><img src="'+String(product_faltante[i].img)+'" alt="IMG" class="rounded" width="45"></div></td><td>'+String(product_faltante[i].product)+'</td><td>'+String(product_faltante[i].brand)+'</td></tr>');
            }
        }
    {% endfor %}
};
*/