
function LliureXGuard(){
    this.BlackLists={"domainLists":[]};
    this.WhiteLists={"domainLists":[]};
}


// Init Function
LliureXGuard.prototype.init=function init(){
  //alert( this._("LliurexGuard Start!"));

}

// I18n
LliureXGuard.prototype._=function _(text){
  //console.log(i18n);
  return ( i18n.gettext("lliurex-guard", text));
}


LliureXGuard.prototype.getStatus=function getStatus(){
  var self=this;

  var credentials=null;
  var n4dclass="LliurexGuard";
  var n4dmethod="getStatus";
  var arglist="";

  Utils.n4d(null, n4dclass, n4dmethod, arglist, function(response){
    var optionRadio=null;
    if (response["config"]=="allow")
                optionRadio="#llx-guard_permissive";
    else if (response["config"]=="deny")
                optionRadio="#llx-guard_restrictive";

    $(optionRadio).attr("checked","checked");

    var llx_guard_status;
    var llx_guard_policy;
    if(response["status"]=="running") llx_guard_status=self._("llx-guard-running");
      else llx_guard_status=self._("llx-guard-not-running");

      if(response["config"]=="deny") llx_guard_policy=self._("llx-guard.policy.restrictive");
        else llx_guard_policy=self._("llx-guard.policy.permissive");

    $("#llx-guard-status").html(llx_guard_status);
    $("#llx-guard-policy").html(llx_guard_policy);
  },0);

    /*$.xmlrpc({
			url: 'https://'+sessionStorage.server+':9779',
			methodName: 'getStatus',
			params: ["", "LliurexGuard"],
			success: function(response,status,jqXHR){
				console.log(response[0]);
				var optionRadio=null;
				if (response[0]["config"]=="allow")
                    optionRadio="#llx-guard_permissive";
				else if (response[0]["config"]=="deny")
                    optionRadio="#llx-guard_restrictive";

				$(optionRadio).attr("checked","checked");

        var llx_guard_status;
        var llx_guard_policy;
        if(response[0]["status"]=="running") llx_guard_status=self._("llx-guard-running");
          else llx_guard_status=self._("llx-guard-not-running");

          if(response[0]["config"]=="deny") llx_guard_policy=self._("llx-guard.policy.restrictive");
            else llx_guard_policy=self._("llx-guard.policy.permissive");

        $("#llx-guard-status").html(llx_guard_status);
        $("#llx-guard-policy").html(llx_guard_policy);

			},
			error: function(jqXHR, status, error) {
				//alert("Status: "+status+"\nError: N4d server is down"+error);
                $("#snack").attr("data-content", "N4d.Error.Connection");
                $("#snack").snackbar("show");
			}
		})*/

}


LliureXGuard.prototype.ApplyPolicy=function ApplyPolicy(){
  var self=this;
  var policy =$("#llx-guard_radioPolicy input:radio:checked").val();

  var blackchecks=$("#llx-guard_BlackList").find("input[type='checkbox']:checked");
  var whitechecks=$("#llx-guard_WhiteList").find("input[type='checkbox']:checked");
  var blacklist=[]
  var whitelist=[]
  var n4dparams={};
  var classdomain="";
  for (i=0;i<blackchecks.length;i++)
          blacklist.push($(blackchecks[i]).attr("file"));

  for (i=0;i<whitechecks.length;i++){
          var file=$(whitechecks[i]).attr("file");
          if (typeof(file)!=="undefined")
                  whitelist.push(file);

          var domain=$(whitechecks[i]).attr("classdomain");
          if (typeof(domain)!=="undefined")
                  classdomain=domain;
                  // No cal fer el push en esta llista, sino tractar-ho com a una variable apart que
                  // S'enviarà com a altre paràmetre
  }

    n4dparams={
        "policy":policy,
        "whitelist":whitelist,
        "blacklist":blacklist,
        "classdomain":classdomain
  };


      // Now let's call n4d method to apply Policy

      $("body").css("cursor", "wait");

      var credentials=[sessionStorage.username , sessionStorage.password];
      var n4dclass="LliurexGuard";
      var n4dmethod="applyPolicy";
      var arglist=[n4dparams];

      Utils.n4d(credentials, n4dclass, n4dmethod, arglist, function(response){
        $("body").css("cursor", "auto");
        try{
          console.log(response);
          var message="";
          if (response["status"]=="true") {
            message=self._("llx-guard.config.applied.ok");
            Utils.msg(message, MSG_SUCCESS);
          }
          else {
            message=self._("llx-guard.config.applied.error");
            Utils.msg(message, MSG_ERROR);
          }
        }catch(e){
          message=self._("llx-guard.config.applied.error");
          Utils.msg(message, MSG_ERROR);
        }

      },0);



      /*$.xmlrpc({
			url: 'https://'+sessionStorage.server+':9779',
			methodName: 'applyPolicy',
			params: [[sessionStorage.username , sessionStorage.password], "LliurexGuard", n4dparams],
			success: function(response,status,jqXHR){
                $("body").css("cursor", "auto");
                var message="";
                if (response[0]["status"]=="true") {
                  message=self._("llx-guard.config.applied.ok");
                  Utils.msg(message, MSG_SUCCESS);
                }
                else {
                  message=self._("llx-guard.config.applied.error");
                  Utils.msg(message, MSG_ERROR);
                }

			},
			error: function(jqXHR, status, error) {
                message=self._("llx-guard.N4d.Error.Connection");
                Utils.msg(message, MSG_ERROR);
			}
		})*/

}


