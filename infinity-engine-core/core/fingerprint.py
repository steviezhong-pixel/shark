"""Browser fingerprint generation and anti-detection init scripts.

Compared to the previous JS-only spoofing, this version mirrors how
native engines (e.g. GoLogin's Orbita) behave:
  * navigator.* props are defined on Navigator.prototype with the same
    descriptor shape real Chrome uses (webdriver is a data property
    "false", not a getter returning undefined).
  * Canvas noise is applied at getImageData time so every read path
    (getImageData / toDataURL / toBlob / OffscreenCanvas) returns the
    same deterministic, position-stable noise.
  * WebGL masks VENDOR/RENDERER/VERSION/GLSL via getParameter, the
    WEBGL_debug_renderer_info extension, and optionally adds precision
    noise (webgl_noise).
  * WebGPU adapter info is masked (navigator.gpu).
  * Optional sub-pixel clientRects noise.
"""

import json
import random

CHROME_VERSIONS = list(range(128, 152))

UA_TEMPLATES = {
    "MacIntel": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.0.0 Safari/537.36",
    "Win32": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.0.0 Safari/537.36",
}

LOCALE_OPTIONS = [
    ("en-US", "America/New_York", ["en-US", "en"]),
    ("en-GB", "Europe/London", ["en-GB", "en"]),
    ("zh-CN", "Asia/Shanghai", ["zh-CN", "zh"]),
    ("zh-TW", "Asia/Taipei", ["zh-TW", "zh"]),
    ("zh-HK", "Asia/Hong_Kong", ["zh-HK", "zh"]),
    ("ja-JP", "Asia/Tokyo", ["ja-JP", "ja"]),
    ("ko-KR", "Asia/Seoul", ["ko-KR", "ko"]),
    ("de-DE", "Europe/Berlin", ["de-DE", "de"]),
    ("fr-FR", "Europe/Paris", ["fr-FR", "fr"]),
    ("es-ES", "Europe/Madrid", ["es-ES", "es"]),
    ("ru-RU", "Europe/Moscow", ["ru-RU", "ru"]),
    ("pt-BR", "America/Sao_Paulo", ["pt-BR", "pt"]),
    ("vi-VN", "Asia/Ho_Chi_Minh", ["vi-VN", "vi"]),
    ("th-TH", "Asia/Bangkok", ["th-TH", "th"]),
    ("id-ID", "Asia/Jakarta", ["id-ID", "id"]),
]

SCREENS = [
    (1920, 1080, 1.0),
    (2560, 1440, 1.0),
    (1440, 900, 1.0),
    (1680, 1050, 1.0),
    (1536, 864, 1.0),
    (1366, 768, 1.0),
    (1920, 1080, 2.0),
    (2560, 1440, 2.0),
]

WEBGL_OPTIONS = {
    "MacIntel": [
        ("Google Inc. (Apple)", "ANGLE (Apple, Apple M1, OpenGL 4.1 Metal - 83.1)"),
        ("Google Inc. (Apple)", "ANGLE (Apple, Apple M2 Pro, OpenGL 4.1 Metal - 89.1)"),
        ("Google Inc. (Apple)", "ANGLE (Apple, Apple M3, OpenGL 4.1 Metal - 93.1)"),
        ("Google Inc. (Apple)", "ANGLE (Apple, Apple M4, OpenGL 4.1 Metal - 97.1)"),
    ],
    "Win32": [
        ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
        ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 4060 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
        ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
        ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
        ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon(TM) Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ],
}

WEBGL_VERSION_TMPL = "WebGL 2.0 (OpenGL ES 3.0 {renderer})"
GLSL_VERSION = "OpenGL ES GLSL ES 3.00 (OpenGL ES GLSL ES 3.00 Chromium)"


def _gpu_name(renderer: str) -> str:
    """Extract the GPU model from an ANGLE renderer string, e.g.
    'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11...' -> 'NVIDIA GeForce RTX 3060'."""
    body = renderer
    if "(" in body:
        body = body.split("(", 1)[1]
    parts = [p.strip() for p in body.split(",")]
    for p in parts:
        if p and not p.lower().startswith("angle"):
            return p
    return renderer


