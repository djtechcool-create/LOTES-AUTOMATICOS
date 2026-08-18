var UI = false;
var FA;
var HA;
var s2s = true;
var lastContent;
var formErrors = 0;
var lastPending = 0;
var chronographInterval;
$(function () {

    jQuery.extend({
        postJSON: function (url, data, callBack) {
            return $.ajax({ type: 'POST', url: url, data: data, success: callBack, error: callBack, dataType: "json" });
        }
    });
    $(document)
        .ajaxSend(function (event, jqxhr, settings) { if (~settings.url.indexOf("/tracker/") === 0 && $.active === 1) { $('#loading').show(); chronograph(true); } })
        .ajaxComplete(function (event, jqxhr, settings) { if ($.active === 1) { $('#loading').hide(); chronograph(false); } });
    track();
    var tracker = setInterval(function () { track(); }, 30000);

});

function chronograph(start) {
    var lt = $("#loading-timer");
    if (start === true) {
        var sc = 0;
        var ms = 0;
        var ss = 0;
        var mm = 0;
        var hh = 0;
        var time;
        chronographInterval = setInterval(function () {
            if (ms === 99) {
                ms = 0;
            } else {
                ms++;
            }
            if (ms === 0) {
                if (ss === 59) {
                    ss = 0;
                } else {
                    ss++;
                }
            }
            if (ms === 0 && ss === 0) {
                if (mm === 59) {
                    mm = 0;
                } else {
                    mm++;
                }
            }
            if (ms === 0 && ss === 0 && mm === 0) {
                hh++;
            }
            time = ((hh < 10) ? ("0" + hh) : hh) + ":" + ((mm < 10) ? ("0" + mm) : mm) + ":" + ((ss < 10) ? ("0" + ss) : ss) + ":" + ((ms < 10) ? ("0" + ms) : ms);
            lt.text(time);
            //writeChronograph(time);
        }, 10
        );
    } else {
        clearInterval(chronographInterval);
        lt.text("00:00:00.000");
        //writeChronograph("00:00:00.000");
    }
}
function writeChronograph(time) {
    $("#loading-timer").text(time);
}
/*
function loadContent(content, name) {
    lastContent = { content: content, name: name };
    $("#texto").html(name);
    $("#mainBox").empty();
    $("#mainBox").load(content);
    if (!$(".navbar-toggle").hasClass("collapsed")) $(".navbar-toggle").trigger("click");
}*/

function loadContent(content, name) {
    lastContent = { content: content, name: name };
    $("#texto").html(name);

    $("body").append(`
        <div id="loading-overlay" class="position-fixed w-100 h-100 d-flex justify-content-center align-items-center" style="top: 0; left: 0; background: rgba(94, 110, 130, 0.4); z-index: 1050;">
            <div class="row align-items-center">
                <div class="col-lg-4">
                    <div class="lottie mx-auto" style="width: 120px; height: 120px" data-options='{"path":"lib/template/public/assets/img/animated-icons/infinite-loop.json"}'></div>
                </div>
            </div>
        </div>
    `);


    const lottieElements = document.querySelectorAll('.lottie');
    lottieElements.forEach(el => {
        const options = JSON.parse(el.getAttribute('data-options'));
        lottie.loadAnimation({
            container: el,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: options.path
        });
    });

    $("#mainBox").empty().append('<div id="loading">Cargando...</div>');
    $("#mainBox").load(content, function(response, status, xhr) {
        if (status === "error") {
            $("#mainBox").html('<p>Error al cargar el contenido.</p>');
        } else {
            $("#loading").remove();
        }
        $("#loading-overlay").remove();
    });

    if (!$(".navbar-toggler").hasClass("collapsed")) $(".navbar-toggler").trigger("click");
}



