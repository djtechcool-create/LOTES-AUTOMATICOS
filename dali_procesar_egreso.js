$(function () {
    var id_dmbcodigo = '';
    var procesaregresoshojaruta_validador_detalle = $("#procesaregresoshojaruta_frm_detalle").validate({
        highlight: function (element, errorClass) {
            $(element).addClass(errorClass);
        },
        invalidHandler: function () {
            mostrarModal("Hay " + procesaregresoshojaruta_validador_detalle.numberOfInvalids() + " campos incorrectos\n\nRevise por favor los campos resaltados en color rojo.\nCorrija e intente guardar nuevamente.\n\nGracias");
        }
    });

    $("#procesaregresoshojaruta_flex_listaegresos").flexigrid({
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
            { name: "json", value: 2093 },
            { name: "uid", value: UI }
        ],
        buttons: [
            { id: "procesaregresoshojaruta_flex_listaegresos_ver", name: 'Ver', bclass: 'view', onpress: fn_procesaregresoshojaruta_buttonFlexgrid }
        ],
        searchitems: [
            { display: 'EGRESO', name: 'EGR' },
            { display: 'BODEGA', name: 'BOD' },
            { display: 'ORDEN', name: 'ORD', isdefault: true },
            { display: 'TRANSPORTE', name: 'TRA' },
            { display: 'HOJA RUTA', name: 'HOJ' }
        ]
    });

    $("#procesaregresoshojaruta_flex_detalle_egreso").flexigrid({
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
            { id: "procesaregresoshojaruta_flex_detalle_egreso_ver", name: 'Ver', bclass: 'view', onpress: fn_procesaregresoshojaruta_buttonFlexgrid }
        ]
    }).parent().parent().find(".pDiv").hide();

    $("#procesaregresoshojaruta_flex_detalle_lote").flexigrid({
        colModel: [
            { display: 'LOTE', name: 'LOTE', width: 150, sortable: false, align: 'left' },
            { display: 'CANTIDAD', name: 'CANTIDAD', width: 100, sortable: false, align: 'right' },
            { display: 'DMB_CODIGO', name: 'DMB_CODIGO', width: 10, sortable: false, align: 'left', hide: true },
            { display: 'ILO_CODIGO', name: 'ILO_CODIGO', width: 10, sortable: false, align: 'left', hide: true }
        ],
        buttons: [
            { id: "procesaregresoshojaruta_flex_detalle_lote_agregar", name: 'Agregar', bclass: 'add', onpress: fn_procesaregresoshojaruta_buttonFlexgrid },
            // {id:"procesaregresoshojaruta_flex_detalle_lote_editar", name : 'Editar', bclass : 'edit', onpress : fn_procesaregresoshojaruta_buttonFlexgrid},
            { id: "procesaregresoshojaruta_flex_detalle_lote_eliminar", name: 'Eliminar', bclass: 'delete', onpress: fn_procesaregresoshojaruta_buttonFlexgrid }
        ]
    }).parent().parent().find(".pDiv").hide();

    $("#procesaregresoshojaruta_cancelar").click(function () {
        //if(
        mostrarConfirmacion("¿Seguro que desea cancelar el proceso actual.?",//)){
            function () {
                fn_procesaregresoshojaruta_limpiarCampos();
                fn_procesaregresoshojaruta_limpiarCamposDetalle();
                fn_procesaregresoshojaruta_habilitarCampos(true);

            });
        //}
    });

    $("#procesaregresoshojaruta_procesar").click(function () {
        guardarObjetoData('proc', { "mbocodigo": $("#procesaregresoshojaruta_codigo").val() }, 2099, fn_procesaregresoshojaruta_aftersave, null);
    });
});
function fn_procesaregresoshojaruta_limpiarCampos() {
    $("#procesaregresoshojaruta_secuencial, #procesaregresoshojaruta_fecha, #procesaregresoshojaruta_bodega, #procesaregresoshojaruta_orden, #procesaregresoshojaruta_dia, #procesaregresoshojaruta_placa, #procesaregresoshojaruta_hojaruta, #procesaregresoshojaruta_descripciontransporte, #procesaregresoshojaruta_descripcionhojaruta, #procesaregresoshojaruta_responsableruta, #procesaregresoshojaruta_estado, #procesaregresoshojaruta_observacion, #procesaregresoshojaruta_codigo, #procesaregresoshojaruta_dcaestado").val("");

    $("#procesaregresoshojaruta_flex_listaegresos tr").removeClass("trSelected");
    $("#procesaregresoshojaruta_flex_detalle_egreso").flexClean();
    $("#procesaregresoshojaruta_flex_detalle_lote").flexClean();
    $("#procesaregresoshojaruta_frm_cabecera").find(".error").removeClass("error");
    $("#procesaregresoshojaruta_frm_detalle").find(".error").removeClass("error");
}
function fn_procesaregresoshojaruta_limpiarCamposDetalle() {
    $("#procesaregresoshojaruta_grupo, #procesaregresoshojaruta_producto, #procesaregresoshojaruta_cantidad, #procesaregresoshojaruta_dmbcodigoorigen, #procesaregresoshojaruta_dmbcodigodestino, #procesaregresoshojaruta_pgecodigo, #procesaregresoshojaruta_pescodigo, #procesaregresoshojaruta_saldo").val("");
    limpiaCombo($("#procesaregresoshojaruta_lote"));
}