def _webgpu_for(renderer: str) -> dict:
    gpu = _gpu_name(renderer)
    vendor = gpu.split()[0] if gpu else "Google Inc."
    return {
        "vendor": vendor,
        "architecture": "common",
        "device": gpu,
        "description": gpu,
        "driver": "",
    }


def generate_fingerprint() -> dict:
    platform = random.choice(["MacIntel", "Win32"])
    version = random.choice(CHROME_VERSIONS)
    ua = UA_TEMPLATES[platform].format(ver=version)

    locale, timezone, languages = random.choice(LOCALE_OPTIONS)
    width, height, scale = random.choice(SCREENS)
    webgl_vendor, webgl_renderer = random.choice(WEBGL_OPTIONS[platform])
    webgpu = _webgpu_for(webgl_renderer)

    return {
        "ua": ua,
        "platform": platform,
        "language": locale,
        "languages": languages,
        "timezone": timezone,
        "screen_width": width,
        "screen_height": height,
        "device_scale_factor": scale,
        "hardware_concurrency": random.choice([4, 6, 8, 8, 10, 12, 16]),
        "device_memory": random.choice([4, 8, 8, 16, 32]),
        "max_touch_points": 0,
        "color_depth": random.choice([24, 24, 24, 30]),
        "webgl_vendor": webgl_vendor,
        "webgl_renderer": webgl_renderer,
        "webgl_version": WEBGL_VERSION_TMPL.format(renderer=webgl_renderer),
        "webgl_noise": random.choice([0.0, 0.0, 0.001, 0.002]),
        "webgpu_vendor": webgpu["vendor"],
        "webgpu_architecture": webgpu["architecture"],
        "webgpu_device": webgpu["device"],
        "webgpu_description": webgpu["description"],
        "webgpu_driver": webgpu["driver"],
        "canvas_noise": True,
        "canvas_noise_seed": random.randint(1, 2**31),
        "client_rects_noise": 0.0,
        "audio_noise": 0.0,
        "fonts": [],
        "media_devices": None,
        "do_not_track": None,
    }


def _cfg(fp: dict) -> dict:
    """Extract the init-script config, defaulting gracefully for older profiles."""
    fonts = fp.get("fonts") or []
    md = fp.get("media_devices")
    return {
        "platform": fp.get("platform", "Win32"),
        "language": fp.get("language", "en-US"),
        "languages": fp.get("languages", ["en-US", "en"]),
        "hardware_concurrency": fp.get("hardware_concurrency", 4),
        "device_memory": fp.get("device_memory", 8),
        "max_touch_points": fp.get("max_touch_points", 0),
        "color_depth": fp.get("color_depth", 24),
        "webgl_vendor": fp.get("webgl_vendor", ""),
        "webgl_renderer": fp.get("webgl_renderer", ""),
        "webgl_version": fp.get("webgl_version", ""),
        "webgl_noise": float(fp.get("webgl_noise", 0.0) or 0.0),
        "webgpu_vendor": fp.get("webgpu_vendor", ""),
        "webgpu_architecture": fp.get("webgpu_architecture", "common"),
        "webgpu_device": fp.get("webgpu_device", ""),
        "webgpu_description": fp.get("webgpu_description", ""),
        "webgpu_driver": fp.get("webgpu_driver", ""),
        "canvas_noise": bool(fp.get("canvas_noise", True)),
        "canvas_noise_seed": fp.get("canvas_noise_seed", 1),
        "client_rects_noise": float(fp.get("client_rects_noise", 0.0) or 0.0),
        "audio_noise": float(fp.get("audio_noise", 0.0) or 0.0),
        "fonts": fonts,
        "media_devices": md if isinstance(md, dict) and md.get("uid") else None,
        "do_not_track": fp.get("do_not_track"),
    }