/*

function getJson(urlstr, params, elem, callBack) {
    var poststr = ($.type(params) === "object") ? $.param(params) : "";
    var request = $.postJSON(urlstr, poststr,
        function (data) {
            if ($.type(data) !== "undefined" && $.type(data.data) !== "undefined" && $.type(data.data[0]) !== "undefined") {
                if ($.type(callBack) === "function") {
                    callBack({ url: urlstr, params: params, elem: elem, data: data.data });
                }
            } else {
                if (elem === "ui") {
                    document.location = '/logout/';
                } else {
                    alert((($.type(data.data) !== "undefined" && $.type(data.data[0]) !== "undefined" && $.type(data.data[0].MSG) !== "undefined") ? "Error :\n\n" + data.data[0].MSG : ($.type(data.responseText) === "undefined" ? "No hay datos" : data.responseText)));
                }
            }
            request = null;
        }
    );
}*/
function getJson(urlstr, params, elem, callBack) {
    var poststr = ($.type(params) === "object") ? $.param(params) : "";
    var request = $.postJSON(urlstr, poststr, function (data) {
        if ($.type(data) !== "undefined" && $.type(data.data) !== "undefined" && $.type(data.data[0]) !== "undefined") {
            if ($.type(callBack) === "function") {
                callBack({ url: urlstr, params: params, elem: elem, data: data.data });
            }
        } else {
            if (elem === "ui") {
                document.location = '/logout/';
            } else {
                var errorMessage = (($.type(data.data) !== "undefined" && $.type(data.data[0]) !== "undefined" && $.type(data.data[0].MSG) !== "undefined") ? "Error :\n\n" + data.data[0].MSG : ($.type(data.responseText) === "undefined" ? "No hay datos" : data.responseText));
                showMessageModal(errorMessage);
            }
        }
        request = null;
    });
}

function showMessageModal(message) {
    $("#messageModalBody").text(message);
    $("#messageModal").modal('show');
}


