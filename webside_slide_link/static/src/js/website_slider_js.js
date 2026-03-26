odoo.define('webside_slide_link.fullscreen', function (require) {
"use strict";



var core = require('web.core');
var QWeb = core.qweb;
var FullscreenCustom = require('@website_slides/js/slides_course_fullscreen_player')[Symbol.for("default")];
FullscreenCustom.include({
    xmlDependencies: (FullscreenCustom.prototype.xmlDependencies || []).concat(
        ["/webside_slide_link/static/src/xml/website_full_screen_extend.xml"]
    ),

    /**
     * Extend the _renderSlide method so that slides of type "certification"
     * are also taken into account and rendered correctly
     *
     * @private
     * @override
     */
    _renderSlide: async function (){
        var def = this._super.apply(this, arguments);
        var $content = this.$('.o_wslides_fs_content');
        
        if (this.get('slide').type === "certification"){
            $content.html(QWeb.render('website.slides.fullscreen.certification.custom',{widget: this}));
        }
        await this._rpc({
                model: 'slide.slide',
                method: 'get_linked_records_info',
                args: [this.get('slide').id],
            }).then(result => {
                if(result[0]==1){
                    var ifrm = document.createElement('iframe');
                    ifrm.setAttribute('title', 'LINK');
                    ifrm.setAttribute('src', result[1]); // assign an id
                    ifrm.setAttribute('width', '100%'); // assign an id



  $content[0].innerHTML=''
  $content[0].appendChild(ifrm)
                    
                }
            })
        if (this.get('slide').type === "video"){
        var video_tag = $content[0].getElementsByTagName('iframe')
        var main_tag = video_tag[0].getElementsByTagName('video')
        var src=video_tag[0].src
        video_tag[0].remove()
        var ifrm = document.createElement('video');
                    ifrm.setAttribute('controls', '');
                    ifrm.setAttribute('autoplay', ''); // assign an id
                    ifrm.setAttribute('name', 'media'); 
                    ifrm.setAttribute('controlsList', 'nodownload'); 
                    ifrm.setAttribute('oncontextmenu', 'return false;'); 
                    ifrm.setAttribute('width', '100%');
                    ifrm.setAttribute('height', '100%'); 
        var source = document.createElement('source');
                    source.setAttribute('src',src)
                    ifrm.setAttribute("type","video/mp4")
        ifrm.appendChild(source)            
                    // ifrm.setAttribute("controlsList","nodownload")



  $content[0].innerHTML=''
  $content[0].appendChild(ifrm)
  // var innerDoc = ifrm.contentDocument || ifrm.contentWindow.document;
  //  console.log(innerDoc.body);
}
        //video_tag[0].setAttribute("allow","nodownload", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture");

        return Promise.all([def]);
    },
});
});


