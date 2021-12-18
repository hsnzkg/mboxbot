function img_find() {
    var momos = document.querySelector("#mypet > div:nth-child(4) > div")
    var imgs = momos.getElementsByClassName("opa-4")
    var imgSrcs = [];
    for (var i = 0; i < imgs.length; i++) {
        imgSrcs.push(imgs[i].src);
    }   
    return imgSrcs;
}