LliureXGuard.prototype.editList=function editList(title, domainList, targetListFile){
  var self=this;
  
  var textArea=$(document.createElement("textarea")).addClass("form-control").attr("rows", 13).attr("id", "llx-guard_customList");
  $(textArea).html(domainList);

  bootbox.dialog({
    title: self._(title),
    message: textArea,
    buttons: {
      succes:{
        label: self._("llx-guard.Save.changes"),
        className: "btn-primary",
        callback: function(){
          var content=$("#llx-guard_customList").val().trim()+"\n";

          var credentials=[sessionStorage.username , sessionStorage.password];
          var n4dclass="LliurexGuard";
          var n4dmethod="setCustomList";
          //var arglist=[content, targetListFile];
          var arglist=[];
          arglist.push(content);
          arglist.push(targetListFile);


          try{
            Utils.n4d(credentials, n4dclass, n4dmethod, arglist, function(response){
              message=self._("llx-guard.File Saved");
              Utils.msg(message, MSG_SUCCESS);
            },0);
          } catch(err){
            message=self._("n4d.error")+":"+err;
            Utils.msg(message, MSG_ERROR);
          }

          /*$.xmlrpc({
                 url: 'https://'+sessionStorage.server+':9779',
                 methodName: 'setCustomList',
                 params: [[sessionStorage.username , sessionStorage.password], "LliurexGuard", content, targetListFile],
                 success: function(response,status,jqXHR){
                         message=self._("llx-guard.File Saved");
                         Utils.msg(message, MSG_SUCCESS);
                       },
                 error: function(jqXHR, status, error) {
                         message=self._("N4d.Error.Connection");
                         Utils.msg(message, MSG_ERROR);
                 }
         })*/

        }
      },
      cancel: {
      label: self._("llx-guard.Close"),
      className: "btn-cancel",
      callback: function(){
        /*var content=$("#llx-guard_customList").val();
        var orig=$("#llx-guard_customList").html();
        var ret;
        if(content!==orig){
          //bootbox.confirm("Are you sure?", function(result) {
          //    if (result)
          //});
          alert("different content");
          return false;
          //alert(ret);
          //return ret;
        }*/

      }
    }
  } // end buttons
  });
};