function getJsonToForm(urlstr, params, form, elem, callBack) {
    getJson(urlstr, params, elem, function (data) { setJsonToForm(data, form, callBack); });
}
function setJsonToForm(data, form, callBack) {
    form.each(function () {
    });
    if ($.type(callBack) === "function") {
        data["form"] = form;
        callBack(data);
    }
}
function definirUI(data) {
    if (UI === false) {
        $.ajax('https://maps.googleapis.com/maps/api/js?signed_in=false&key=' + data.data[0].gmapk, {
            crossDomain: true,
            dataType: 'script'
        });
    }
    UI = data.data[0].u * 1;
    FA = data.data[0].f;
    HA = data.data[0].h;

    if ($("#mainMenu").html() === "") {        
        getJson("/?option=json", { json: 1027, uid: UI }, "me", construirMenu);              
    }
}
/*
function construirMenu(data) {
    console.log(data);

    if ($.type(data.data) !== "undefined" && $.type(data.data[0]) !== "undefined") {
        var temporal = $("<ul>");
        temporal.append($("<ul/>").addClass("navbar-nav flex-column mb-3").attr({ id: "navbarVerticalNav" }));
        for (var x in data.data) {
            if (data.data[x].PARENT === '0') {
                temporal.find("#navbarVerticalNav").append($("<li/>").addClass("nav-item").attr({ id: "men_0" + data.data[x].CHILD })
                    .append($("<a/>").addClass("nav-link dropdown-indicator").attr({ href: "#men_" + data.data[x].CHILD, "role": "button", "data-bs-toggle": "collapse", "aria-expanded": "false", "aria-controls": "men_" + data.data[x].CHILD })
                    .append($("<div/>").addClass("d-flex align-items-center")
                    .append($("<span/>").addClass("nav-link-icon")
                    .append($("<span/>").addClass(data.data[x].URL)))
                    .append($("<span/>").addClass("nav-link-text ps-1").text(data.data[x].TITLE)))));
            } else {
                if (data.data[x].URL === "") {
                    temporal.find("#men_0" + data.data[x].PARENT)
                        .append($("<ul/>").addClass("nav collapse").attr({ id: "men_" + data.data[x].PARENT })
                        .append($("<li/>").addClass("nav-item").attr({ id: "men_0" + data.data[x].CHILD })
                        .append($("<a/>").addClass("nav-link dropdown-indicator").attr({ href: "#men_" + data.data[x].CHILD, "data-bs-toggle": "collapse", "aria-expanded": "false", "aria-controls": "men_" + data.data[x].PARENT })
                        .append($("<div/>").addClass("d-flex align-items-center")
                        .append($("<span/>").addClass("nav-link-text ps-1").text(data.data[x].TITLE))))));
                } else {
                    temporal.find("#men_0" + data.data[x].PARENT)
                        .append($("<ul/>").addClass("nav collapse").attr({ id: "men_" + data.data[x].PARENT })
                        .append($("<li/>").addClass("nav-item").attr({ id: "men_0" + data.data[x].CHILD })
                        .append($("<a/>").addClass("nav-link").attr({ href: data.data[x].URL })
                        .append($("<div/>").addClass("d-flex align-items-center")
                        .append($("<span/>").addClass("nav-link-text ps-1").text(data.data[x].TITLE))))));
                }
            }
        }
        //temporal.append($("<li/>").attr({rel:"out"}).append($("<a/>").text("Salir").css({"color":"transparent"}).attr({"title":"Salir"}).addClass("icon-salir")));
        if ($("#mainMenu").html() !== temporal.html()) {
            $("#mainMenu").html(temporal.html());
            /*$("#mainMenu li").click(function(){
                            var rel=$(this).attr("rel");
                            var name=$("a",$(this)).text();
                            if(rel==="out"){
                                $('#loading').show();
                                chronograph(true);
                                window.location.href="/logout/?";
                            }else{
                                if(typeof(rel) !== 'undefined' && rel!==""){
                                    loadContent(rel,name);
                                }
                            }
                        });
        }
        $("#mainMenu").show();
        eventMenu();
    }
}*/
function construirMenu(data) {
    if ($.type(data.data) !== "undefined" && $.type(data.data[0]) !== "undefined") {
        var persona = data.data[0].PERSONA;
        $("#nameUser").text(persona);
        var temporal = $("<ul>");
        temporal.append($("<ul/>").addClass("navbar-nav flex-column mb-3").attr({ id: "navbarVerticalNav" }));
        for (var x in data.data) {
            if (data.data[x].PARENT === '0') {
                temporal.find("#navbarVerticalNav").append($("<li/>").addClass("nav-item").attr({ id: "men_0" + data.data[x].CHILD })
                    .append($("<a/>").addClass("nav-link dropdown-indicator collapsed principal-menu").attr({ href: "#men_" + data.data[x].CHILD, "role": "button", "data-bs-toggle": "collapse", "aria-expanded": "false", "aria-controls": "men_" + data.data[x].CHILD })
                    .append($("<div/>").addClass("d-flex align-items-center")
                    .append($("<span/>").addClass("nav-link-icon")
                    .append($("<span/>").addClass(data.data[x].URL)))
                    .append($("<span/>").addClass("nav-link-text ps-1").text(data.data[x].TITLE)))));
            } else {
                if (data.data[x].URL === "") {
                    temporal.find("#men_0" + data.data[x].PARENT)
                        .append($("<ul/>").addClass("nav collapse").attr({ id: "men_" + data.data[x].PARENT })
                        .append($("<li/>").addClass("nav-item").attr({ id: "men_0" + data.data[x].CHILD })
                        .append($("<a/>").addClass("nav-link dropdown-indicator collapsed").attr({ href: "#men_" + data.data[x].CHILD, "data-bs-toggle": "collapse", "aria-expanded": "false", "aria-controls": "men_" + data.data[x].PARENT })
                        .append($("<div/>").addClass("d-flex align-items-center")
                        .append($("<span/>").addClass("nav-link-text ps-1").text(data.data[x].TITLE))))));
                } else {
                    temporal.find("#men_0" + data.data[x].PARENT)
                        .append($("<ul/>").addClass("nav collapse").attr({ id: "men_" + data.data[x].PARENT })
                        .append($("<li/>").addClass("nav-item").attr({ id: "men_0" + data.data[x].CHILD })
                        .append($("<a/>").addClass("nav-link").attr({ href: "#", "data-url": data.data[x].URL })
                        .append($("<div/>").addClass("d-flex align-items-center")
                        .append($("<span/>").addClass("nav-link-text ps-1").text(data.data[x].TITLE))))));
                }
            }
        }
        if ($("#mainMenu").html() !== temporal.html()) {
            $("#mainMenu").html(temporal.html());
        }
        $("#mainMenu").show();
        eventMenu();

        
       /* $('#mainMenu').on('show.bs.collapse', '.collapse', function () {
            var target = $(this).attr('id');
            
            $('#mainMenu .principal-menu').each(function () {
                var otherTarget = $(this).attr('href').substring(1);
                if (otherTarget !== target && $('#' + otherTarget).hasClass('show')) {
                    $('#' + otherTarget).collapse('hide');
                }
            });
        });*/
    }
}

