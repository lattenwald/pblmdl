#!/usr/bin/env node

var IMAGE_DATA_SEPARATOR = '\x00\x00\x00\x00scramble:';
var MIME_LENGTH = 20;
var SUBSTITUTE_MIN_LENGTH = 10000;

class i {
    static async descrambleUrl(e, t) {
        const s = await fetch(e).then((e => e.arrayBuffer())).then((e => new Uint8Array(e)));
        return i.descramble(s, t)
    }
    static async descrambleFile(f, t, to) {
        const fs = require('fs/promises');
        const c = await fs.readFile(f);
        var data = i.descramble(c, t);
        await fs.writeFile(to, data, {encoding: 'base64'});
        // await fs.writeFile(to, data);
    }
    static descramble(e, t) {
        const s = i.findEncodedImageBytesOffset(e);
        if (0 === s) throw new Error('Cannot find separator in the image data');
        return i.decodeImageBytes(e, s, t)
    }
    static decodeImageBytes(e, t, s) {
        const o = String.fromCharCode(...[
            ...e.slice(t, t + MIME_LENGTH)
        ].filter((e => e > 0))),
            r = e[t + MIME_LENGTH];
        if (e = e.slice(t + MIME_LENGTH + 1), 1 === r) {
            const t = (e, t) => (e % t + t) % t;
            for (let o = 0, i = e.length; o < i; o++) e[o] = t(e[o] - s, 256)
        }
        const n = [];
        for (let i = 0; i < e.length; i += 5000) n.push(String.fromCharCode.apply(null, Array.from(e.slice(i, i + 5000))));
        return btoa(n.join(''))
    }
    static findEncodedImageBytesOffset(e) {
        const t = IMAGE_DATA_SEPARATOR.split('').map((e => e.charCodeAt(0))),
            s = t[0];
        e: for (let o = SUBSTITUTE_MIN_LENGTH, r = e.length; o < r; o++) if (e[o] === s) {
            for (let s = 1; s < t.length; s++) if (e[o + s] !== t[s]) continue e;
            return o + t.length
        }
        return 0
    }
}

var img = process.argv[2];
var offset = process.argv[3];
var to = process.argv[4];
console.log("descrambling " + img);
i.descrambleFile(img, offset, to);
