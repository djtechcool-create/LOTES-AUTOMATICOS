$(function () {
    var egresoshojaruta_validador_cabecera = $("#egresoshojaruta_frm_cabecera").validate({
        highlight: function (element, errorClass) {
            $(element).addClass(errorClass);
        },
        invalidHandler: function () {
            mostrarModal("Hay " + egresoshojaruta_validador_cabecera.numberOfInvalids() + " campos incorrectos\n\nRevise por favor los campos resaltados en color rojo.\nCorrija e intente guardar nuevamente.\n\nGracias");
        }
    });

    $("#egresoshojaruta_flex_listaegresos").flexigrid({
        title: "Listado de Egresos por Rutas",
        url: "/?option=json",
        colModel: [
            { display: 'EGRESO', name: 'EGRESO', width: 120, sortable: false, align: 'center' },
            { display: 'FECHA', name: 'FECHA', width: 80, sortable: false, align: 'center' },
            { display: 'BODEGA', name: 'BODEGA', width: 200, sortable: false, align: 'left' },
            { display: 'ORDEN', name: 'ORDEN', width: 190, sortable: false, align: 'left' },
            { display: 'DIA', name: 'DIA', width: 35, sortable: false, align: 'center' },
            { display: 'TRANSPORTE', name: 'TRANSPORTE', width: 70, sortable: false, align: 'center' },
            { display: 'HOJA RUTA', name: 'HOJARUTA', width: 120, sortable: false, align: 'center' },
            { display: 'ESTADO', name: 'ESTADO', width: 82, sortable: false, align: 'left' },
            { display: 'RESPONSABLE', name: 'RESPONSABLE', width: 200, sortable: false, align: 'left' },
            { display: 'OBSERVACIÓN', name: 'OBSERVACION', width: 300, sortable: false, align: 'left' },
            { display: 'MBO_CODIGO', name: 'MBO_CODIGO', width: 10, sortable: false, align: 'left', hide: true }
        ],
        params: [
            { name: "json", value: 2083 },
            { name: "uid", value: UI }
        ],
        buttons: [
            { id: "egresoshojaruta_flex_listaegresos_nuevo", name: 'Nuevo', bclass: 'new', onpress: fn_egresoshojaruta_buttonFlexgrid },
            { id: "egresoshojaruta_flex_listaegresos_ver", name: 'Ver', bclass: 'view', onpress: fn_egresoshojaruta_buttonFlexgrid }
        ],
        searchitems: [
            { display: 'EGRESO', name: 'EGR' },
            { display: 'BODEGA', name: 'BOD' },
            { display: 'ORDEN', name: 'ORD', isdefault: true },
            { display: 'TRANSPORTE', name: 'TRA' },
            { display: 'HOJA RUTA', name: 'HOJ' }
        ]
    });

    $("#egresoshojaruta_flex_detalle_egreso").flexigrid({
        colModel: [
            { display: 'GRUPO', name: 'GRUPO', width: 300, sortable: false, align: 'left' },
            { display: 'PRODUCTO', name: 'PRODUCTO', width: 300, sortable: false, align: 'left' },
            { display: 'CANTIDAD', name: 'CANTIDAD', width: 100, sortable: false, align: 'right' },
            { display: 'SALDO', name: 'SALDO', width: 10, sortable: false, align: 'left', hide: true },
            { display: 'DMB_CODIGO', name: 'DMB_CODIGO', width: 10, sortable: false, align: 'left', hide: true },
            { display: 'PGE_CODIGO', name: 'PGE_CODIGO', width: 10, sortable: false, align: 'left', hide: true },
            { display: 'PES_CODIGO', name: 'PES_CODIGO', width: 10, sortable: false, align: 'left', hide: true }
        ],
        buttons: [
            { id: "egresoshojaruta_flex_detalleegreso_editar", name: 'Editar', bclass: 'edit', onpress: fn_egresoshojaruta_buttonFlexgrid},
            { id: "egresoshojaruta_flex_detalleegreso_agregar", name: 'Agregar', bclass: 'add', onpress: fn_egresoshojaruta_buttonFlexgrid}
        ],
    }).parent().parent().find(".pDiv").hide();

    $("#egresoshojaruta_cancelar").click(function () {
        //if (
        mostrarConfirmacion("¿Seguro que desea cancelar el proceso actual.?",//)){ {
            function () {
                fn_egresoshojaruta_limpiarCampos();
            });
        //}
    });

    $("#egresoshojaruta_guardar").click(function () {
        if ($("#egresoshojaruta_frm_cabecera").valid()) {
            if($("#egresoshojaruta_pescodigo").val() * 1 <= 0){
                var info_saldo = $("#egresoshojaruta_flex_detalle_egreso").getFlexDataAsParams(["SALDO"]);
                var parametros = $("#egresoshojaruta_flex_detalle_egreso").getFlexDataAsParams(["DMB_CODIGO", "PGE_CODIGO", "PES_CODIGO", "CANTIDAD"]);
                if (Object.keys(parametros).length > 0) {
                    if (fn_egresoshojaruta_evaluaSaldo(info_saldo)) {
                        parametros["id"] = $("#egresoshojaruta_codigo").val() === '' ? 'NULL' : $("#egresoshojaruta_codigo").val();
                        parametros["bodega"] = $("#egresoshojaruta_bodega").val();
                        parametros["orden"] = $("#egresoshojaruta_orden").val();
                        parametros["hojaruta"] = $("#egresoshojaruta_hojaruta").val();
                        parametros["responsable"] = $("#egresoshojaruta_responsableruta").val();
                        parametros["observacion"] = $("#egresoshojaruta_observacion").val();
                        parametros["uid"] = UI;

                        guardarObjetoData('cab', parametros, 2085, fn_egresoshojaruta_aftersave, null);
                    } else {
                        mostrarModal("No se puede egresar la ruta, porque el saldo actual en bodega no cubre lo requerido para egresar esta ruta.");
                    }
                } else {
                    mostrarModal("El egreso debe de tener al menos un producto.");
                }
            }else{
                mostrarModal("No se puede egresar la ruta, tiene pendiente agregar el ajuste de un grupo - producto.");
            }
        }
    });
    $("#egresoshojaruta_pdf").click(function () {
        creaPDF({ reporte: "pdf_egresoruta_guiaestiba", modulo: "logistica", uid: UI, mbocodigo: $("#egresoshojaruta_codigo").val() });
    });
    $("#egresoshojaruta_pdf_definicion").click(function () {
        creaPDF({ reporte: "pdf_egresobodegahojarutacompensacion", modulo: "logistica", uid: UI, mbocodigo: $("#egresoshojaruta_codigo").val() });
    });
    $("#egresoshojaruta_bodega").change(function () {
        limpiaCombo($("#egresoshojaruta_dia"));
        limpiaCombo($("#egresoshojaruta_placa"));
        limpiaCombo($("#egresoshojaruta_hojaruta"));
        $("#egresoshojaruta_flex_detalle_egreso").flexClean();
    });
    $("#egresoshojaruta_orden").change(function () {
        limpiaCombo($("#egresoshojaruta_placa"));
        limpiaCombo($("#egresoshojaruta_hojaruta"));
        $("#egresoshojaruta_flex_detalle_egreso").flexClean();
        llenaCombo($("#egresoshojaruta_dia"), "/?option=json", { json: 2075, bodcodigo: $("#egresoshojaruta_bodega").val(), oddcodigo: $(this).val() });
    });
    $("#egresoshojaruta_dia").change(function () {
        limpiaCombo($("#egresoshojaruta_hojaruta"));
        $("#egresoshojaruta_flex_detalle_egreso").flexClean();
        llenaCombo($("#egresoshojaruta_placa"), "/?option=json", { json: 2076, bodcodigo: $("#egresoshojaruta_bodega").val(), oddcodigo: $("#egresoshojaruta_orden").val(), dia: $(this).val() });
    });
    $("#egresoshojaruta_placa").change(function () {
        llenaCombo($("#egresoshojaruta_hojaruta"), "/?option=json", { json: 2077, bodcodigo: $("#egresoshojaruta_bodega").val(), oddcodigo: $("#egresoshojaruta_orden").val(), dia: $("#egresoshojaruta_dia").val(), paucodigo: $(this).val() });
        fn_egresoshojaruta_cargaDescripcionTransporte($(this).val());
    });
    $("#egresoshojaruta_hojaruta").change(function () {
        fn_egresoshojaruta_cargaDescripcionHojaRuta($(this).val());
        fn_egresoshojaruta_cargaGridDetalleProductoHojaRuta($(this).val());
    });

    $("#egresoshojaruta_producto").change(function () {        
        var parametros = { json: 2129, odd: $("#egresoshojaruta_orden").val(), bod:$("#egresoshojaruta_bodega").val(), pes: $("#egresoshojaruta_producto").val()};
        $("#egresoshojaruta_saldo").val('0');
        getJson("/?option=json", parametros, "saldo", fn_egresoshojaruta_aftersave);
    });

    llenaCombo($("#egresoshojaruta_bodega"), "/?option=json", { json: 1098, usu: UI });
    llenaCombo($("#egresoshojaruta_orden"), "/?option=json", { json: 1099, est: [64] });

    limpiaCombo($("#egresoshojaruta_dia"));
    limpiaCombo($("#egresoshojaruta_placa"));
    limpiaCombo($("#egresoshojaruta_hojaruta"));

    //botones
    $("#egresoshojaruta_pdf").prop("disabled", true);
    $("#egresoshojaruta_pdf_definicion").prop("disabled", true);
});
function fn_egresoshojaruta_limpiarCampos() {
    $("#egresoshojaruta_secuencial, #egresoshojaruta_fecha, #egresoshojaruta_bodega, #egresoshojaruta_orden, #egresoshojaruta_descripciontransporte, #egresoshojaruta_descripcionhojaruta, #egresoshojaruta_responsableruta, #egresoshojaruta_observacion, #egresoshojaruta_codigo").val("");

    limpiaCombo($("#egresoshojaruta_dia"));
    limpiaCombo($("#egresoshojaruta_placa"));
    limpiaCombo($("#egresoshojaruta_hojaruta"));

    $("#egresoshojaruta_bodegadescripcion,#egresoshojaruta_ordendescripcion,#egresoshojaruta_diadescripcion,#egresoshojaruta_placadescripcion,#egresoshojaruta_sechojarutadescripcion").css({ "display": "none" });
    $("#egresoshojaruta_bodega,#egresoshojaruta_orden,#egresoshojaruta_dia,#egresoshojaruta_placa,#egresoshojaruta_hojaruta").css({ "display": "block" });

    $("#egresoshojaruta_flex_listaegresos tr").removeClass("trSelected");
    $("#egresoshojaruta_flex_detalle_egreso").flexClean();
    $("#egresoshojaruta_frm_cabecera").find(".error").removeClass("error");
    $("#egresoshojaruta_frm_detalle").find(".error").removeClass("error");
    $("#egresoshojaruta_guardar").prop("disabled", false);
    $("#egresoshojaruta_pdf").prop("disabled", true);
    $("#egresoshojaruta_pdf_definicion").prop("disabled", true);
    fn_egresoshojaruta_habilitarCampos(true);
}
function fn_egresoshojaruta_limpiarCamposDetalle(){
    $("#egresoshojaruta_grupo, #egresoshojaruta_saldo, #egresoshojaruta_cantidad, #egresoshojaruta_dbmcodigo, #egresoshojaruta_pgecodigo, #egresoshojaruta_pescodigo, #egresoshojaruta_cantidadreq, #egresoshojaruta_saldofaltante, #egresoshojaruta_rowid").val("");
    limpiaCombo($("#egresoshojaruta_producto"));
}
function fn_egresoshojaruta_aftersave(data) {
    switch (data.elem) {
        case 'cab':
            if (data.data[0].MBO_CODIGO * 1 > 0) {
                $("#egresoshojaruta_codigo").val(data.data[0].MBO_CODIGO);
                $("#egresoshojaruta_secuencial").val(data.data[0].MBO_SECUENCIAL);
                $("#egresoshojaruta_fecha").val(data.data[0].MBO_FECHA);
                $("#egresoshojaruta_flex_listaegresos").flexReload();
                fn_egresoshojaruta_cargaGridDetalleEgresoRuta(data.data[0].MBO_CODIGO);
                fn_egresoshojaruta_habilitarCampos(false);
                $("#egresoshojaruta_guardar").prop("disabled", true);
                $("#egresoshojaruta_pdf").prop("disabled", false);
                $("#egresoshojaruta_pdf_definicion").prop("disabled", false);
            }
            break;
        case 'crgInfo':
            if (data.data[0].MBOCODIGO * 1 > 0) {
                $("#egresoshojaruta_codigo").val(data.data[0].MBOCODIGO);
                $("#egresoshojaruta_secuencial").val(data.data[0].SECUENCIAL);
                $("#egresoshojaruta_fecha").val(data.data[0].FECHA);
                $("#egresoshojaruta_bodegadescripcion").val(data.data[0].BODEGA);
                $("#egresoshojaruta_ordendescripcion").val(data.data[0].ORDEN);
                $("#egresoshojaruta_diadescripcion").val(data.data[0].DIA);
                $("#egresoshojaruta_placadescripcion").val(data.data[0].PLACA);
                $("#egresoshojaruta_descripciontransporte").val(data.data[0].DESCRIPCIONTRANSPORTE);
                $("#egresoshojaruta_sechojarutadescripcion").val(data.data[0].HOJARUTA);
                $("#egresoshojaruta_descripcionhojaruta").val(data.data[0].DESCRIPCIONHOJARUTA);
                $("#egresoshojaruta_responsableruta").val(data.data[0].RESPONSABLE);
                $("#egresoshojaruta_observacion").val(data.data[0].OBSERVACION);

                $("#egresoshojaruta_bodegadescripcion,#egresoshojaruta_ordendescripcion,#egresoshojaruta_diadescripcion,#egresoshojaruta_placadescripcion,#egresoshojaruta_sechojarutadescripcion").css({ "display": "block" });
                $("#egresoshojaruta_bodega,#egresoshojaruta_orden,#egresoshojaruta_dia,#egresoshojaruta_placa,#egresoshojaruta_hojaruta").css({ "display": "none" });
            }
            break;
        case 'saldo':
            if (data.data[0].PES_CODIGO * 1 > 0) {
                var datosProductoAsignado = $("#egresoshojaruta_flex_detalle_egreso").getFlexData(["PES_CODIGO", "CANTIDAD"]);
                var saldoProducto = data.data[0].SALDO * 1;
                console.log(saldoProducto) ;              
                saldoProducto -= fn_egresoshojaruta_SaldoPorProductoAsignado(datosProductoAsignado, $("#egresoshojaruta_producto").val());
                if (saldoProducto < 0) { saldoProducto = 0; } 
                $("#egresoshojaruta_saldo").val(saldoProducto);
            } else {
                $("#egresoshojaruta_saldo").val(0);
            }          
            break;
    }
}
function fn_egresoshojaruta_habilitarCampos(bool) {
    $("#egresoshojaruta_bodega, #egresoshojaruta_orden, #egresoshojaruta_dia, #egresoshojaruta_placa, #egresoshojaruta_hojaruta, #egresoshojaruta_responsableruta, #egresoshojaruta_observacion").prop("disabled", !bool);
}
function fn_egresoshojaruta_buttonFlexgrid(btnId, grid) {
    switch (btnId) {
        case "egresoshojaruta_flex_listaegresos_nuevo":
            //if(
            mostrarConfirmacion("Este proceso limpia el formulario, si no ha guardado se perdeán los cambios. \n¿Desea continuar.?",//)){
                function () {
                    $("#egresoshojaruta_li_reg").trigger("click");
                    fn_egresoshojaruta_limpiarCampos();
                });
            //}
            break;
        case "egresoshojaruta_flex_listaegresos_ver":
            var filasSeleccionadas = grid.getSelectedRowsIds();
            if (filasSeleccionadas.length > 0) {
                //if(
                mostrarConfirmacion("Este proceso recarga el formulario, si no ha guardado los cambios del proceso actual se perderán los cambios. \n¿Desea continuar.?",//)){
                    function () {
                        fn_egresoshojaruta_limpiarCampos();
                        var rowData = grid.getRowData(filasSeleccionadas[0]);
                        var id = rowData["MBO_CODIGO"];
                        var parametros = { json: 2091, mbocodigo: id };

                        getJson("/?option=json", parametros, "crgInfo", fn_egresoshojaruta_aftersave);
                        fn_egresoshojaruta_cargaGridDetalleEgresoRuta(id);

                        $("#egresoshojaruta_guardar").prop("disabled", true);
                        $("#egresoshojaruta_pdf").prop("disabled", false);
                        $("#egresoshojaruta_pdf_definicion").prop("disabled", false);
                        fn_egresoshojaruta_habilitarCampos(false);

                        $("#egresoshojaruta_li_reg").trigger("click");
                        $("#egresoshojaruta_flex_listaegresos tr").removeClass("trSelected");
                    });
                //}
            } else {
                mostrarModal("Seleccione un registro para ser visualizado.");
            }
            break;
        case "egresoshojaruta_flex_detalleegreso_editar":
            var filasSeleccionadas=grid.getSelectedRowsIds();
            if(filasSeleccionadas.length > 0){
                if($("#egresoshojaruta_pescodigo").val() * 1 <= 0){
                    var rowId;
                    var saldo;
                    for(var i in filasSeleccionadas){
                        var rowData = grid.getRowData(filasSeleccionadas[i]);                    
                        rowId = filasSeleccionadas[i];
                        saldo = rowData["SALDO"] * 1;                    
                        if (saldo > 0){
                            mostrarModal("No se permite editar producto que no tiene saldo suficiente para completar lo requerido.");
                        }else{                        
                            llenaCombo($("#egresoshojaruta_producto"), "/?option=json", { json: 2128, odd: $("#egresoshojaruta_orden").val(),  bod:$("#egresoshojaruta_bodega").val(), pge: rowData["PGE_CODIGO"]},'',
                            function(){
                                var totalOpciones = $('#egresoshojaruta_producto option').length;                            
                                if(totalOpciones * 1 > 2) {                                
                                    $("#egresoshojaruta_grupo").val(rowData["GRUPO"]);
                                    $("#egresoshojaruta_producto").val(rowData["PRODUCTO"]);
                                    $("#egresoshojaruta_cantidad").val(rowData["CANTIDAD"]);
                                    $("#egresoshojaruta_dbmcodigo").val(rowData["DMB_CODIGO"]);
                                    $("#egresoshojaruta_pgecodigo").val(rowData["PGE_CODIGO"]);
                                    $("#egresoshojaruta_pescodigo").val(rowData["PES_CODIGO"]);
                                    $("#egresoshojaruta_cantidadreq").val(rowData["CANTIDAD"]);
                                    $("#egresoshojaruta_saldofaltante").val(saldo);
                                    $("#egresoshojaruta_rowid").val(rowId);

                                    grid.removeSelectedRows(false);
                                    $("#otrosegresos_flex_detalle_ingreso tr").removeClass("trSelected");
                                } else {
                                    fn_egresoshojaruta_limpiarCamposDetalle();
                                    mostrarModal("Este grupo solo tiene definido un producto para el despacho o solo tiene disponible un producto con saldo mayor a cero.");               
                                }
                            });
                        }
                    }
                }else{
                    mostrarModal("Se encuentra ajustando la asignación de otro grupo - producto, debe agregar el ajuste antes de editar un nuevo grupo - producto.");
                }
            }else{
                mostrarModal("Seleccione un registro para ser editado");
            }
            break;
        case "egresoshojaruta_flex_detalleegreso_agregar":
            fn_egresoshojaruta_agregardetalle();
            break;
    }
}

