(function () {
  "use strict";

  var CDN = {
    exif: "https://cdn.jsdelivr.net/npm/exifreader@4.23.1/dist/exifreader.js",
    face: "https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js",
    tfjs: "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.0/dist/transformers.min.js"
  };
  var FACE_WEIGHTS = "https://cdn.jsdelivr.net/gh/justadudewhohacks/face-api.js@master/weights";

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src; s.async = true;
      s.onload = resolve; s.onerror = function () { reject(new Error("CDN yuklenemedi: " + src)); };
      document.head.appendChild(s);
    });
  }

  // ---------- MOTOR 1: EXIF FORENSICS (negatif bilgi: yokluk) ----------
  async function exifForensics(buffer) {
    try {
      if (!window.ExifReader) await loadScript(CDN.exif);
      var tags = window.ExifReader.load(buffer, { expanded: true });
      var gps = tags.gps || {};
      var exif = tags.exif || {};
      var hasDate = !!(exif.DateTimeOriginal || exif.DateTime);
      var hasGPS = !!(gps.latitude && gps.longitude);
      var hasMake = !!(tags.file && (tags.file.Make || tags.file.Model)) || !!(exif.Make || exif.Model);
      var findings = [];
      if (!hasDate && !hasGPS && !hasMake) {
        findings.push("EXIF tamamen yok/silinmis: yeniden kaydetme veya manipulasyon suphesi");
      } else {
        if (!hasDate) findings.push("Tarih metadata'si yok: zaman iddiasi dogrulanamaz");
        if (!hasGPS) findings.push("GPS yok: konum iddiasi dogrulanamaz");
        if (!hasMake) findings.push("Cihaz bilgisi yok: kaynak cihaz dogrulanamaz");
      }
      return {
        motor: "ExifReader",
        has_date: hasDate, has_gps: hasGPS, has_device: hasMake,
        date: exif.DateTimeOriginal || exif.DateTime || null,
        gps: hasGPS ? { lat: gps.latitude, lon: gps.longitude } : null,
        negative_findings: findings
      };
    } catch (e) {
      return { motor: "ExifReader", error: String(e), negative_findings: ["EXIF okunamadi"] };
    }
  }

  // ---------- MOTOR 2: ELA (montaj tespiti, canvas tabanli) ----------
  function elaAnalysis(img) {
    return new Promise(function (resolve) {
      try {
        var w = 256, h = 256;
        var c1 = document.createElement("canvas"); c1.width = w; c1.height = h;
        var x1 = c1.getContext("2d"); x1.drawImage(img, 0, 0, w, h);
        var orig = x1.getImageData(0, 0, w, h).data;
        var jpeg = c1.toDataURL("image/jpeg", 0.9);
        var r2 = new Image();
        r2.onload = function () {
          var c2 = document.createElement("canvas"); c2.width = w; c2.height = h;
          var x2 = c2.getContext("2d"); x2.drawImage(r2, 0, 0, w, h);
          var recomp = x2.getImageData(0, 0, w, h).data;
          var diffs = [], sum = 0;
          for (var i = 0; i < orig.length; i += 16) {
            var d = Math.abs(orig[i] - recomp[i]) + Math.abs(orig[i + 1] - recomp[i + 1]) + Math.abs(orig[i + 2] - recomp[i + 2]);
            diffs.push(d); sum += d;
          }
          var mean = sum / diffs.length;
          var max = Math.max.apply(null, diffs);
          var variance = diffs.reduce(function (a, b) { return a + (b - mean) * (b - mean); }, 0) / diffs.length;
          var inconsistency = mean > 0 ? max / mean : 0;
          var findings = [];
          if (inconsistency > 6) findings.push("ELA tutarsizlik orani yuksek (" + inconsistency.toFixed(1) + "): bolgesel yeniden sikistirma = montaj suphesi");
          if (variance > 400) findings.push("ELA varyansi yuksek: homojen olmayan sikistirma gecmisi");
          resolve({ motor: "ELA", mean_diff: +mean.toFixed(2), max_diff: max, inconsistency_ratio: +inconsistency.toFixed(2), negative_findings: findings });
        };
        r2.onerror = function () { resolve({ motor: "ELA", error: "recompress fail", negative_findings: [] }); };
        r2.src = jpeg;
      } catch (e) { resolve({ motor: "ELA", error: String(e), negative_findings: [] }); }
    });
  }

  // ---------- MOTOR 3: YUZ + DUYGU (kisi fotografindan yorum) ----------
  async function faceForensics(img) {
    try {
      if (!window.faceapi) await loadScript(CDN.face);
      await window.faceapi.nets.tinyFaceDetector.loadFromUri(FACE_WEIGHTS);
      await window.faceapi.nets.faceExpressionNet.loadFromUri(FACE_WEIGHTS);
      await window.faceapi.nets.ageGenderNet.loadFromUri(FACE_WEIGHTS);
      var det = await window.faceapi
        .detectAllFaces(img, new window.faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.5 }))
        .withFaceExpressions().withAgeAndGender();
      if (!det || det.length === 0) {
        return { motor: "face-api", face_count: 0, negative_findings: ["Yuz tespit edilmedi: 'kisi fotografi' iddiasi dogrulanamiyor"] };
      }
      var faces = det.map(function (d) {
        var exp = d.expressions.asSortedArray ? d.expressions.asSortedArray() : [];
        return {
          age: Math.round(d.age), gender: d.gender, gender_prob: +d.genderProbability.toFixed(2),
          top_emotion: exp[0] ? exp[0].expression : null,
          top_emotion_prob: exp[0] ? +exp[0].probability.toFixed(2) : null
        };
      });
      var findings = [];
      if (faces.length > 1) findings.push("Birden fazla yuz (" + faces.length + "): kimlik iddiasi belirsiz");
      return { motor: "face-api", face_count: faces.length, faces: faces, negative_findings: findings };
    } catch (e) {
      return { motor: "face-api", error: String(e), negative_findings: ["Yuz motoru yuklenemedi"] };
    }
  }

  // ---------- MOTOR 4: BLIP CAPTION (sahne/nesne, OCR'in goremedigi) ----------
  async function captionForensics(img) {
    try {
      if (!window.transformers) await loadScript(CDN.tfjs);
      var t = window.transformers;
      var cap = await t.pipeline("image-to-text", "Xenova/blip-image-captioning-base");
      var out = await cap(img);
      var text = (out && out[0] && out[0].generated_text) || "";
      return { motor: "BLIP", caption: text, negative_findings: text ? [] : ["Gorsel aciklamasi uretilemedi"] };
    } catch (e) {
      return { motor: "BLIP", error: String(e), negative_findings: ["Caption motoru yuklenemedi"] };
    }
  }

  // ---------- MOTOR 5: OCR (zaten kurulu Tesseract) ----------
  async function ocrForensics(file) {
    try {
      if (!window.Tesseract) return { motor: "Tesseract", error: "Tesseract yuklu degil", negative_findings: [] };
      var res = await window.Tesseract.recognize(file, "tur+eng");
      var text = ((res.data && res.data.text) || "").trim();
      return { motor: "Tesseract", text: text, negative_findings: text.length < 5 ? ["Gorselde anlamlı metin yok"] : [] };
    } catch (e) {
      return { motor: "Tesseract", error: String(e), negative_findings: [] };
    }
  }

  // ---------- CELISKI MOTORU: motorlar arasi negatif bilgi sentezi ----------
  function crossContradictions(report, claimText) {
    var out = [];
    var exif = report.find(function (r) { return r.motor === "ExifReader"; });
    var face = report.find(function (r) { return r.motor === "face-api"; });
    var ocr = report.find(function (r) { return r.motor === "Tesseract"; });
    if (claimText) {
      var c = claimText.toLowerCase();
      if (exif && exif.has_date && exif.date) {
        var year = String(exif.date).match(/(\d{4})/);
        if (year && c.indexOf(year[1]) === -1 && /gecen|bu yil|20\d\d/.test(c)) {
          out.push("IDDA-EXIF CELISKISI: iddia metni ile EXIF tarihi (" + exif.date + ") uyusmayabilir");
        }
      }
      if (face && face.face_count === 0 && /kisi|adam|kadin|cocuk|yuz/.test(c)) {
        out.push("IDDA-YUZ CELISKISI: metin kisi iddia ediyor ama gorselde yuz yok");
      }
      if (ocr && (!ocr.text || ocr.text.length < 5) && /belge|yazi|fatura|makbuz|ekran/.test(c)) {
        out.push("IDDA-OCR CELISKISI: metin belge iddia ediyor ama gorselde okunur yazi yok");
      }
    }
    return out;
  }

  // ---------- ANA GIRIS ----------
  async function analyzeImage(file, claimText, onProgress) {
    onProgress = onProgress || function () {};
    onProgress("Gorsel cozumleniyor...");
    var url = URL.createObjectURL(file);
    var img = new Image();
    await new Promise(function (res, rej) { img.onload = res; img.onerror = rej; img.src = url; });
    var buffer = await file.arrayBuffer();

    onProgress("EXIF forensics...");
    var exif = await exifForensics(buffer);
    onProgress("ELA (montaj tespiti)...");
    var ela = await elaAnalysis(img);
    onProgress("Yuz + duygu analizi...");
    var face = await faceForensics(img);
    onProgress("Sahne aciklamasi (BLIP)...");
    var cap = await captionForensics(img);
    onProgress("OCR...");
    var ocr = await ocrForensics(file);

    var report = [exif, ela, face, cap, ocr];
    var contradictions = crossContradictions(report, claimText || "");
    var negative = [];
    report.forEach(function (r) { (r.negative_findings || []).forEach(function (f) { negative.push(r.motor + ": " + f); }); });
    contradictions.forEach(function (c) { negative.push("CELISKI: " + c); });

    var summary = [
      "[GORSEL TERSINE MUHENDISLIK RAPORU]",
      "Yuz sayisi: " + (face.face_count !== undefined ? face.face_count : "bilinmiyor"),
      "Sahne: " + (cap.caption || "yok"),
      "OCR metin: " + ((ocr.text || "").slice(0, 200) || "yok"),
      "EXIF tarih: " + (exif.date || "yok") + " | GPS: " + (exif.gps ? "var" : "yok"),
      "ELA tutarsizlik: " + (ela.inconsistency_ratio !== undefined ? ela.inconsistency_ratio : "n/a"),
      "NEGATIF BULGULAR:",
      negative.length ? negative.map(function (n) { return "  - " + n; }).join("\n") : "  - bulgu yok"
    ].join("\n");

    URL.revokeObjectURL(url);
    return { report: report, contradictions: contradictions, negative_findings: negative, summary: summary };
  }

  window.InversionVision = { analyzeImage: analyzeImage };
})();
