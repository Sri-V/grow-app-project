new WOW().init();

function addProduct(i, name, alph_num_name, price, tags) {
    var row_num = i - (i % 4) // Get the correct row for the product
    $('#row-' + row_num).append("<!--New column-->\n" +
        "                <div class=\"col-lg-3 col-md-6 mb-4\">\n" +
        "                    <!--Card-->\n" +
        "                    <div class=\"card\">\n" +
        "                        <!--Card image-->\n" +
        "                        <div class=\"view overlay\">\n" +
        "                            <img src=\"https://mdbootstrap.com/img/Photos/Horizontal/E-commerce/Vertical/12.jpg\"\n" +
        "                                 class=\"card-img-top\" alt=\"\">\n" +
        "                            <a id=\"" + alph_num_name + "\"><div class=\"mask rgba-white-slight\"></div></a>\n" +
        "                        </div>\n" +
        "                        <!--Card image-->\n" +
        "                        <!--Card content-->\n" +
        "                        <div class=\"card-body text-center\">\n" +
        "                            <!--Category & Title-->\n" +
        "                            <a href=\"\" class=\"grey-text\">\n" +
        "                                <h5>Microgreen</h5>\n" +
        "                            </a>\n" +
        "                            <h5>\n" +
        "                                <strong>\n" +
        "                                    <a id=\"" + alph_num_name + "\" class=\"dark-grey-text\">" + name + "\n" +
        "                                    </a>\n" +
        "                                </strong>\n" +
        "                                        <a id=\"tags-"+alph_num_name+"\"></a>\n" +
        "                            </h5>\n" +
        "                            <h4 class=\"font-weight-bold blue-text\">\n" +
        "                                <strong>$" + price + "</strong>\n" +
        "                            </h4>\n" +
        "                        </div>\n" +
        "                    </div>\n" +
        "                </div> ")
    for (let tag of tags) {
        $("a#tags-"+ alph_num_name).append("<span class=\"badge badge-pill "+ tag.color +"\">"+ tag.name +"</span>")
    }

}