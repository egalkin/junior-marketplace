var number_of_products_in_cart = 0;
var putToCart = function (consumer_id, product_id) {
    $.post("/api/v1/consumers/" + consumer_id + "/cart",
        {
            product_id: product_id,
            quantity: $(".product_quantity_input").val(),
            mode: 'inc'
        },
        function (data, status) {
            number_of_products_in_cart = 0;
            for (var k in data.items) {
                if (data.items.hasOwnProperty(k)) {
                    number_of_products_in_cart += parseInt(data.items[k]);
                }
            }
            document.getElementById('numberOfProductsInCart').innerHTML = number_of_products_in_cart;
        });
};

var getNumberOfProductsInCart;
if (localStorage.getItem("globalUserId") > 0) {
    $(document).ready(function () {
        var user_id = localStorage.getItem("globalUserId");
        getNumberOfProductsInCart = function (user_id) {
            $.get("/api/v1/consumers/" + user_id + "/cart/quantity",
                function (data, status) {
                    if (data.number_of_products) {
                        document.getElementById('numberOfProductsInCart').innerHTML = data.number_of_products;
                    }
                });
        };
        getNumberOfProductsInCart(user_id);
    });

}


function deleteProduct(product_id, producer_id, consumer_id) {
    $('#' + product_id).remove();
    var producer = $('#producer' + producer_id);
    $.post("/api/v1/consumers/" + consumer_id + "/cart",
        {
            product_id: product_id,
            mode: 'remove'
        },
        function (data, status) {
            number_of_products_in_cart = 0;
            for (var k in data.items) {
                if (data.items.hasOwnProperty(k)) {
                    number_of_products_in_cart += parseInt(data.items[k]);
                }
            }
            document.getElementById('numberOfProductsInCart').innerHTML = number_of_products_in_cart;

        });

    var products = producer.find('section');
    if (products.length == 0) {
        producer.remove();
    }
    var allProducerBlock = $('.notEmptyCart').find('section');
    if (allProducerBlock.length == 0) {
        $('.notEmptyCart').remove();
        $('#cartMain').append('<section class="container total_container py-4" id="emptyCart">\n' +
            '                 <h2>Ваша корзина пуста</h2>\n' +
            '            </section>')
    }
    countTotalCost();

}

function getProductsByUserId() {
    var user_id = localStorage.getItem("globalUserId");
    $.get("/api/v1/products/" + user_id + "/cart",
        function (products, status) {
            if (status) {
                getCartInformation(products);
            }
        }
    )
}

function getCartInformation(products) {
    var user_id = localStorage.getItem("globalUserId");
    $.get("/api/v1/consumers/" + user_id + "/cart",
        function (items, status) {
            if (status) {
                countTotalCostInner(items, products);
            }
        })
}

function countTotalCostInner(items, products) {
    var total = 0;
    for (var i in items.items) {
        for (var p = 0; p < products.length; p++) {
            if (i == products[p].id) {
                var sum = items.items[i] * products[p].price;
                total += sum;
            }
        }
    }
    $('#totalCost').html(total);
}

function countTotalCost() {
    getProductsByUserId();
}

if (localStorage.getItem("globalUserId") > 0) {
    countTotalCost();
}

function changeQuantityOfProduct(product_id) {
    let quantity = $('#number' + product_id).val();
    var user_id = localStorage.getItem("globalUserId");
    $.post("/api/v1/consumers/" + user_id + "/cart",
        {
            product_id: product_id,
            quantity: quantity,
            mode: 'set'
        },
        function (data, status) {
            number_of_products_in_cart = 0;
            for (var k in data.items) {
                if (data.items.hasOwnProperty(k)) {
                    number_of_products_in_cart += parseInt(data.items[k]);
                }
            }
            document.getElementById('numberOfProductsInCart').innerHTML = number_of_products_in_cart;
        });
    countTotalCost();
}