/*
function eventMenu() {
    var dropdownElements = document.querySelectorAll('.navbar a.dropdown-toggle');
    dropdownElements.forEach(function (dropdown) {
        dropdown.addEventListener('click', function (e) {
            e.preventDefault();
            var $el = $(this);
            var $parent = $el.offsetParent(".dropdown-menu");
            $el.parent("li").toggleClass('open');

            if (!$parent.parent().hasClass('nav')) {
                $el.next().css({ "top": $el[0].offsetTop, "left": $parent.outerWidth() - 4 });
            }
            $('.nav li.open').not($el.parents("li")).removeClass("open");
        });
    });
}*/
function eventMenu() {
    $('#mainMenu a[data-url]').on('click', function (e) {
        e.preventDefault();
        var url = $(this).data('url');
        var name = $(this).find('.nav-link-text').text();
        loadContent(url, name);
    });

    var dropdownElements = document.querySelectorAll('.navbar a.dropdown-toggle');
    dropdownElements.forEach(function (dropdown) {
        dropdown.addEventListener('click', function (e) {
            e.preventDefault();
            var $el = $(this);
            var $parent = $el.offsetParent(".dropdown-menu");
            $el.parent("li").toggleClass('open');

            if (!$parent.parent().hasClass('nav')) {
                $el.next().css({ "top": $el[0].offsetTop, "left": $parent.outerWidth() - 4 });
            }
            $('.nav li.open').not($el.parents("li")).removeClass("open");
        });
    });
}


function preparaFormaReporte(tipo,parametros){
    console.log(parametros);
    var forma=$("<form/>");
    for(var x in parametros){
        forma.append($("<input/>").attr({name:x,value:parametros[x],hidden:true}));
    }
    $("#downloader").html(forma.html()).prop({action:"/"+tipo+"/"}).submit().empty();
}
function creaPDF(parametros){
    preparaFormaReporte("pdf",parametros);
}
function creaXLS(parametros){
    preparaFormaReporte("xls",parametros);
}
function track() {
    var trackParams = (UI === false) ? { gmapk: "1" } : {};
    getJson("/tracker/?" + (new Date().getTime()), trackParams, "ui", function (data) { definirUI(data); setTimeout(function () { presentarTareasPendientes(data); }, 1500); });
}
function limpiaCombo(obj) {
    $(obj).empty();
    $(obj).append('<option value="" disabled selected>Sin datos...</option>');
}
function llenaCombo(obj, url, params, selected, callback, leyend) {
    limpiaCombo(obj);
    getJson(url, params, "cbo", function (data) { procesaCombo(data, obj, selected, leyend); if ($.type(callback) === "function") callback(); });
}
function procesaCombo(data, obj, selected, leyend) {
    $(obj).empty();
    if ($.type(leyend) === "undefined" || $.type(leyend) === "string" || leyend === true) {
        if ($.type(leyend) === "string")
            $(obj).append('<option value="" disabled selected>' + leyend + '</option>');
        else if ($(obj).prop("title") !== "") {
            $(obj).append('<option value="" disabled selected>' + $(obj).prop("title") + '</option>');
        } else
            $(obj).append('<option value="" disabled selected>Seleccione aquí...</option>');
    }
    for (var x in data.data) {
        $(obj).append($("<option/>").attr({ value: data.data[x].V }).text(data.data[x].T));
    }
    $(obj).val(selected);
}

