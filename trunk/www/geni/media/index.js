window.onload = function() {
	var tabs = $$(".tab");
	for (var i = 0;i < tabs.length;i++) {
		tabs[i].onclick = switchTab;
	}
	if (BrowserDetect.OS == "Win") {
		$("win").src = "{{ MEDIA URL }}bigwin.jpg";
	} else if (BrowserDetect.OS == "Mac") {
		$("osx").src = "{{ MEDIA URL }}bigosx.jpg";
	} else if (BrowserDetect.OS == "Linux") {
		$("linux").src = "{{ MEDIA URL }}biglinux.jpg";
	} else {
	}
	$("checkAll").onclick = checkAll;
};

function switchTab() {
	var index = (Number)(this.id[3]);
	var windows = $$(".window");
	var tabs = $$(".tab");
	for (var i = 0;i < windows.length;i++) {
		windows[i].style.display = "none";
		tabs[i].removeClassName("highlighted");
	}
	$("window" + index).style.display = "block";
	this.addClassName("highlighted");
	
}

function checkAll() {
	var checkboxes = $$("check");
	for (var i = 0;i < checkboxes.length;i++) {
		checkboxes[i].checked = "true";
	}
}

/*Free online downloaded script that can return OS, Browser Name, and Browser Version, used for browser compatibility purposes*/
var BrowserDetect = {
	init: function () {
		this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
		this.version = this.searchVersion(navigator.userAgent)
			|| this.searchVersion(navigator.appVersion)
			|| "an unknown version";
		this.OS = this.searchString(this.dataOS) || "an unknown OS";
	},
	searchString: function (data) {
		for (var i=0;i<data.length;i++)	{
			var dataString = data[i].string;
			var dataProp = data[i].prop;
			this.versionSearchString = data[i].versionSearch || data[i].identity;
			if (dataString) {
				if (dataString.indexOf(data[i].subString) != -1)
					return data[i].identity;
			}
			else if (dataProp)
				return data[i].identity;
		}
	},
	searchVersion: function (dataString) {
		var index = dataString.indexOf(this.versionSearchString);
		if (index == -1) return;
		return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
	},
	dataBrowser: [
		{
			string: navigator.userAgent,
			subString: "Chrome",
			identity: "Chrome"
		},
		{ 	string: navigator.userAgent,
			subString: "OmniWeb",
			versionSearch: "OmniWeb/",
			identity: "OmniWeb"
		},
		{
			string: navigator.vendor,
			subString: "Apple",
			identity: "Safari"
		},
		{
			prop: window.opera,
			identity: "Opera"
		},
		{
			string: navigator.vendor,
			subString: "iCab",
			identity: "iCab"
		},
		{
			string: navigator.vendor,
			subString: "KDE",
			identity: "Konqueror"
		},
		{
			string: navigator.userAgent,
			subString: "Firefox",
			identity: "Firefox"
		},
		{
			string: navigator.vendor,
			subString: "Camino",
			identity: "Camino"
		},
		{		// for newer Netscapes (6+)
			string: navigator.userAgent,
			subString: "Netscape",
			identity: "Netscape"
		},
		{
			string: navigator.userAgent,
			subString: "MSIE",
			identity: "Explorer",
			versionSearch: "MSIE"
		},
		{
			string: navigator.userAgent,
			subString: "Gecko",
			identity: "Mozilla",
			versionSearch: "rv"
		},
		{ 		// for older Netscapes (4-)
			string: navigator.userAgent,
			subString: "Mozilla",
			identity: "Netscape",
			versionSearch: "Mozilla"
		}
	],
	dataOS : [
		{
			string: navigator.platform,
			subString: "Win",
			identity: "Windows"
		},
		{
			string: navigator.platform,
			subString: "Mac",
			identity: "Mac"
		},
		{
			string: navigator.platform,
			subString: "Linux",
			identity: "Linux"
		}
	]

};
BrowserDetect.init();