LliureXGuard.prototype.prepareList=function prepareList(targetListFile, callback){
  // Reads list in targetListFile, and when finishes, returns it to callback function
  // (callback should be editList)

  var self=this;
  var contentList=[];

  // Set cursor waiting
  $("body").css("cursor", "wait");

  // Prepare Ajax call
  var credentials="";
  var n4dclass="LliurexGuard";
  var n4dmethod="getCustomList";
  var arglist=[targetListFile];

  try{
    Utils.n4d(credentials, n4dclass, n4dmethod, arglist, function(response){
      $("body").css("cursor", "auto");
      contentList=response["response"];
      callback(contentList);
    },0)
  } catch (err){
    $("body").css("cursor", "auto");
    message=self._("N4d.Error.Connection");
    Utils.msg(message, MSG_ERROR);
  }

  /*$.xmlrpc({
          url: 'https://'+sessionStorage.server+':9779',
          methodName: 'getCustomList',
          params: ["", "LliurexGuard", targetListFile],
          success: function(response,status,jqXHR){
            contentList=response[0]["response"];
            callback(contentList);
              //$("#"+llx_guard_customList).val(content);
            },
          error: function(jqXHR, status, error) {
                  message=self._("N4d.Error.Connection");
                  Utils.msg(message, MSG_ERROR);
          }
  })*/
}

LliureXGuard.prototype.drawBlackList=function drawBlackList(){
      var self=this;

      // Prepare Ajax call
      var credentials="";
      var n4dclass="LliurexGuard";
      var n4dmethod="getBlackList";
      var arglist=[];

      try{
        Utils.n4d(credentials, n4dclass, n4dmethod, arglist, function(response){
          self.BlackLists=response["response"];
          // Empty list
          $("#llx-guard_BlackList").empty();

          for (i in self.BlackLists["domainLists"]){
                  var item=self.BlackLists["domainLists"][i];
                  var divcb=$(document.createElement("div")).addClass("checkbox checkbox-primary").css("border-top","1px solid #cccccc");
                  var label=$(document.createElement("label"));
                  var input=$(document.createElement("input")).attr("name", "blacklistGroup").attr("file",item["file"]).attr("id", item["file"]).attr("type", "checkbox");
                  if (item["active"]=="True") $(input).attr("checked", "checked");
                  //var spanDesc=$(document.createElement("span")).css("{padding:0px; }");
                  var spanDesc=$(document.createElement("span")).css({"padding":"0px", "margin-left":"20px", "top":"-3px", "width":"400px;"});
                  $(spanDesc).html(self._("llx-guard."+item["description_short"]));

                  var divdesc=$(document.createElement("div")).addClass("radiodescription").html(self._("llx-guard."+item["description"]));

                  customBt=null;
                  if (item["file"]=="z_custom.list") {
                          var customBt=$(document.createElement("button")).addClass("btn btn-primary btn-xs pull-right").html(self._("llx-guard.customize.list"));
                          $(customBt).on("click", function(){
                            
                            self.prepareList("z_custom.list", function(list){
                              self.editList("llx-guard.Edit.Blacklist", list, "z_custom.list");
                            });
                          });
                          //$(customBt).attr("data-toggle", "modal").attr("data-target","#llx-guard_editCustomBlackList");
                          $(label).append(input, spanDesc);
                          $(divcb).append(label, divdesc, customBt);
                          $(divcb).css("min-height","80px");
                          $("#llx-guard_BlackList").prepend(divcb);
                  } else {
                        $(label).append(input, spanDesc);
                        $(divcb).append(label, divdesc, customBt);
                        $("#llx-guard_BlackList").append(divcb);
                  }
          }
          $.material.init();

        },0)
      } catch (err){
        $("body").css("cursor", "auto");
        message=self._("N4d.Error.Connection");
        Utils.msg(message, MSG_ERROR);
      }

      /*$.xmlrpc({
			url: 'https://'+sessionStorage.server+':9779',
			methodName: 'getBlackList',
			params: ["", "LliurexGuard"],
			success: function(response,status,jqXHR){

                self.BlackLists=response[0]["response"];
                // Empty list
                $("#llx-guard_BlackList").empty();

                for (i in self.BlackLists["domainLists"]){
                        var item=self.BlackLists["domainLists"][i];
                        var divcb=$(document.createElement("div")).addClass("checkbox checkbox-primary").css("border-top","1px solid #cccccc");
                        var label=$(document.createElement("label"));
                        var input=$(document.createElement("input")).attr("name", "blacklistGroup").attr("file",item["file"]).attr("id", item["file"]).attr("type", "checkbox");
                        if (item["active"]=="True") $(input).attr("checked", "checked");
                        //var spanDesc=$(document.createElement("span")).css("{padding:0px; }");
                        var spanDesc=$(document.createElement("span")).css({"padding":"0px", "margin-left":"20px", "top":"-3px", "width":"400px;"});
                        $(spanDesc).html(self._("llx-guard."+item["description_short"]));

                        var divdesc=$(document.createElement("div")).addClass("radiodescription").html(self._("llx-guard."+item["description"]));

                        customBt=null;
                        if (item["file"]=="z_custom.list") {
                                var customBt=$(document.createElement("button")).addClass("btn btn-primary btn-xs pull-right").html(self._("llx-guard.customize.list"));
                                $(customBt).on("click", function(){
                                  self.prepareList("z_custom.list", function(list){
                                    self.editList("llx-guard.Edit.Blacklist", list, "z_custom.list");
                                  });
                                });
                                //$(customBt).attr("data-toggle", "modal").attr("data-target","#llx-guard_editCustomBlackList");
                                $(label).append(input, spanDesc);
                                $(divcb).append(label, divdesc, customBt);
                                $(divcb).css("min-height","80px");
                                $("#llx-guard_BlackList").prepend(divcb);
                        } else {
                              $(label).append(input, spanDesc);
                              $(divcb).append(label, divdesc, customBt);
                              $("#llx-guard_BlackList").append(divcb);
                        }
                }
                $.material.init();
			},
			error: function(jqXHR, status, error) {
				//alert("Status: "+status+"\nError: N4d server is down"+error);
                Utils.msg(self._("N4d.Error.Connection"), MSG_ERROR);

			}
		})*/
}