function doMagic(magic = {}, callback) {
    var url = "/?";
    var params = {};
    for (var x in magic) {
        if (x !== 'params') {
            url = url + ((url === "/?") ? '' : '&') + x + '=' + magic[x];
        } else {
            params = magic[x];
        }
    }
    getJson(url, params, "cbo", function (data) { if ($.type(callback) === "function") callback(data); });
}

/*
function guardarFormulario(form, Json, callBack, byPassConfirm) {
    if (s2s === true) {
        var byPassConfirmation = byPassConfirm;
        if (byPassConfirmation !== true) {
            byPassConfirmation = confirm("\n\n¿Confirma que desea realizar la acción solicitada?.\n\n");
        }
        if (byPassConfirmation === true) {
            s2s = false;
            var url = '/?option=json&seed=' + (new Date().getTime());
            var params = { json: Json, uid: UI };
            var cnts = {};
            $(':input[name!="rp"][name!="q"][name!="qtype"]', form).each(function () {
                if ($(this).prop("name") !== "") {
                    if ($(this).prop("type") === "checkbox") {

                        var str = $(this).prop("name");
                        if ($.type(str.match(/\[(.*)\]/)) !== "null") {
                            if ($(this).prop("checked") === true) {
                                var key = str.replace("[" + (str.match(/\[(.*)\]/).pop()) + "]", "");
                                var value = str.match(/\[(.*)\]/).pop();
                                if ($.type(cnts[key]) === "undefined") { cnts[key] = 0; } else { cnts[key]++; }
                                params[key + "[" + cnts[key] + "]"] = value;
                            }
                        } else {
                            params[$(this).prop("name")] = ($(this).prop("disabled") === true) ? 'NULL' : ($(this).prop("checked") === true) ? 1 : 0;
                        }
                    } else if ($(this).prop("type") === "radio") {
                        if ($(this).prop("checked") === true) {
                            params[$(this).prop("name")] = ($(this).prop("disabled") === true || $.trim($(this).val()) === "") ? 'NULL' : $(this).val();
                        }
                    } else if ($(this).prop("type") === "select-multiple") {
                        var value;
                        var cnt = 0;
                        if ($(this).prop("disabled") !== true) {
                            value = $(this).val();
                            for (var iVal in value) {
                                params[$(this).prop("name") + "[" + cnt + "]"] = value[iVal];
                                cnt++;
                            }
                        }
                    } else {
                        params[$(this).prop("name")] = ($(this).prop("disabled") === true || $.trim($(this).val()) === "") ? 'NULL' : $(this).val();
                    }
                }
            });
            var poststr = ($.type(params) === "object") ? $.param(params) : "";
            $.postJSON(url, poststr, function (data) {
                s2s = true;
                if (
                    (
                        $.type(data) !== "undefined" &&
                        $.type(data.data) !== "undefined" &&
                        $.type(data.data[0]) !== "undefined" &&
                        $.type(data.data[0].MSG) !== "undefined" && data.data[0].MSG === "ok"
                    )
                ) {
                    alert('Transacción realizada satisfactoriamente !');
                    if ($.type(callBack) === "function") {
                        callBack({ url: url, form: form, params: params, data: data.data });
                    } else {
                        loadContent(lastContent.content, lastContent.name);
                    }
                } else {
                    var msg = (($.type(data.data) !== "undefined" && $.type(data.data[0]) !== "undefined" && $.type(data.data[0].MSG) !== "undefined") ? data.data[0].MSG : ($.type(data.responseText) === "undefined" ? "No hay datos" : data.responseText));
                    try {
                        if (msg.length > 0 && msg.search("<br/>") > 0)
                            alert("Error :\n\n" + msg.replace(/<br\/>/g, '\n') + "\n\n");
                        else
                            alert("Error :\n\n" + msg + "\n\n");
                    }
                    catch (err) {
                        alert(err.message);
                    }

                }
            });
        }
    }
}
function guardarObjetoData(elem, datos, Json, callBack, byPassConfirm, byPassSucces) {
    if (s2s === true) {
        var byPassConfirmation = byPassConfirm;
        if (byPassConfirmation !== true) {
            byPassConfirmation = confirm("\n\n¿Confirma que desea realizar la acción solicitada?.\n\n");
        }
        if (byPassConfirmation === true) {
            s2s = false;
            var url = '/?option=json&seed=' + (new Date().getTime());
            var params = { json: Json, uid: UI };
            for (var i in datos) {
                params[i] = datos[i];
            }
            var poststr = ($.type(params) === "object") ? $.param(params) : "";
            $.postJSON(url, poststr, function (data) {
                s2s = true;
                if (
                    (
                        $.type(data) !== "undefined" &&
                        $.type(data.data) !== "undefined" &&
                        $.type(data.data[0]) !== "undefined" &&
                        $.type(data.data[0].MSG) !== "undefined" && data.data[0].MSG === "ok"
                    )
                ) {
                    if (byPassSucces !== true) {
                        alert('Transacción realizada satisfactoriamente !');
                    }
                    if ($.type(callBack) === "function") {
                        callBack({ url: url, elem: elem, params: params, data: data.data });
                    } else {
                        loadContent(lastContent.content, lastContent.name);
                    }

                } else {
                    alert("Error :\n\n" + (($.type(data.data) !== "undefined" && $.type(data.data[0]) !== "undefined" && $.type(data.data[0].MSG) !== "undefined") ? data.data[0].MSG : data.responseText) + "\n\n");
                }
            });
        }
    }
}
*/