function fn_procesaregresoshojaruta_aftersave(data) {
    switch (data.elem) {
        case 'crgInfo':
            if (data.data[0].MBOCODIGO * 1 > 0) {
                $("#procesaregresoshojaruta_codigo").val(data.data[0].MBOCODIGO);
                $("#procesaregresoshojaruta_secuencial").val(data.data[0].SECUENCIAL);
                $("#procesaregresoshojaruta_fecha").val(data.data[0].FECHA);
                $("#procesaregresoshojaruta_bodega").val(data.data[0].BODEGA);
                $("#procesaregresoshojaruta_orden").val(data.data[0].ORDEN);
                $("#procesaregresoshojaruta_dia").val(data.data[0].DIA);
                $("#procesaregresoshojaruta_placa").val(data.data[0].PLACA);
                $("#procesaregresoshojaruta_descripciontransporte").val(data.data[0].DESCRIPCIONTRANSPORTE);
                $("#procesaregresoshojaruta_hojaruta").val(data.data[0].HOJARUTA);
                $("#procesaregresoshojaruta_descripcionhojaruta").val(data.data[0].DESCRIPCIONHOJARUTA);
                $("#procesaregresoshojaruta_responsableruta").val(data.data[0].RESPONSABLE);
                $("#procesaregresoshojaruta_estado").val(data.data[0].ESTADO);
                $("#procesaregresoshojaruta_observacion").val(data.data[0].OBSERVACION);
                $("#procesaregresoshojaruta_dcaestado").val(data.data[0].DCAESTADO);

                if (data.data[0].DCAESTADO * 1 === 23) fn_procesaregresoshojaruta_habilitarCampos(true); else fn_procesaregresoshojaruta_habilitarCampos(false);
            }
            break;
        case 'addlot':
            if (data.data[0].MSG === 'ok') {
                $("#procesaregresoshojaruta_cantidad, #procesaregresoshojaruta_lote, #procesaregresoshojaruta_dmbcodigodestino").val("");
                fn_procesaregresoshojaruta_cargaGridDetalleEgresoRuta($("#procesaregresoshojaruta_codigo").val());
                fn_procesaregresoshojaruta_cargaGridLoteEgresoRuta($("#procesaregresoshojaruta_codigo").val(), $("#procesaregresoshojaruta_pgecodigo").val(), $("#procesaregresoshojaruta_pescodigo").val());
                var parametros = { json: 2092, dmbcodigo: id_dmbcodigo };
                llenaCombo($("#procesaregresoshojaruta_lote"), "/?option=json", parametros);
            }
            break;
        case 'dellot':
            if (data.data[0].MSG === 'ok') {
                fn_procesaregresoshojaruta_cargaGridDetalleEgresoRuta($("#procesaregresoshojaruta_codigo").val());
                fn_procesaregresoshojaruta_cargaGridLoteEgresoRuta($("#procesaregresoshojaruta_codigo").val(), $("#procesaregresoshojaruta_pgecodigo").val(), $("#procesaregresoshojaruta_pescodigo").val());
                var parametros = { json: 2092, dmbcodigo: id_dmbcodigo };
                llenaCombo($("#procesaregresoshojaruta_lote"), "/?option=json", parametros);
            }
            break;
        case 'proc':
            if (data.data[0].MSG === 'ok') {
                fn_procesaregresoshojaruta_habilitarCampos(false);
                fn_procesaregresoshojaruta_cargaGridDetalleEgresoRuta($("#procesaregresoshojaruta_codigo").val());
                $("#procesaregresoshojaruta_estado").val("PROCESADO");
                $("#procesaregresoshojaruta_flex_listaegresos").flexReload();
            }
            break;
    }
}

function fn_procesaregresoshojaruta_habilitarCampos(bool) {
    $("#procesaregresoshojaruta_lote, #procesaregresoshojaruta_cantidad").prop("disabled", !bool);
    $("#procesaregresoshojaruta_procesar").prop("disabled", !bool);
    $("#procesaregresoshojaruta_flex_detalle_lote").btnShowHide(bool);
}