LliureXGuard.prototype.drawWhiteList=function drawWhiteList(){
    var self=this;


    // Prepare Ajax call
    var credentials="";
    var n4dclass="LliurexGuard";
    var n4dmethod="getWhiteList";
    var arglist=[];

    try{
      Utils.n4d(credentials, n4dclass, n4dmethod, arglist, function(response){
        self.WhiteLists=response["response"];

        $("#llx-guard_WhiteList").empty();

          for (i in self.WhiteLists["domainLists"]){

                var item=self.WhiteLists["domainLists"][i];

                var divcb=$(document.createElement("div")).addClass("checkbox checkbox-primary").css("border-top","1px solid #cccccc");
                var label=$(document.createElement("label"));
                var input=$(document.createElement("input")).attr("name", "whitelistGroup").attr("file",item["file"]).attr("classdomain",item["domain"]).attr("id", item["file"]).attr("type", "checkbox");
                if (item["active"]=="True") $(input).attr("checked", "checked");
                //var spanDesc=$(document.createElement("span")).css("{padding:0px; }");
                var spanDesc=$(document.createElement("span")).css({"padding":"0px", "margin-left":"20px", "top":"-3px", "width":"400px;"});
                var desc_short=self._(item["description_short"]);
                if (item["domain"]) desc_short=desc_short+" ("+item["domain"]+")";
                $(spanDesc).html(desc_short);

                var divdesc=$(document.createElement("div")).addClass("radiodescription").html(self._(item["description"]));

                customBt=null;
                if (item["file"]=="z_customwhite.list") {
                        var customBt=$(document.createElement("button")).addClass("btn btn-primary btn-xs pull-right").html(self._("customize.list"));
                        //$(customBt).attr("data-toggle", "modal").attr("data-target","#llx-guard_editCustomWhiteList");
                        $(customBt).on("click", function(){
                          self.prepareList("z_customwhite.list", function(list){
                            self.editList("llx-guard.Edit.Whitelist", list, "z_customwhite.list");
                          });
                        });

                        $(label).append(input, spanDesc);
                        $(divcb).append(label, divdesc, customBt);
                        $(divcb).css("min-height","80px");
                        $("#llx-guard_WhiteList").prepend(divcb);


                } else {
                      $(label).append(input, spanDesc);
                      $(divcb).append(label, divdesc, customBt);
                      $("#llx-guard_WhiteList").append(divcb);
                 }
        }

        $.material.init();



      },0)
    } catch (err){
      $("body").css("cursor", "auto");
      message=self._("N4d.Error.Connection");
      Utils.msg(message, MSG_ERROR);
    }




    /*$.xmlrpc({
			url: 'https://'+sessionStorage.server+':9779',
			methodName: 'getWhiteList',
			params: ["", "LliurexGuard"],
			success: function(response,status,jqXHR){
                self.WhiteLists=response[0]["response"];

                $("#llx-guard_WhiteList").empty();

                  for (i in self.WhiteLists["domainLists"]){

                        var item=self.WhiteLists["domainLists"][i];

                        var divcb=$(document.createElement("div")).addClass("checkbox checkbox-primary").css("border-top","1px solid #cccccc");
                        var label=$(document.createElement("label"));
                        var input=$(document.createElement("input")).attr("name", "whitelistGroup").attr("file",item["file"]).attr("classdomain",item["domain"]).attr("id", item["file"]).attr("type", "checkbox");
                        if (item["active"]=="True") $(input).attr("checked", "checked");
                        //var spanDesc=$(document.createElement("span")).css("{padding:0px; }");
                        var spanDesc=$(document.createElement("span")).css({"padding":"0px", "margin-left":"20px", "top":"-3px", "width":"400px;"});
                        var desc_short=self._(item["description_short"]);
                        if (item["domain"]) desc_short=desc_short+" ("+item["domain"]+")";
                        $(spanDesc).html(desc_short);

                        var divdesc=$(document.createElement("div")).addClass("radiodescription").html(self._(item["description"]));

                        customBt=null;
                        if (item["file"]=="z_customwhite.list") {
                                var customBt=$(document.createElement("button")).addClass("btn btn-primary btn-xs pull-right").html(self._("customize.list"));
                                //$(customBt).attr("data-toggle", "modal").attr("data-target","#llx-guard_editCustomWhiteList");
                                $(customBt).on("click", function(){
                                  self.prepareList("z_customwhite.list", function(list){
                                    self.editList("llx-guard.Edit.Whitelist", list, "z_customwhite.list");
                                  });
                                });

                                $(label).append(input, spanDesc);
                                $(divcb).append(label, divdesc, customBt);
                                $(divcb).css("min-height","80px");
                                $("#llx-guard_WhiteList").prepend(divcb);


                        } else {
                              $(label).append(input, spanDesc);
                              $(divcb).append(label, divdesc, customBt);
                              $("#llx-guard_WhiteList").append(divcb);
                         }
                }

                $.material.init();

			},
			error: function(jqXHR, status, error) {

				            //alert("Status: "+status+"\nError: N4d server is down"+error);
                  Utils.msg(self._("N4d.Error.Connection"), MSG_ERROR);
			}
		})*/


}