function showMessageModal(message) {
    $("#messageModalBody").text(message);
    $("#messageModal").modal('show');
}

function showConfirmationModal(callback) {
    var modalHtml = `
        <div class="modal fade" id="confirmationModal" tabindex="-1" aria-labelledby="confirmationModalLabel" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="confirmationModalLabel">Confirmación</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                ¿Confirma que desea realizar la acción solicitada?
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-success me-1 mb-1" id="confirmButton">Confirmar</button>
                <button type="button" class="btn btn-secondary me-1 mb-1" data-bs-dismiss="modal">Cancelar</button> 
              </div>
            </div>
          </div>
        </div>`;
    $('body').append(modalHtml);
    var modal = new bootstrap.Modal(document.getElementById('confirmationModal'), {});
    modal.show();

    $('#confirmButton').on('click', function () {
        callback(true);
        modal.hide();
        $('#confirmationModal').remove();
    });

    $('#confirmationModal').on('hidden.bs.modal', function () {
        callback(false);
        $('#confirmationModal').remove();
    });
}

function guardarFormulario(form, Json, callBack, byPassConfirm) {
    var validacion = validarFormulario(form);
    if (!validacion.esValido) {
        showMessageModal(validacion.mensajesDeError.join('\n'));
        return;
    }

    if (s2s === true) {
        var byPassConfirmation = byPassConfirm;
        if (byPassConfirmation !== true) {
            showConfirmationModal(function(confirmed) {
                if (confirmed) {
                    processFormSubmission(form, Json, callBack);
                }
            });
        } else {
            processFormSubmission(form, Json, callBack);
        }
    }
}