function fn_egresoshojaruta_agregardetalle (){
    var id_fila = $("#egresoshojaruta_rowid").val();
    var vld_Agregar = $.type($("tr[id=row"+id_fila+"]", "#egresoshojaruta_flex_detalle_egreso").html());
    if($("#egresoshojaruta_frm_detalle").valid()){
        if (vld_Agregar==="undefined"){
            var producto = $("#egresoshojaruta_producto :selected").text();
            var saldo = $("#egresoshojaruta_saldo").val() * 1;
            var cantidadRequerida= $("#egresoshojaruta_cantidadreq").val() * 1;
            if(saldo >= cantidadRequerida){
                $("#egresoshojaruta_flex_detalle_egreso").flexAddDataRow({"ID":id_fila,
                    "GRUPO": $("#egresoshojaruta_grupo").val(),
                    "PRODUCTO": producto,
                    "CANTIDAD": cantidadRequerida,
                    "SALDO":$("#egresoshojaruta_saldofaltante").val(),
                    "DMB_CODIGO":$("#egresoshojaruta_dbmcodigo").val(),
                    "PGE_CODIGO":$("#egresoshojaruta_pgecodigo").val(),
                    "PES_CODIGO":$("#egresoshojaruta_producto").val()
                });
                fn_egresoshojaruta_limpiarCamposDetalle();
            }else{
                mostrarModal("Saldo insuficiente. Cantidad requerida: " + cantidadRequerida +" y saldo: "+saldo);
            }
        }else{
            mostrarModal("La definición de egreso por ruta ya se encuentra agregado al detalle.");
        }
    }
    $("#egresoshojaruta_producto").focus();
}