function fn_procesaregresoshojaruta_buttonFlexgrid(btnId, grid) {
    switch (btnId) {
        case "procesaregresoshojaruta_flex_listaegresos_ver":
            var filasSeleccionadas = grid.getSelectedRowsIds();
            if (filasSeleccionadas.length > 0) {
               // if (
                    
                    mostrarConfirmacion("Este proceso recarga el formulario, si no ha guardado los cambios del proceso actual se perderán los cambios. \n¿Desea continuar.?",//)) {
                    function () {
                        fn_procesaregresoshojaruta_limpiarCampos();
                    var rowData = grid.getRowData(filasSeleccionadas[0]);
                    var id = rowData["MBO_CODIGO"];
                    var parametros = { json: 2091, mbocodigo: id };

                    getJson("/?option=json", parametros, "crgInfo", fn_procesaregresoshojaruta_aftersave);
                    fn_procesaregresoshojaruta_cargaGridDetalleEgresoRuta(id);

                    $("#procesaregresoshojaruta_li_reg").trigger("click");
                    $("#procesaregresoshojaruta_flex_listaegresos tr").removeClass("trSelected");
                    });
               // }
            } else {
                mostrarModal("Seleccione un registro para ser visualizado.");
            }
            break;
        case "procesaregresoshojaruta_flex_detalle_egreso_ver":
            var filasSeleccionadas = grid.getSelectedRowsIds();
            if (filasSeleccionadas.length > 0) {
                fn_procesaregresoshojaruta_limpiarCamposDetalle();
                var rowData = grid.getRowData(filasSeleccionadas[0]);
                var id = rowData["DMB_CODIGO"];
                id_dmbcodigo = id;
                if ($("#procesaregresoshojaruta_dcaestado").val() * 1 === 23) {
                    var parametros = { json: 2092, dmbcodigo: id };
                    llenaCombo($("#procesaregresoshojaruta_lote"), "/?option=json", parametros);
                }
                $("#procesaregresoshojaruta_dmbcodigoorigen").val(id);
                $("#procesaregresoshojaruta_grupo").val(rowData["GRUPO"]);
                $("#procesaregresoshojaruta_producto").val(rowData["PRODUCTO"]);
                $("#procesaregresoshojaruta_pgecodigo").val(rowData["PGE_CODIGO"]);
                $("#procesaregresoshojaruta_pescodigo").val(rowData["PES_CODIGO"]);

                fn_procesaregresoshojaruta_cargaGridLoteEgresoRuta($("#procesaregresoshojaruta_codigo").val(), rowData["PGE_CODIGO"], rowData["PES_CODIGO"]);

            } else {
                mostrarModal("Seleccione un registro para ser visualizado.");
            }
            break;
        case "procesaregresoshojaruta_flex_detalle_lote_agregar":
            var parametros = {};
            if ($("#procesaregresoshojaruta_frm_detalle").valid()) {
                parametros["dmborigen"] = $("#procesaregresoshojaruta_dmbcodigoorigen").val() === '' ? 'NULL' : $("#procesaregresoshojaruta_dmbcodigoorigen").val();
                parametros["dmbdestino"] = $("#procesaregresoshojaruta_dmbcodigodestino").val() === '' ? 'NULL' : $("#procesaregresoshojaruta_dmbcodigodestino").val();
                parametros["ilocodigo"] = $("#procesaregresoshojaruta_lote").val();
                parametros["cantidad"] = $("#procesaregresoshojaruta_cantidad").val();
                guardarObjetoData('addlot', parametros, 2096, fn_procesaregresoshojaruta_aftersave, null);
            }
            break;
        // case "procesaregresoshojaruta_flex_detalle_lote_editar":
        //     var filasSeleccionadas=grid.getSelectedRowsIds();
        //     if(filasSeleccionadas.length > 0){
        //         var id;
        //         for(var i in filasSeleccionadas){
        //             var rowData = grid.getRowData(filasSeleccionadas[i]);
        //             id = rowData["DMB_CODIGO"];
        //             $("#procesaregresoshojaruta_dmbcodigodestino").val(id);
        //             $("#procesaregresoshojaruta_lote").val(rowData["ILO_CODIGO"]);
        //             $("#procesaregresoshojaruta_cantidad").val(rowData["CANTIDAD"]);
        //         }
        //     }else{
        //         mostrarModal("Seleccione un registro a ser editado");
        //     }
        // break;
        case "procesaregresoshojaruta_flex_detalle_lote_eliminar":
            var filasSeleccionadas = grid.getSelectedRowsIds();
            if (filasSeleccionadas.length > 0) {
                for (var i in filasSeleccionadas) {
                    var rowData = grid.getRowData(filasSeleccionadas[i]);
                    guardarObjetoData('dellot', { "dmborigen": $("#procesaregresoshojaruta_dmbcodigoorigen").val(), "dmbdestino": rowData["DMB_CODIGO"] }, 2097, fn_procesaregresoshojaruta_aftersave, null);
                }
            } else {
                mostrarModal("Seleccione un registro a ser eliminado");
            }
            break;
    }
}
function fn_procesaregresoshojaruta_cargaGridDetalleEgresoRuta(id) {
    var flexParams = {
        url: "/?option=json",
        params: [
            { name: "json", value: 2094 },
            { name: "mbocodigo", value: id }
        ]
    };
    $("#procesaregresoshojaruta_flex_detalle_egreso").flexOptions(flexParams).flexReload();
}

function fn_procesaregresoshojaruta_cargaGridLoteEgresoRuta(mbo, pge, pes) {
    var flexParams = {
        url: "/?option=json",
        params: [
            { name: "json", value: 2095 },
            { name: "mbocodigo", value: mbo },
            { name: "pgecodigo", value: pge },
            { name: "pescodigo", value: pes }
        ]
    };
    $("#procesaregresoshojaruta_flex_detalle_lote").flexOptions(flexParams).flexReload();
}