function processFormSubmission(form, Json, callBack) {
    s2s = false;
    var url = '/?option=json&seed=' + (new Date().getTime());
    var params = { json: Json, uid: UI };
    var cnts = {};

    $("body").append(`
        <div id="loading-overlay" class="position-fixed w-100 h-100 d-flex justify-content-center align-items-center" style="top: 0; left: 0; background: rgba(94, 110, 130, 0.4); z-index: 1050;">
            <div class="row align-items-center">
                <div class="col-lg-4">
                    <div class="lottie mx-auto" style="width: 120px; height: 120px" data-options='{"path":"lib/template/public/assets/img/animated-icons/infinite-loop.json"}'></div>
                </div>
            </div>
        </div>
    `);

    $(':input[name!="rp"][name!="q"][name!="qtype"]', form).each(function () {
        if ($(this).prop("name") !== "") {
            if ($(this).prop("type") === "checkbox") {
                var str = $(this).prop("name");
                if ($.type(str.match(/\[(.*)\]/)) !== "null") {
                    if ($(this).prop("checked") === true) {
                        var key = str.replace("[" + (str.match(/\[(.*)\]/).pop()) + "]", "");
                        var value = str.match(/\[(.*)\]/).pop();
                        if ($.type(cnts[key]) === "undefined") { cnts[key] = 0; } else { cnts[key]++; }
                        params[key + "[" + cnts[key] + "]"] = value;
                    }
                } else {
                    params[$(this).prop("name")] = ($(this).prop("disabled") === true) ? 'NULL' : ($(this).prop("checked") === true) ? 1 : 0;
                }
            } else if ($(this).prop("type") === "radio") {
                if ($(this).prop("checked") === true) {
                    params[$(this).prop("name")] = ($(this).prop("disabled") === true || $.trim($(this).val()) === "") ? 'NULL' : $(this).val();
                }
            } else if ($(this).prop("type") === "select-multiple") {
                var value;
                var cnt = 0;
                if ($(this).prop("disabled") !== true) {
                    value = $(this).val();
                    for (var iVal in value) {
                        params[$(this).prop("name") + "[" + cnt + "]"] = value[iVal];
                        cnt++;
                    }
                }
            } else {
                params[$(this).prop("name")] = ($(this).prop("disabled") === true || $.trim($(this).val()) === "") ? 'NULL' : $(this).val();
            }
        }
    });

    var poststr = ($.type(params) === "object") ? $.param(params) : "";
    $.postJSON(url, poststr, function (data) {
        s2s = true;
        $("#loading-overlay").remove();
        if (
            (
                $.type(data) !== "undefined" &&
                $.type(data.data) !== "undefined" &&
                $.type(data.data[0]) !== "undefined" &&
                $.type(data.data[0].MSG) !== "undefined" && data.data[0].MSG === "ok"
            )
        ) {
            showMessageModal('Transacción realizada satisfactoriamente!');
            if ($.type(callBack) === "function") {
                callBack({ url: url, form: form, params: params, data: data.data });
            } else {
                loadContent(lastContent.content, lastContent.name);
            }
        } else {
            var msg = (($.type(data.data) !== "undefined" && $.type(data.data[0]) !== "undefined" && $.type(data.data[0].MSG) !== "undefined") ? data.data[0].MSG : ($.type(data.responseText) === "undefined" ? "No hay datos" : data.responseText));
            msg = msg.replace(/<br\/>/g, '').replace(/<br>/g, '');
            showMessageModal(msg);
        }
    });
}

function guardarObjetoData(elem, datos, Json, callBack, byPassConfirm, byPassSucces) {
    if (s2s === true) {
        var byPassConfirmation = byPassConfirm;
        if (byPassConfirmation !== true) {
            showConfirmationModal(function(confirmed) {
                if (confirmed) {
                    processObjectDataSubmission(elem, datos, Json, callBack, byPassSucces);
                }
            });
        } else {
            processObjectDataSubmission(elem, datos, Json, callBack, byPassSucces);
        }
    }
}

function processObjectDataSubmission(elem, datos, Json, callBack, byPassSucces) {
    s2s = false;
    var url = '/?option=json&seed=' + (new Date().getTime());
    var params = { json: Json, uid: UI };
    for (var i in datos) {
        params[i] = datos[i];
    }
    var poststr = ($.type(params) === "object") ? $.param(params) : "";
    $.postJSON(url, poststr, function (data) {
        s2s = true;
        if (
            (
                $.type(data) !== "undefined" &&
                $.type(data.data) !== "undefined" &&
                $.type(data.data[0]) !== "undefined" &&
                $.type(data.data[0].MSG) !== "undefined" && data.data[0].MSG === "ok"
            )
        ) {
            if (byPassSucces !== true) {
                showMessageModal('Transacción realizada satisfactoriamente!');
            }
            if ($.type(callBack) === "function") {
                callBack({ url: url, elem: elem, params: params, data: data.data });
            } else {
                loadContent(lastContent.content, lastContent.name);
            }
        } else {
            var msg = (($.type(data.data) !== "undefined" && $.type(data.data[0]) !== "undefined" && $.type(data.data[0].MSG) !== "undefined") ? data.data[0].MSG : data.responseText);
            showMessageModal(msg);
        }
    });
}
function round(val, precission = 2) {
    var nominal = Math.pow(10, precission);
    return Math.round(val * nominal) / nominal;
}