LliureXGuard.prototype.bindEvents=function bindEvents(){
  var self=this;

  // Module Loaded: Triggered when a module is fully loaded (html and scripts)
  $(document).on("moduleLoaded", function(e, args){
    var moduleName="lliurex-guard";
    console.log(args["moduleName"]);
    if(args["moduleName"]===moduleName)
      llxGuard.init();
  });

  // componentShown: Triggered when a module component is clicked
  $("#lliurex-guard").on("componentClicked", function(e, args){
    // Refresh status
    self.getStatus();
  });

  /*$("#lliurex-guard_set_policy").on("componentShown", function(e, args){

  });*/

  $("#lliurex-guard_edit_blacklist").on("componentShown", function(e, args){
    self.drawBlackList();

  $("#llx-guard_CancelButtonBlacklist").off("click");
  $("#llx-guard_CancelButtonBlacklist").on("click", function(){
    self.drawBlackList();
  });


  });

  $("#lliurex-guard_edit_whitelist").on("componentShown", function(e, args){
    self.drawWhiteList();

    $("#llx-guard_CancelButtonWhitelist").off("click");
    $("#llx-guard_CancelButtonWhitelist").on("click", function(){
      self.drawWhiteList();
    });
  });


  $("#llx-guard_ApplyButtonPolicy").on("click",function(){
          self.ApplyPolicy();
        });

  $("#llx-guard_ApplyButtonBlacklist").on("click",function(){
          self.ApplyPolicy();
        });

  $("#llx-guard_ApplyButtonWhitelist").on("click",function(){
          self.ApplyPolicy();
        });


}

var llxGuard=new LliureXGuard();
llxGuard.bindEvents();
//llxGuard.bindModalEvents();
llxGuard.getStatus();
// Binding events
