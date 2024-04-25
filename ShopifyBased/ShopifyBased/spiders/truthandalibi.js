function u() {
    var e = 0,
        t = 0;
    try {
        e = (new Date).getTime() >>> 0
    } catch (t) {
        e = (new Date).getTime() >>> 0
    }
    try {
        t = performance.now() >>> 0
    } catch (e) {
        t = 0
    }
    var n = Math.abs(e + t).toString(16).toLowerCase();
    return '00000000'.substr(0, 8 - n.length) + n
}

var a = "xxxx-4xxx-xxxx-xxxxxxxxxxxx";
var e = '';
try {
    var n = new Uint16Array(31);
    for (let i = 0, l = n.length; i < l; i++) {
        n[i] = Math.floor(Math.random() * 1024 * 1024);
    }
    var o = 0;
    e = a.replace(/[x]/g, (function(e) {
        for (var t = [], r = 1; r < arguments.length; r++) t[r - 1] = arguments[r];
        var i = n[o] % 16,
            a = 'x' === e ? i : 3 & i | 8;
        return o++,
            a.toString(16)
    })).toUpperCase()
} catch (t) {
    e = a.replace(/[x]/g, (function(e) {
        for (var t = [], n = 1; n < arguments.length; n++) t[n - 1] = arguments[n];
        var r = 16 * Math.random() | 0,
            o = 'x' === e ? r : 3 & r | 8;
        return o.toString(16)
    })).toUpperCase()
}
e = u() + '-' + e