def build_init_script(fp: dict) -> str:
    cfg = _cfg(fp)
    js = r"""
(() => {
    const cfg = __CFG__;
    const makeRng = (seed) => {
        let t = seed + 0x6D2B79F5;
        return () => {
            t = Math.imul(t ^ (t >>> 15), t | 1);
            t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    };

    // ---- navigator: match real Chrome descriptor shapes ----
    // Chrome ships `webdriver` as a *data property* (value:false) on
    // Navigator.prototype. A getter returning `undefined` is detectable.
    try {
        Object.defineProperty(Navigator.prototype, 'webdriver', {
            value: false, writable: true, enumerable: true, configurable: true,
        });
    } catch (e) {}
    const navGet = (prop, val) => {
        try {
            Object.defineProperty(Navigator.prototype, prop, {
                get: () => (typeof val === 'function' ? val() : val),
                set: () => {}, enumerable: true, configurable: true,
            });
        } catch (e) {}
    };
    navGet('hardwareConcurrency', cfg.hardware_concurrency);
    navGet('deviceMemory', cfg.device_memory);
    navGet('platform', cfg.platform);
    navGet('language', cfg.language);
    navGet('languages', () => cfg.languages.slice());
    navGet('maxTouchPoints', cfg.max_touch_points);
    if (cfg.do_not_track !== null && cfg.do_not_track !== undefined) {
        navGet('doNotTrack', cfg.do_not_track ? '1' : '0');
    }

    // ---- screen color depth as a data property (matches real Chrome) ----
    const setScreenDepth = (d) => {
        try {
            Object.defineProperty(Screen.prototype, 'colorDepth', {
                value: d, writable: true, enumerable: true, configurable: true,
            });
            Object.defineProperty(Screen.prototype, 'pixelDepth', {
                value: d, writable: true, enumerable: true, configurable: true,
            });
        } catch (e) {}
    };
    setScreenDepth(cfg.color_depth);

    // ---- deterministic, position-stable per-pixel noise ----
    const hash01 = (seed) => {
        let t = Math.imul(seed, 0x9E3779B1);
        t ^= t >>> 15; t = Math.imul(t, 0x85EBCA6B); t ^= t >>> 13;
        return ((t >>> 0) % 1000) / 1000;
    };
    const applyNoise = (data, seed, rate) => {
        if (rate <= 0) return;
        for (let i = 0; i < data.length; i += 4) {
            if (hash01(seed + (i >> 2)) < rate) {
                data[i] ^= 1 << ((hash01(seed + (i >> 2) + 0x9E3779B1) * 8) | 0);
            }
        }
    };

    // ---- canvas: consistent noise across getImageData/toDataURL/toBlob ----
    const shouldNoise = cfg.canvas_noise;
    const canvasSeeds = new WeakMap();
    let canvasCounter = 0;
    const canvasSeed = (c) => {
        if (!canvasSeeds.has(c)) {
            canvasSeeds.set(c, (cfg.canvas_noise_seed ^ (canvasCounter++ * 0x9E3779B1)) >>> 0);
        }
        return canvasSeeds.get(c);
    };
    const wrap2D = (ctx, canvas) => {
        try {
            const orig = ctx.getImageData;
            ctx.getImageData = function (sx, sy, sw, sh) {
                const img = orig.apply(this, arguments);
                applyNoise(img.data, canvasSeed(canvas) ^ ((sy * sw + sx) * 0x5BD1E995), 0.02);
                return img;
            };
        } catch (e) {}
        return ctx;
    };
    const origGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (type, ...args) {
        const ctx = origGetContext.apply(this, arguments);
        if (ctx && shouldNoise && String(type).toLowerCase() === '2d') {
            return wrap2D(ctx, this);
        }
        return ctx;
    };
    if (shouldNoise) {
        const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function (type, quality) {
            try {
                const ctx = this.getContext('2d');
                if (ctx) {
                    const w = this.width, h = this.height;
                    const img = ctx.getImageData(0, 0, w, h);
                    const tmp = document.createElement('canvas');
                    tmp.width = w; tmp.height = h;
                    tmp.getContext('2d').putImageData(img, 0, 0);
                    return origToDataURL.call(tmp, type, quality);
                }
            } catch (e) {}
            return origToDataURL.apply(this, arguments);
        };
        const origToBlob = HTMLCanvasElement.prototype.toBlob;
        HTMLCanvasElement.prototype.toBlob = function (cb, type, quality) {
            try {
                const ctx = this.getContext('2d');
                if (ctx) {
                    const w = this.width, h = this.height;
                    const img = ctx.getImageData(0, 0, w, h);
                    const tmp = document.createElement('canvas');
                    tmp.width = w; tmp.height = h;
                    tmp.getContext('2d').putImageData(img, 0, 0);
                    return origToBlob.call(tmp, cb, type, quality);
                }
            } catch (e) {}
            return origToBlob.apply(this, arguments);
        };
        const origOcGetContext = OffscreenCanvas.prototype.getContext;
        OffscreenCanvas.prototype.getContext = function (type, ...args) {
            const ctx = origOcGetContext.apply(this, arguments);
            if (ctx && String(type).toLowerCase() === '2d') return wrap2D(ctx, this);
            return ctx;
        };
        const origConvert = OffscreenCanvas.prototype.convertToBlob;
        OffscreenCanvas.prototype.convertToBlob = function (...args) {
            try {
                const ctx = this.getContext('2d');
                if (ctx) {
                    const w = this.width, h = this.height;
                    const img = ctx.getImageData(0, 0, w, h);
                    const tmp = new OffscreenCanvas(w, h);
                    tmp.getContext('2d').putImageData(img, 0, 0);
                    return origConvert.apply(tmp, args);
                }
            } catch (e) {}
            return origConvert.apply(this, args);
        };
    }

    // ---- WebGL: mask vendor/renderer/version + debug extension + precision noise ----
    const glMask = {
        vendor: cfg.webgl_vendor,
        renderer: cfg.webgl_renderer,
        version: cfg.webgl_version || 'WebGL 2.0 (OpenGL ES 3.0 Chromium)',
        glsl: 'OpenGL ES GLSL ES 3.00 (OpenGL ES GLSL ES 3.00 Chromium)',
    };
    const patchGL = (proto) => {
        if (!proto) return;
        const origParam = proto.getParameter;
        proto.getParameter = function (param) {
            // 0x1F00 VENDOR, 0x1F01 RENDERER, 0x1F02 VERSION,
            // 0x8B8C SHADING_LANGUAGE_VERSION, 0x9240/0x9241 UNMASKED_*_WEBGL
            if (param === 0x1F00 && glMask.vendor) return glMask.vendor;
            if (param === 0x1F01 && glMask.renderer) return glMask.renderer;
            if (param === 0x1F02 && glMask.version) return glMask.version;
            if (param === 0x8B8C && glMask.glsl) return glMask.glsl;
            if (param === 0x9240 && glMask.vendor) return glMask.vendor;
            if (param === 0x9241 && glMask.renderer) return glMask.renderer;
            return origParam.apply(this, arguments);
        };
        const origGetExt = proto.getExtension;
        proto.getExtension = function (name) {
            const ext = origGetExt.apply(this, arguments);
            const n = String(name);
            if (ext && n === 'WEBGL_debug_renderer_info') {
                try {
                    Object.defineProperty(ext, 'UNMASKED_VENDOR_WEBGL', { value: glMask.vendor });
                    Object.defineProperty(ext, 'UNMASKED_RENDERER_WEBGL', { value: glMask.renderer });
                } catch (e) {}
            }
            return ext;
        };
        if (cfg.webgl_noise > 0) {
            const origPrec = proto.getShaderPrecisionFormat;
            proto.getShaderPrecisionFormat = function (type, rangeType) {
                const fmt = origPrec.apply(this, arguments);
                if (!fmt) return fmt;
                const rng = makeRng((cfg.canvas_noise_seed ^ (type * 131 + rangeType)) >>> 0);
                try {
                    return {
                        rangeMin: fmt.rangeMin,
                        rangeMax: fmt.rangeMax,
                        precision: fmt.precision + (rng() < 0.5 ? -1 : 1),
                    };
                } catch (e) { return fmt; }
            };
        }
    };
    patchGL(window.WebGLRenderingContext && WebGLRenderingContext.prototype);
    patchGL(window.WebGL2RenderingContext && WebGL2RenderingContext.prototype);

    // ---- WebGPU: mask adapter info ----
    if (cfg.webgpu_device && navigator.gpu && navigator.gpu.requestAdapter) {
        try {
            const origReq = navigator.gpu.requestAdapter.bind(navigator.gpu);
            navigator.gpu.requestAdapter = async (...args) => {
                const adapter = await origReq(...args);
                if (!adapter || !adapter.requestAdapterInfo) return adapter;
                const origInfo = adapter.requestAdapterInfo.bind(adapter);
                adapter.requestAdapterInfo = async () => {
                    const info = await origInfo();
                    try {
                        return Object.assign({}, info, {
                            vendor: cfg.webgpu_vendor,
                            architecture: cfg.webgpu_architecture,
                            device: cfg.webgpu_device,
                            description: cfg.webgpu_description,
                            driver: cfg.webgpu_driver,
                        });
                    } catch (e) { return info; }
                };
                return adapter;
            };
        } catch (e) {}
    }

    // ---- optional sub-pixel clientRects noise ----
    if (cfg.client_rects_noise !== 0) {
        let rectCounter = 0;
        const jitter = () => (makeRng((cfg.canvas_noise_seed ^ (++rectCounter * 0x9E3779B1)) >>> 0)() - 0.5) * 2 * cfg.client_rects_noise;
        const origBR = Element.prototype.getBoundingClientRect;
        Element.prototype.getBoundingClientRect = function () {
            const r = origBR.apply(this, arguments);
            try {
                return new DOMRect(r.x + jitter(), r.y + jitter(), r.width, r.height);
            } catch (e) { return r; }
        };
        const origCR = Element.prototype.getClientRects;
        Element.prototype.getClientRects = function () {
            const list = origCR.apply(this, arguments);
            try {
                const arr = [];
                for (const r of list) arr.push(new DOMRect(r.x + jitter(), r.y + jitter(), r.width, r.height));
                arr.item = (i) => arr[i] || null;
                return arr;
            } catch (e) { return list; }
        };
    }

    // ---- audio noise ----
    if (cfg.audio_noise > 0) {
        const OrigOfflineAudioContext = window.OfflineAudioContext;
        if (OrigOfflineAudioContext) {
            const origStart = OrigOfflineAudioContext.prototype.startRendering;
            OrigOfflineAudioContext.prototype.startRendering = function () {
                const ctx = this;
                return Promise.resolve(origStart.call(ctx)).then((buf) => {
                    try {
                        const amps = cfg.audio_noise * 500;
                        for (let c = 0; c < buf.numberOfChannels; c++) {
                            const d = buf.getChannelData(c);
                            for (let i = 0; i < d.length; i += 4) {
                                d[i] += (Math.random() * 2 - 1) * amps;
                            }
                        }
                    } catch (e) {}
                    return buf;
                });
            };
        }
    }

    // ---- font masking (best-effort in JS; native font masking needs a patched engine) ----
    const addFontMask = (families) => {
        if (!families || !families.length) return;
        const faces = [];
        for (const f of families) {
            try { faces.push(new FontFace(f, "local('" + f + "')")); } catch (e) {}
        }
        const byName = {};
        const normName = (s) => String(s).toLowerCase().replace(/^["']|["']$/g, '');
        faces.forEach((fa) => { byName[normName(fa.family)] = fa; });
        FontFaceSet.prototype.check = function (font) {
            const tokens = String(font || '').trim().split(/\s+/);
            let i = 0;
            for (; i < tokens.length; i++) {
                const t = tokens[i];
                if (/\d/.test(t) || /^(bold|bolder|italic|oblique|normal|lighter|small-caps|inherit|initial|auto)$/i.test(t)) continue;
                break;
            }
            const fam = tokens.slice(i).join(' ').replace(/^["']|["']$/g, '').toLowerCase();
            return !!byName[fam];
        };
        FontFaceSet.prototype.forEach = function (cb, thisArg) { faces.slice().forEach((f) => cb.call(thisArg || this, f, f.family, this)); };
        FontFaceSet.prototype[Symbol.iterator] = function* () { yield* faces; };
        FontFaceSet.prototype.entries = function* () { for (const f of faces) yield [f.family, f]; };
        FontFaceSet.prototype.keys = function* () { for (const f of faces) yield f.family; };
        FontFaceSet.prototype.values = function* () { yield* faces; };
        try { Object.defineProperty(FontFaceSet.prototype, 'size', { get: () => faces.length }); } catch (e) {}
    };
    addFontMask(cfg.fonts);

    // ---- media devices ----
    if (cfg.media_devices) {
        const md = cfg.media_devices;
        const counts = { audioinput: md.audio_inputs || 1, audiooutput: md.audio_outputs || 1, videoinput: md.video_inputs || 1 };
        const makeDevices = () => {
            const out = [];
            for (const kind of ['audioinput', 'audiooutput', 'videoinput']) {
                for (let i = 0; i < counts[kind]; i++) {
                    out.push({
                        kind,
                        deviceId: md.uid + '-' + kind + '-' + i,
                        groupId: md.uid,
                        label: kind === 'videoinput'
                            ? 'HD WebCam'
                            : (kind === 'audiooutput' ? 'Speakers' : 'Microphone') + (counts[kind] > 1 ? ' ' + (i + 1) : ''),
                        toJSON: () => ({}),
                    });
                }
            }
            return out;
        };
        if (!navigator.mediaDevices) {
            try { Object.defineProperty(navigator, 'mediaDevices', { value: {} }); } catch (e) {}
        }
        if (navigator.mediaDevices) {
            try {
                navigator.mediaDevices.enumerateDevices = () => Promise.resolve(makeDevices());
            } catch (e) {}
        }
    }
})();
"""
    return js.replace("__CFG__", json.dumps(cfg, ensure_ascii=True))


