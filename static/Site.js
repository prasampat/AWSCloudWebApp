
var uri = "uknown";
var canLogin = false;
var canRegister = false;
var FileUploadUri = "";
function register(e) {
    try {


        canRegister = requiredFieldValidator("email");
        canRegister = requiredFieldValidator("password");
        canRegister = requiredFieldValidator("username");
        canRegister = requiredFieldValidator("passwordMatch");


        if (canRegister) {

            resetControl("email");
            resetControl("password");
            resetControl("username");
            resetControl("passwordMatch");
        } else {
     
            
            return false;
        }
   
    } catch (ex) {
        alert(ex);
    }


return true;
}

  

function returnToPreviousPage()
{
    window.history.back();
}
function getData() {

    $.ajax({
        type: "GET",
        url: uri,

        dataType: "json",
        success: function (data) {
            $("#FileList").empty();
            $(data).each(function (key, item) {

                $("#FileList").append($("<tr></tr>").append($("<td></td>").append($("<a href='" + item.file + "'>" + item.file + "</a>"))));
            }
            )

        }
    });


}

function uploadFile() {
    try {

        var Files = $("#Files");
        var FileLength = Files[0].files.length;
        var EmailList = $(".email");

        if (FileLength == 0) {

            $("#Errordisplay").text("Please select atleast one file to upload");

            return false;
        } else if (FileLength > 5) {

            $("#Errordisplay").text("Files may not exceed 5");

            return false;

        }
        else {

            $("#Errordisplay").text("");

        }

        var isEmpty = true;
        $.each(EmailList, function (index, item) {

            if (item.value != "") {
                isEmpty = false;

            }
        });

        if (isEmpty) {
            $("#Errordisplay").text("please provide atleast one email address");
            requiredFieldValidator(EmailList[0].id);
            
            return false
        }
        var formdata = new FormData();
        for(var i=0;i<FileLength;i++)
        {
            formdata.append("files", Files.files[i]);
        }
   

        $.each(EmailList, function (index, item) {
            if (item.value != "") {

                formdata.append("email" + index, item);
            }
        });
        $.ajax({
            type: "POST",
            dataType="json",
            url: FileUploadUri,
            contentType: false,
            processData: false,
            data: formdata,
            error: function (response) {            
                $.each(response, function (index, item) {
                    $("#Errordisplay").text(item);
                });

            },
            success: function (response) {
                $("#Errordisplay").css({ color: "green" });
                $.each(response, function (index, item) {
                    $("#Errordisplay").text(item);
                });          
                getData()
            }
        });
    } catch (ex) {
        alert(ex);
    }

    return true;

}
function login() {
    try {
        //alert(data.request())
        canLogin = requiredFieldValidator("email");
        canLogin = requiredFieldValidator("password");

        if (canLogin) {
            resetControl("email");
            resetControl("password");  
        } else {
            
            return false
        }
    } catch (ex) {
        alert(ex);
    }
    return true;
}
function requiredFieldValidator(controlname) {
    if ($("#" + controlname).val() == "") {
        $("#" + controlname).css({ border: "2px solid red" });
        $("#Errordisplay").text("field cannot be empty");
        return false;
    }
    function resetControl(controlname) {
        $("#" + controlname).css({ border: "none" });
    }

    return true;

}

function passMatch(data) {
    var p = $("#password").val()
    if (p != data.value) {
        $("#Errordisplay").text("passwords don't match");
        canRegister = false;

    } else {
        canRegister = true;
        $("#Errordisplay").text("");
    }

}
function passValidation(data) {
    var reg = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}/;

    var isMatch = new RegExp(reg).test(data.value);
    if (isMatch) {
        $("#Errordisplay").text("");
        canLogin = true;
    } else {
        canLogin = false;
        $("#Errordisplay").text("password must contain atleast 7 none numeric characters & and one single number");
    }


}