function fn_egresoshojaruta_cargaGridDetalleEgresoRuta(id) {
    var flexParams = {
        url: "/?option=json",
        params: [
            { name: "json", value: 2084 },
            { name: "mbocodigo", value: id }
        ]
    };
    $("#egresoshojaruta_flex_detalle_egreso").flexOptions(flexParams).flexReload();
}
function fn_egresoshojaruta_cargaGridDetalleProductoHojaRuta(hru) {
    var flexParams = {
        url: "/?option=json",
        params: [
            { name: "json", value: 2082 },
            { name: "hrucodigo", value: hru }
        ]
    };
    $("#egresoshojaruta_flex_detalle_egreso").flexOptions(flexParams).flexReload();
}
function fn_egresoshojaruta_cargaDescripcionTransporte(tra) {
    var parametros = { json: 2078, paucodigo: tra };
    getJson("/?option=json", parametros, "dt", fn_egresoshojaruta_aftercargaDescripcionTransporte);
}
function fn_egresoshojaruta_aftercargaDescripcionTransporte(data) {
    $("#egresoshojaruta_descripciontransporte").val(data.data[0].DESCRIPCION);
}
function fn_egresoshojaruta_cargaDescripcionHojaRuta(hru) {
    var parametros = { json: 2079, hrucodigo: hru };
    getJson("/?option=json", parametros, "dhr", fn_egresoshojaruta_aftercargaDescripcionHojaRuta);
}
function fn_egresoshojaruta_aftercargaDescripcionHojaRuta(data) {    
    $("#egresoshojaruta_descripcionhojaruta").val(data.data[0].DESCRIPCION);
}
function fn_egresoshojaruta_evaluaSaldo(obj) {
    var retorno = true;
    for (var i in obj) {
        if (obj[i] * 1 > 0) {
            retorno = false;
            break;
        }
    }
    return retorno;
}
function fn_egresoshojaruta_SaldoPorProductoAsignado(obj, pes) {
    var retSaldo = 0;    
   for (var indice in obj) {
        if(obj[indice].PES_CODIGO * 1 == pes){
            retSaldo += (obj[indice].CANTIDAD * 1);
        }        
    }
    console.log(retSaldo);
    return retSaldo;
}