def fingerprint_summary(fp: dict, source: str = "") -> str:
    fonts = fp.get("fonts") or []
    md = fp.get("media_devices")
    audio = float(fp.get("audio_noise", 0.0) or 0.0)
    webgl_noise = float(fp.get("webgl_noise", 0.0) or 0.0)
    crn = float(fp.get("client_rects_noise", 0.0) or 0.0)

    webgpu = " / ".join(x for x in (fp.get("webgpu_vendor"),
                                    fp.get("webgpu_architecture"),
                                    fp.get("webgpu_device")) if x)
    webgpu_line = f"WebGPU     : masked ({webgpu})" if webgpu else "WebGPU     : not masked"

    lines = [
        f"Source     : {source if source else 'auto-generated'}",
        f"User-Agent : {fp['ua']}",
        f"Language   : {fp['language']}  ({', '.join(fp['languages'])})",
        f"Timezone   : {fp['timezone']}",
        f"Platform   : {fp['platform']}  (maxTouchPoints={fp.get('max_touch_points', 0)})",
        f"Screen     : {fp['screen_width']}x{fp['screen_height']}  scale={fp['device_scale_factor']}",
        f"Hardware   : {fp['hardware_concurrency']} cores / {fp['device_memory']} GB",
        f"ColorDepth : {fp['color_depth']}",
        f"WebGL      : {fp['webgl_vendor']}",
        f"             {fp['webgl_renderer']}",
        f"WebGLNoise : {'enabled (' + str(webgl_noise) + ')' if webgl_noise else 'off'}",
        webgpu_line,
        f"Canvas     : {'noise enabled' if fp.get('canvas_noise', True) else 'real (no noise)'}",
        f"Audio      : {'noise ' + str(audio) if audio else 'real (no noise)'}",
        f"ClientRect : {'noise ' + str(crn) if crn else 'real (no noise)'}",
        f"Fonts      : {'masked (' + str(len(fonts)) + ' families)' if fonts else 'real (no mask)'}",
        f"MediaDev   : " + (f"masked ({md.get('video_inputs', 0)} cam / {md.get('audio_inputs', 0)} mic)"
                           if md else "real (no mask)"),
        "WebDriver  : hidden (native, Camoufox Firefox)",
        "WebRTC     : IP-leak blocked (proxy only)",
        "Engine     : Camoufox (patched Firefox, native fingerprint)",
    ]
    return "\n".join(lines)
