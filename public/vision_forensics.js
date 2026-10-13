(function () {
  "use strict";

  var CDN = {
    exif: "https://cdn.jsdelivr.net/npm/exifreader@4.23.1/dist/exif-reader.js",
    face: "https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js",
    tesseract: "https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js"
  };
  var FACE_WEIGHTS = "https://cdn.jsdelivr.net/gh/justadudewhohacks/face-api.js@master/weights";

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (document.querySelector('script[src="' + src + '"]')) {
        return resolve();
      }
      var s = document.createElement("script");
      s.src = src; s.async = true;
      s.onload = resolve; 
      s.onerror = function () { reject(new Error("CDN yuklenemedi: " + src)); };
      document.head.appendChild(s);
    });
  }

  function withTimeout(promise, ms, fallback) {
    return Promise.race([
      promise,
      new Promise(function (resolve) {
        setTimeout(function () { resolve(fallback); }, ms);
      })
    ]);
  }

  // ---------- MOTOR 1: EXIF FORENSICS (negatif bilgi: yokluk) ----------
  async function exifForensics(buffer) {
    try {
      if (!window.ExifReader) {
        await withTimeout(loadScript(CDN.exif), 4000, null);
      }
      if (!window.ExifReader) {
        return { motor: "ExifReader", error: "ExifReader yuklenemedi", negative_findings: ["EXIF kütüphanesi hazır değil"] };
      }
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
        date: (exif.DateTimeOriginal && exif.DateTimeOriginal.description) || (exif.DateTime && exif.DateTime.description) || null,
        gps: hasGPS ? { lat: gps.latitude, lon: gps.longitude } : null,
        negative_findings: findings
      };
    } catch (e) {
      return { motor: "ExifReader", error: String(e), negative_findings: ["EXIF okunamadi: standart web formati"] };
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
      if (!window.faceapi) {
        await withTimeout(loadScript(CDN.face), 3500, null);
      }
      if (!window.faceapi) {
        return { motor: "face-api", face_count: 0, negative_findings: ["Yuz motoru CDN baglantisi atlandi"] };
      }
      await withTimeout(Promise.all([
        window.faceapi.nets.tinyFaceDetector.loadFromUri(FACE_WEIGHTS),
        window.faceapi.nets.faceExpressionNet.loadFromUri(FACE_WEIGHTS),
        window.faceapi.nets.ageGenderNet.loadFromUri(FACE_WEIGHTS)
      ]), 5000, null);

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
      return { motor: "face-api", error: String(e), negative_findings: ["Yuz motoru atlandi"] };
    }
  }

  // ---------- MOTOR 4: OCR (Tesseract) ----------
  async function ocrForensics(file) {
    try {
      if (!window.Tesseract) {
        await withTimeout(loadScript(CDN.tesseract), 3500, null);
      }
      if (!window.Tesseract) {
        return { motor: "Tesseract", error: "Tesseract yuklenemedi", negative_findings: [] };
      }
      var res = await withTimeout(window.Tesseract.recognize(file, "tur+eng"), 8000, null);
      if (!res) {
        return { motor: "Tesseract", text: "", negative_findings: ["OCR zaman asimina ugradi"] };
      }
      var text = ((res.data && res.data.text) || "").trim();
      return { motor: "Tesseract", text: text, negative_findings: text.length < 5 ? ["Gorselde anlamli metin yok"] : [] };
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
    onProgress("Görsel çözümleniyor...");
    var url = URL.createObjectURL(file);
    var img = new Image();
    await new Promise(function (res, rej) { img.onload = res; img.onerror = rej; img.src = url; });
    var buffer = await file.arrayBuffer();

    onProgress("EXIF adli tıp analizi...");
    var exif = await exifForensics(buffer);
    onProgress("ELA montaj tespiti...");
    var ela = await elaAnalysis(img);
    onProgress("Yüz ve mimik tespiti...");
    var face = await withTimeout(faceForensics(img), 6000, { motor: "face-api", face_count: 0, negative_findings: [] });
    onProgress("OCR metin taraması...");
    var ocr = await withTimeout(ocrForensics(file), 8000, { motor: "Tesseract", text: "", negative_findings: [] });

    var report = [exif, ela, face, ocr];
    var contradictions = crossContradictions(report, claimText || "");
    var negative = [];
    report.forEach(function (r) { (r.negative_findings || []).forEach(function (f) { negative.push(r.motor + ": " + f); }); });
    contradictions.forEach(function (c) { negative.push("CELISKI: " + c); });

    var summary = [
      "[GORSEL TERSINE MUHENDISLIK RAPORU]",
      "Dosya: " + file.name + " (" + (file.size / 1024).toFixed(1) + " KB)",
      "Yuz tespiti: " + (face.face_count !== undefined ? face.face_count + " adet" : "yok"),
      "OCR metin: " + ((ocr.text || "").slice(0, 150) || "metin bulunamadi"),
      "EXIF tarih: " + (exif.date || "yok") + " | GPS: " + (exif.gps ? "var" : "yok"),
      "ELA montaj skoru: " + (ela.inconsistency_ratio !== undefined ? ela.inconsistency_ratio : "n/a"),
      "NEGATIF BULGULAR:",
      negative.length ? negative.map(function (n) { return "  - " + n; }).join("\n") : "  - Kritik manipülasyon izi yok"
    ].join("\n");

    URL.revokeObjectURL(url);
    return { report: report, contradictions: contradictions, negative_findings: negative, summary: summary };
  }

  window.InversionVision = { analyzeImage: analyzeImage };
})();
