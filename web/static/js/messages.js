function getMessagesDevEx(){
    var url = "http://127.0.0.1:8000/messages";
    $("#grid").dxDataGrid({
        dataSource: DevExpress.data.AspNet.createStore({
            key: "id",
            insertUrl: url,
            updateUrl: url,
            deleteUrl: url,
            loadUrl: url,
            onBeforeSend: function(method, ajaxOptions) {
                ajaxOptions.xhrFields = { withCredentials: true };
            }
        }),

        editing: {
            allowUpdating: true,    
            allowDeleting: true,
            allowAdding: true
        },

        remoteOperations: {
             sorting: true,
             paging: true
        },

        columns: [{
            dataField: "id",
            dataType: "number",
            allowEditing: true
        }, {
            dataField: "content"
        },
        {dataField: "sent_on"
    	allowEditing: true},
        {dataField: "user_from_id"
    	allowEditing: true},
        {dataField: "user_to_id"
    	allowEditing: true},
        {dataField: "user_from"
    	allowEditing: true},
        {dataField: "user_to"
        allowEditing: true
        }]

    }).dxDataGrid("instance");
}