function presentarTareasPendientes(data) {
    var pend = data.data[0].p;
    var npend = 0;
    var html = "";
    for (var x in pend) {
        var elem = "#" + x;
        if ($(elem).text() !== "") {
            npend += (pend[x] * 1);
            html += "<div class=\"bublelink\" onclick=\"javascript:verTareasPendientes('" + x + "');\"> " + $(elem).text() + " (" + pend[x] + ")</div>";
        }
    };
    $("#core_frontpage_pendientes").empty().text(npend).attr({
        "data-toggle": "popover",
        "data-trigger": "click",
        "data-content": ((npend === 0) ? "Ninguna" : html),
        "data-placement": "top",
        "data-original-title": "Tareas pendientes"
    }).popover({ html: true });
    if (npend === 0) {
        $("#core_frontpage_pendientes").fadeOut(1200);
    } else {
        $("#core_frontpage_pendientes").fadeIn(1200).animate({ opacity: 0.2 }).animate({ opacity: 0.6 }).animate({ opacity: 0.2 }).animate({ opacity: 0.6 }).animate({ opacity: 0.2 }).animate({ opacity: 0.6 });
        if (lastPending !== npend) {
            lastPending = npend;
            beep();
        }
    }
}

function verTareasPendientes(el) {
    $("#core_frontpage_pendientes,#" + el).trigger("click");
    $("#core_frontpage_pendientes").fadeOut(1200);
}

function isValidDate(date) {
    var valid = false;
    if (date.length === 10) {
        var temp = date.split('/');
        var d = new Date(temp[2] + '/' + temp[1] + '/' + temp[0]);
        temp[0] = parseInt(temp[0], 10);
        temp[1] = parseInt(temp[1], 10);
        temp[2] = parseInt(temp[2], 10);
        valid = (d && d.getFullYear() === temp[2] && d.getMonth() + 1 === temp[1] && d.getDate() === temp[0]);
    }
    return valid;
}
function validarFormulario(form) {
    var esValido = true;
    var mensajesDeError = [];

    $(':input[required]', form).each(function () {
        if ($(this).val() === '') {
            esValido = false;
            var campoNombre = $(this).attr('name');
            mensajesDeError.push('El campo ' + campoNombre + ' es obligatorio.');
        }
    });


    return { esValido: esValido, mensajesDeError: mensajesDeError };
}


function beep() {
    var snd = new Audio("data:audio/wav;base64,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");
    snd.play();
}

/*
function saveFlexiGridToTarget(target,elem,classSelected){
    var a=getSelectedData(elem,classSelected);
    var pStr=[];
    for (var i=0;i<a.length;i++){
        for (var v in a[i]){
                pStr[v+"["+i+"][0]"]=((a[i][v]!=='undefined' && a[i][v]!==undefined)?a[i][v]:"");
        }
    }
    if(a.length>0){
        guardarEnDestino(target,pStr,elem);
    }else{
        alert("Nada que guardar");
    }
}
*/


function cargartable(p){


}


function enviarArchivo(form, doBefore, onSuccess, onError) {
    $.ajax({
        url: $(form).attr("action"), // Url to which the request is send
        type: "POST",             // Type of request to be send, called as method
        data: new FormData(form), // Data sent to server, a set of key/value pairs (i.e. form fields and values)
        contentType: false,       // The content type used when sending data to the server.
        cache: false,             // To unable request pages to be cached
        processData: false,        // To send DOMDocument or non processed data file it is set to false
        beforeSend: doBefore, // A function to be called before the request is sent.
        success: onSuccess,  // A function to be called if request succeeds
        error: onError  // A function to be called if request fails
    });
}
function mostrarModal(mensaje) {
    $('#messageModalBody').text(mensaje);
    $('#messageModal').modal('show');
  }

function mostrarConfirmacion(mensaje, callback) {
    $('#confirmModalBody').text(mensaje);
    $('#confirmModal').modal('show');

    $('#confirmModalYes').off('click').on('click', function() {
        $('#confirmModal').modal('hide');
        if (typeof callback === 'function') {
            callback();
        }
    });
}