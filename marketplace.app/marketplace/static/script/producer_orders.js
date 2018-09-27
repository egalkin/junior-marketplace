if ($('main.producer-orders').length > 0) {

    let isInViewport = function (element) {
        let elementTop = element.offset().top;
        let elementBottom = elementTop + element.outerHeight();

        let viewportTop = $(window).scrollTop();
        let viewportBottom = viewportTop + $(window).height();

        return elementBottom > viewportTop && elementTop < viewportBottom;
    };

    $('#changeOrderStatusBtnTable').click(function () {
        let change_status_btn = $('#changeOrderStatusBtnTable');
        $('#changeOrderStatusSelectTable').removeAttr('disabled');
        change_status_btn.css('display', 'none');
        $('#saveStatusOrderBtnTable').css('display', 'block');
    });

    // ========= Chat functionality start =========
    var current_date = null;
    var orders_with_unread_messages = new Set();

    namespace = '/chat';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function () {
        socket.emit('connected', {data: 'I\'m connected!'});
    });

    function adjustHeaderMessageBadge() {
        $.get("/api/v1/chat/unread/" + localStorage.getItem("globalUserId"),
            function (numberOfMessages, status) {
                $('#numberOfUnreadMessagesBadge').html(numberOfMessages);
            });
    }

    function setUnreadMessagesToZero(id) {
        if (orders_with_unread_messages.has(id)) {
            orders_with_unread_messages.delete(id);
            // Удаляем бадж с кнопки "Связаться с производителем
            $('#talkToConsumer' + id).html(' Связаться с покупателем ');
            // В данном случае entity - это человек, чьи сообщения были непрочитаны.
            $.post('/api/v1/chat',
                {
                    order_id: id,
                    entity: 'consumer'
                },
                function (data) {
                    adjustHeaderMessageBadge();
                })
        }
    }


    function appendMessage(data) {
        let chatWindow = $('#chat' + data['room']);
        // Если сообщения относятся к разным дням, то прикрепляем разделитель формата 02.07.2018
        let message_date = data.timestamp.split(' ')[1].split('.');
        // parseInt(message_date[1])-1 потому что Date принимает индекс месяца, а отсчёт начинается с нуля
        let new_date = new Date(parseInt(message_date[2]), parseInt(message_date[1]) - 1, parseInt(message_date[0]));
        if ((current_date - new_date) !== 0) {
            chatWindow.append(
                '<div class="date-divider">' + message_date[0] + "." + message_date[1] + "." + message_date[2] + '</div>'
            );
            current_date = new_date;
        }
        // прикрепляем сообщение
        chatWindow.append(
            '<div class="order-dialog__item">' +
            '<div class="row order-dialog__header">' +
            '<div class="col-4 col-sm-2 order-dialog__photo">' +
            '<img src="/' + data['photo_url'] + '" alt="">' +
            '</div>' +
            '<div class="col-8 col-sm-7 order-dialog__name">' +
            '<p class="main-text">' + data['username'] + '</p>' +
            '<p class="main-text">' + data['body'] + '</p>' +
            '</div>' +
            '<div class="col-8 col-sm-3 order-dialog__date">' +
            '<p>' + data['timestamp'].split(' ')[0] + '</p>' +
            '</div>' +
            '</div>' +
            '</div>'
        );
        // скроллим до дна окна с сообщениями
        chatWindow.scrollTop(1E10);
    }

    socket.on('response', function (data) {
        appendMessage(data);
        // добавляем id заказа в нерпочитанные сообщения
        orders_with_unread_messages.add(data['room']);
        // Если окно чата видно на экране, то сразу удаляем сообщение из непрочитанных. Если нет, то удалим по скроллу.
        // Если нет, то удалим при следующем открытии чата.
        if (isInViewport($('#chat' + data['room']))) {
            setUnreadMessagesToZero(data['room'])
        }
    });

    function load_message_history(order_id) {
        $.get("/api/v1/chat/" + order_id,
            function (messages) {
                for (let i = 0; i < messages.length; i++) {
                    appendMessage(messages[i]);
                }
                setUnreadMessagesToZero(order_id);
            })
    }

    function joinRoom(order_id) {
        socket.emit('join', {
            room: order_id
        });
        return false;
    }

    function startDialog(order_id) {
        $('#talkToConsumer' + order_id).hide();
        $("#orderDialog" + order_id).show();
        load_message_history(order_id);
        joinRoom(order_id);
    }

    function sendToRoom(order_id) {
        let inputField = $("#orderDialogMessage" + order_id);
        socket.emit('send_to_room', {
            room: order_id,
            body: inputField.val(),
            entity: 'producer'
        });
        inputField.val('').focus()
    }

    // ========= Chat functionality end =========
    // ===============================   AJAX   ===============================

    let currentOrders;

    // data for request to get filtered orders
    let orderFilter = {
        producer_id: null,
        order_status: null,
        page: 1,
    };

    $(window).on('resize scroll', function () {
        let element = $('.pageNumber');
        if (element.length > 0 && isInViewport(element)) {
            element.remove();
            orderFilter['page'] = element.attr("data-page-number");
            update_orders_page(orderFilter);
        }

        for (let id of orders_with_unread_messages.keys()) {
            let lastElement = $('#chat' + id + ' div:last-child');
            if (lastElement.length > 0) {
                if (isInViewport(lastElement)) {
                    // Сразу удаляем из сэта, чтобы по следующему скроллу не включать его в цикл
                    orders_with_unread_messages.delete(id);
                    // Удаляям бадж с кнопки "Связаться с производитлем
                    $('#talkToConsumer' + id).html(' Связаться с производителем ');
                    // В данном случае entity - это человек, чьи сообщения были непрочитаны.
                    $.post('/api/v1/chat',
                        {
                            order_id: id,
                            entity: 'consumer'
                        },
                        function (data) {
                            adjustHeaderMessageBadge();
                        })
                }
            }
        }
    });


    // get and set producer id in orderFilter
    let addr = window.location + '';
    addr = addr.split('/');
    var producer_id = addr[addr.length - 2];
    orderFilter['producer_id'] = producer_id;

    function fill_order_filter(orderFilter) {
        orderFilter['order_status'] = $('#statuses option:selected').text();
    }

    function delete_current_orders() {
        let producerOrderSectionTable = document.getElementById("producerOrderSectionTable");
        while (producerOrderSectionTable.firstChild) {
            producerOrderSectionTable.removeChild(producerOrderSectionTable.firstChild);
        }
    }

    function add_new_orders_table_view(orders, page) {
        for (var i = 0; i < orders.length; i++) {
            $("#producerOrderSectionTable").append(
                '<div class="container table_container">' +
                '<div class="table_global_row">' +
                '<div class="table_global_cell">' +
                '<div>Номер заказа</div>' +
                '<div class="main-text" id="orderIdTable' + orders[i].id + '">' + orders[i].id + '</div>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<div>Покупатель</div>' +
                '<div class="main-text">' + orders[i].first_name + ' ' + orders[i].last_name + '</div>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<div>Телефон</div>' +
                '<div class="main-text">' + orders[i].consumer_phone + '</div>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<div>E-mail</div>' +
                '<div class="main-text">' + orders[i].consumer_email + '</div>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<div>Дата заказа</div>' +
                '<div class="main-text">' + orders[i].order_timestamp + '</div>' +
                '</div>' +
                '</div>' +
                '<div class="table_global_row">' +
                '<div class="table_global_cell">' +
                '<div>Товар</div>' +
                '<div id="innerTableProductName' + orders[i].id + '"></div>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<div>Цена</div>' +
                '<div id="innerTableProductPrice' + orders[i].id + '"></div>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<div>Артикул</div>' +
                '<div id="innerTableProductId' + orders[i].id + '"></div>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<div>Количество</div>' +
                '<div id="innerTableProductQuantity' + orders[i].id + '"></div>' +
                '</div>' +
                '</div>' +
                '<div id="innerTableProductsSection' + orders[i].id + '"></div>' +
                '<div class="table_global_row">' +
                '<div class="table_global_cell">' +
                '<div>Способ доставки</div>' +
                '<div class="main-text">' + orders[i].delivery_method + '</div>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<div>Адрес</div>' +
                '<div class="main-text">' + orders[i].delivery_address + '</div>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<div>Сумма заказа</div>' +
                '<div class="main-text">' + orders[i].total_cost + '</div>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<div>Статус заказа</div>' +
                '<select class="form-control select-order-status" id="changeOrderStatusSelectTable' + orders[i].id + '" name="subcategory" onchange="orderStatusOnChange(' + orders[i].id + ')">' +
                '<option value="Не обработан">Не обработан</option>' +
                '<option value="Обрабатывается">Обрабатывается</option>' +
                '<option value="Отправлен">Отправлен</option>' +
                '<option value="Готов к самовывозу">Готов к самовывозу</option>' +
                '<option value="Завершён">Завершён</option>' +
                '</select>' +
                '</div>' +
                '<div class="table_global_cell">' +
                '<button class="btn btn-success common-view-btn save-status-order-btn" id="saveStatusOrderBtnTable' + orders[i].id + '" onclick="saveOrderStatusClicked(' + orders[i].id + ')">Сохранить</button>' +
                '</div>' +
                '</div>' +
                '<button type="button" class="btn btn-primary connect-customer-table" id="talkToConsumer' +
                orders[i].id +
                '" onclick="startDialog(' +
                orders[i].id +
                ')"> Связаться с покупателем </button>' +
                // chat window interface start
                '<section class="container order-dialog" id="orderDialog' + orders[i].id + '">' +
                '<div class="message-history" id="chat' + orders[i].id + '">' +
                '</div>' +
                '<div class="order-dialog__form col-12 col-lg-10">' +
                '<textarea type="text" class="form-control" rows="4" id="orderDialogMessage' + orders[i].id + '" name="orderDialogMessage">' +
                '</textarea>' +
                '<div class="order-dialog__btn-block">' +
                '<button class="btn btn-secondary" onclick="sendToRoom(' + orders[i].id + ')">Отправить</button>' +
                '</div>' +
                '</div>' +
                '</section>' +
                // chat window interface end
                '</div>'
            );
            let items = orders[i]['items'];
            for (let p = 0; p < items.length; p++) {
                $("#innerTableProductName" + orders[i].id).append(
                    '<div class="main-text">' + items[p].name + '</div>'
                );
                $("#innerTableProductPrice" + orders[i].id).append(
                    '<div class="main-text">' + items[p].price + '/' + items[p].measurement_unit + '</div>'
                );
                $("#innerTableProductId" + orders[i].id).append(
                    '<div class="main-text">' + items[p].id + '</div>'
                );
                $("#innerTableProductQuantity" + orders[i].id).append(
                    '<div class="main-text">' + items[p].quantity + '</div>'
                );
            }

            if (orders[i].unread_consumer_messages) {
                // Это нужно для того, чтобы отправлять запросы для определённых заказов, а не всех.
                orders_with_unread_messages.add(orders[i].id);
                // Отображаем бадж на кнопках "Связаться с производителем".
                $('#talkToConsumer' + orders[i].id).html(' Связаться с покупателем <span id="messageBadge' +
                    orders[i].id + '" class="badge badge-pill badge-secondary message-badge">' +
                    orders[i].unread_consumer_messages + '</span> ')
            }
        }
        let next_page_number = page;
        if (next_page_number) {
            $("#mainProducerOrderSection").append(
                '<div data-page-number="' + next_page_number + '" class="pageNumber" style="width: 1px; height: 1px;" id="page' + next_page_number + '"></div>'
            );
        }
    }

    // Set the right status of each order
    function set_selected_options(orders) {
        for (let i = 0; i < orders.length; i++) {
            let currentSelectTable = document.getElementById('changeOrderStatusSelectTable' + orders[i].id);
            for (var o = 0; o < currentSelectTable.options.length; o++) {
                if (currentSelectTable.options[o].value === currentOrders[i].status) {
                    currentSelectTable.options[o].selected = 'selected'
                }
            }
        }
    }

    // if a different order status is selected, show "save" button
    function orderStatusOnChange(i) {
        $('#saveStatusOrderBtnTable' + i).show();
    }


    function changeOrderStatusInDB(order_id, order_status, i) {
        $.ajax({
            url: "/api/v1/orders/" + order_id,
            type: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({status: order_status}),
            success: function (data, status) {
                $('#saveStatusOrderBtnTable' + i).hide();
                var hulla = new hullabaloo();
                hulla.send("Статус заказа изменен", "secondary");
            }
        })
    }

    // on click of "save" button: get the new selected status, order id and send a request
    function saveOrderStatusClicked(i) {
        let select = document.getElementById("changeOrderStatusSelectTable" + i);
        let order_status = select.options[select.selectedIndex].value;
        let order_id = document.getElementById("orderIdTable" + i).innerHTML;
        changeOrderStatusInDB(order_id, order_status, i)
    }


    function display_new_orders(orderFilter) {
        $.post('/api/v1/producers/filtered_orders',
            orderFilter,
            function (orders, status) {
                currentOrders = orders.orders;
                add_new_orders_table_view(orders.orders, orders.page);
                set_selected_options(orders.orders);
                // hide all "save" buttons until a new status is selected
                let items = orders.orders;
                for (let i = 0; i < items.length; i++) {
                    $("#saveStatusOrderBtnTable" + items[i].id).hide();
                }
            });
    }


    function update_orders_page(orderFilter) {
        fill_order_filter(orderFilter);
        display_new_orders(orderFilter);
    }


// update orders on change of the main select
    $('#statuses').change(function () {
        delete_current_orders();
        orderFilter['page'] = 1;
        update_orders_page(orderFilter);
    });
    update_orders_page(orderFilter);

}
