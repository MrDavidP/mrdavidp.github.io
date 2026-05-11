/**
 * HoodTip Uploader — custom Cloudinary upload component
 * No Cloudinary widget. Full HoodTip design control.
 *
 * Usage:
 *   Single photo (profile):
 *     const u = new HoodTipUploader({ mode: 'single', target: '#myContainer', onUpload: fn })
 *
 *   Multiple photos (tips):
 *     const u = new HoodTipUploader({ mode: 'multi', target: '#myContainer', onUpload: fn, onChange: fn })
 *
 *   onUpload(url)        — called each time a photo finishes uploading
 *   onChange(urls[])     — called whenever the list changes (multi mode)
 */

(function(global) {
  'use strict';

  var CLOUD   = 'dq9newmhl';
  var PRESET  = 'jykjigyw';
  var API_URL = 'https://api.cloudinary.com/v1_1/' + CLOUD + '/image/upload';

  var CSS = `
    .ht-uploader * { box-sizing: border-box; }
    .ht-uploader {
      font-family: 'Barlow Condensed', system-ui, sans-serif;
    }

    /* Drop zone */
    .ht-drop {
      border: 1.5px dashed #d9d2c6;
      background: #efeae1;
      padding: 2rem 1.5rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: .75rem;
      cursor: pointer;
      transition: border-color .15s, background .15s;
      text-align: center;
      position: relative;
    }
    .ht-drop:hover,
    .ht-drop.drag-over {
      border-color: #1a1816;
      background: #e4ddd1;
    }
    .ht-drop input[type=file] {
      position: absolute;
      inset: 0;
      opacity: 0;
      cursor: pointer;
      width: 100%;
      height: 100%;
    }
    .ht-drop-icon {
      width: 36px;
      height: 36px;
      border: 1.5px solid #6b6560;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #6b6560;
      flex-shrink: 0;
    }
    .ht-drop-icon svg {
      width: 16px;
      height: 16px;
      stroke: currentColor;
      fill: none;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    .ht-drop-label {
      font-size: .78rem;
      font-weight: 500;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: #1a1816;
      line-height: 1.4;
    }
    .ht-drop-sub {
      font-size: .62rem;
      letter-spacing: .1em;
      text-transform: uppercase;
      color: #6b6560;
    }

    /* Single preview (profile photo) */
    .ht-single-wrap {
      display: flex;
      align-items: center;
      gap: 1.25rem;
      flex-wrap: wrap;
    }
    .ht-single-preview {
      width: 100px;
      height: 100px;
      border: 1.5px solid #1a1816;
      background: #efeae1;
      overflow: hidden;
      position: relative;
      flex-shrink: 0;
    }
    .ht-single-preview img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center top;
      display: block;
    }
    .ht-single-actions {
      display: flex;
      flex-direction: column;
      gap: .5rem;
    }
    .ht-btn {
      font-family: 'Barlow Condensed', system-ui, sans-serif;
      font-size: .62rem;
      font-weight: 600;
      letter-spacing: .14em;
      text-transform: uppercase;
      padding: 8px 14px;
      border: 1.5px solid #1a1816;
      background: transparent;
      color: #1a1816;
      cursor: pointer;
      transition: background .15s, color .15s;
      display: inline-block;
    }
    .ht-btn:hover {
      background: #1a1816;
      color: #f7f4ef;
    }
    .ht-btn-remove {
      background: transparent;
      border: none;
      color: #6b6560;
      font-family: 'Barlow Condensed', system-ui, sans-serif;
      font-size: .58rem;
      letter-spacing: .12em;
      text-transform: uppercase;
      cursor: pointer;
      padding: 0;
      text-decoration: underline;
      text-underline-offset: 3px;
      transition: color .15s;
    }
    .ht-btn-remove:hover { color: #b5322a; }
    .ht-status-text {
      font-size: .58rem;
      letter-spacing: .1em;
      text-transform: uppercase;
      color: #6b6560;
    }

    /* Progress bar */
    .ht-progress-wrap {
      height: 2px;
      background: #e0dbd3;
      margin-top: .5rem;
      overflow: hidden;
      display: none;
    }
    .ht-progress-wrap.show { display: block; }
    .ht-progress-bar {
      height: 100%;
      background: #b5322a;
      width: 0%;
      transition: width .1s;
    }

    /* Multi thumbnails grid */
    .ht-thumbs {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(88px, 1fr));
      gap: 6px;
      margin-top: .75rem;
    }
    .ht-thumbs:empty { display: none; }
    .ht-thumb {
      position: relative;
      aspect-ratio: 1/1;
      overflow: hidden;
      border: 1px solid #d9d2c6;
      background: #efeae1;
    }
    .ht-thumb img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .ht-thumb-rm {
      position: absolute;
      top: 4px;
      right: 4px;
      width: 20px;
      height: 20px;
      background: #1a1816;
      color: #f7f4ef;
      border: none;
      border-radius: 0;
      cursor: pointer;
      font-size: 11px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      line-height: 1;
      transition: background .15s;
    }
    .ht-thumb-rm:hover { background: #b5322a; }
    .ht-thumb-badge {
      position: absolute;
      bottom: 4px;
      left: 4px;
      font-family: 'Barlow Condensed', system-ui, sans-serif;
      font-size: .48rem;
      font-weight: 600;
      letter-spacing: .14em;
      text-transform: uppercase;
      background: #b5322a;
      color: #f7f4ef;
      padding: 2px 6px;
    }

    /* Uploading state on thumb */
    .ht-thumb.uploading::after {
      content: '';
      position: absolute;
      inset: 0;
      background: rgba(247,244,239,.6);
    }
    .ht-thumb.uploading::before {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: #b5322a;
      z-index: 2;
      animation: ht-shimmer 1.2s ease-in-out infinite;
    }
    @keyframes ht-shimmer {
      0%   { transform: scaleX(0); transform-origin: left; }
      50%  { transform: scaleX(1); transform-origin: left; }
      51%  { transform: scaleX(1); transform-origin: right; }
      100% { transform: scaleX(0); transform-origin: right; }
    }

    /* Error state */
    .ht-error {
      font-family: 'Barlow Condensed', system-ui, sans-serif;
      font-size: .6rem;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: #b5322a;
      margin-top: .4rem;
      display: none;
    }
    .ht-error.show { display: block; }
  `;

  function injectCSS() {
    if (document.getElementById('ht-uploader-css')) return;
    var style = document.createElement('style');
    style.id = 'ht-uploader-css';
    style.textContent = CSS;
    document.head.appendChild(style);
  }

  function uploadFile(file, onProgress) {
    return new Promise(function(resolve, reject) {
      var fd = new FormData();
      fd.append('file', file);
      fd.append('upload_preset', PRESET);
      fd.append('folder', 'hoodtip');

      var xhr = new XMLHttpRequest();
      xhr.open('POST', API_URL);

      if (onProgress) {
        xhr.upload.addEventListener('progress', function(e) {
          if (e.lengthComputable) {
            onProgress(Math.round((e.loaded / e.total) * 100));
          }
        });
      }

      xhr.onload = function() {
        if (xhr.status === 200) {
          try {
            var data = JSON.parse(xhr.responseText);
            resolve(data.secure_url);
          } catch(e) { reject(new Error('Upload failed')); }
        } else {
          reject(new Error('Upload failed: ' + xhr.status));
        }
      };
      xhr.onerror = function() { reject(new Error('Network error')); };
      xhr.send(fd);
    });
  }

  // ── SINGLE UPLOADER (profile photo) ─────────────────────────────
  function SingleUploader(opts) {
    injectCSS();
    var target = typeof opts.target === 'string'
      ? document.querySelector(opts.target)
      : opts.target;

    var photoUrl = opts.initialUrl || '';
    var onUpload = opts.onUpload || function() {};

    var wrap = document.createElement('div');
    wrap.className = 'ht-uploader';
    wrap.innerHTML = `
      <div class="ht-single-wrap">
        <div class="ht-single-preview" id="htSinglePreview">
          <img id="htSingleImg" src="${photoUrl}" alt="" style="${photoUrl ? '' : 'display:none'}" />
          <svg id="htSinglePlus" viewBox="0 0 24 24" fill="none" stroke="#6b6560" stroke-width="1.5" stroke-linecap="round" style="width:28px;height:28px;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);${photoUrl ? 'display:none' : ''}"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </div>
        <div class="ht-single-actions">
          <button type="button" class="ht-btn" id="htSingleBtn">${photoUrl ? 'Replace photo' : 'Add a photo'}</button>
          <button type="button" class="ht-btn-remove" id="htSingleRm" style="${photoUrl ? '' : 'display:none'}">Remove</button>
          <div class="ht-status-text" id="htSingleStatus">jpg, png &middot; up to 10mb</div>
        </div>
      </div>
      <div class="ht-progress-wrap" id="htSingleProg"><div class="ht-progress-bar" id="htSingleBar"></div></div>
      <div class="ht-error" id="htSingleErr"></div>
      <input type="file" accept="image/*" id="htSingleInput" style="display:none" />
    `;
    target.appendChild(wrap);

    var preview = wrap.querySelector('#htSinglePreview');
    var img     = wrap.querySelector('#htSingleImg');
    var plus    = wrap.querySelector('#htSinglePlus');
    var btn     = wrap.querySelector('#htSingleBtn');
    var rmBtn   = wrap.querySelector('#htSingleRm');
    var status  = wrap.querySelector('#htSingleStatus');
    var prog    = wrap.querySelector('#htSingleProg');
    var bar     = wrap.querySelector('#htSingleBar');
    var err     = wrap.querySelector('#htSingleErr');
    var input   = wrap.querySelector('#htSingleInput');

    function setPhoto(url) {
      photoUrl = url;
      img.src = url;
      img.style.display = url ? 'block' : 'none';
      plus.style.display = url ? 'none' : '';
      btn.textContent = url ? 'Replace photo' : 'Add a photo';
      rmBtn.style.display = url ? '' : 'none';
      status.textContent = url ? 'Looking good.' : 'jpg, png · up to 10mb';
    }

    function handleFile(file) {
      if (!file || !file.type.startsWith('image/')) { showErr('Please select an image file.'); return; }
      if (file.size > 10 * 1024 * 1024) { showErr('File too large — max 10mb.'); return; }
      hideErr();

      // Show local preview immediately
      var reader = new FileReader();
      reader.onload = function(e) { setPhoto(e.target.result); };
      reader.readAsDataURL(file);

      status.textContent = 'Uploading\u2026';
      prog.classList.add('show');
      btn.disabled = true;

      uploadFile(file, function(pct) {
        bar.style.width = pct + '%';
      }).then(function(url) {
        setPhoto(url);
        prog.classList.remove('show');
        bar.style.width = '0%';
        btn.disabled = false;
        onUpload(url);
      }).catch(function(e) {
        showErr('Upload failed — try again.');
        prog.classList.remove('show');
        btn.disabled = false;
        console.error(e);
      });
    }

    function showErr(msg) { err.textContent = msg; err.classList.add('show'); }
    function hideErr() { err.classList.remove('show'); }

    btn.addEventListener('click', function() { input.click(); });
    preview.addEventListener('click', function() { if (!photoUrl) input.click(); });
    input.addEventListener('change', function() { if (input.files[0]) handleFile(input.files[0]); input.value = ''; });
    rmBtn.addEventListener('click', function() { setPhoto(''); onUpload(''); });

    // Drag-and-drop onto preview
    preview.addEventListener('dragover', function(e) { e.preventDefault(); preview.style.borderStyle = 'solid'; });
    preview.addEventListener('dragleave', function() { preview.style.borderStyle = 'dashed'; });
    preview.addEventListener('drop', function(e) {
      e.preventDefault();
      preview.style.borderStyle = '';
      var file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    });

    this.getUrl = function() { return photoUrl; };
    this.setUrl = function(url) { setPhoto(url); };
  }

  // ── MULTI UPLOADER (tip photos) ──────────────────────────────────
  function MultiUploader(opts) {
    injectCSS();
    var target = typeof opts.target === 'string'
      ? document.querySelector(opts.target)
      : opts.target;

    var maxFiles  = opts.maxFiles || 8;
    var onUpload  = opts.onUpload  || function() {};
    var onChange  = opts.onChange  || function() {};
    var photos    = []; // {url, uploading}

    var wrap = document.createElement('div');
    wrap.className = 'ht-uploader';
    wrap.innerHTML = `
      <div class="ht-drop" id="htDrop">
        <input type="file" accept="image/*" multiple id="htDropInput" />
        <div class="ht-drop-icon">
          <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        </div>
        <div class="ht-drop-label">Drop photos here or <span style="color:#b5322a;cursor:pointer;">browse</span></div>
        <div class="ht-drop-sub">Up to ${maxFiles} photos &middot; jpg, png, heic &middot; 15mb each &middot; landscape preferred</div>
      </div>
      <div class="ht-error" id="htMultiErr"></div>
      <div class="ht-thumbs" id="htThumbs"></div>
    `;
    target.appendChild(wrap);

    var drop      = wrap.querySelector('#htDrop');
    var dropInput = wrap.querySelector('#htDropInput');
    var thumbsEl  = wrap.querySelector('#htThumbs');
    var errEl     = wrap.querySelector('#htMultiErr');

    function showErr(msg) { errEl.textContent = msg; errEl.classList.add('show'); setTimeout(function() { errEl.classList.remove('show'); }, 3000); }

    function render() {
      thumbsEl.innerHTML = '';
      photos.forEach(function(p, i) {
        var t = document.createElement('div');
        t.className = 'ht-thumb' + (p.uploading ? ' uploading' : '');

        var img = document.createElement('img');
        img.src = p.preview || p.url;
        img.alt = '';
        t.appendChild(img);

        if (i === 0 && !p.uploading) {
          var badge = document.createElement('span');
          badge.className = 'ht-thumb-badge';
          badge.textContent = 'Hero';
          t.appendChild(badge);
        }

        if (!p.uploading) {
          var rm = document.createElement('button');
          rm.type = 'button';
          rm.className = 'ht-thumb-rm';
          rm.innerHTML = '&times;';
          rm.setAttribute('aria-label', 'Remove photo');
          rm.addEventListener('click', function() {
            photos.splice(i, 1);
            render();
            onChange(getUrls());
          });
          t.appendChild(rm);
        }

        thumbsEl.appendChild(t);
      });

      // Update drop zone label
      var remaining = maxFiles - photos.length;
      drop.querySelector('.ht-drop-sub').textContent =
        remaining > 0
          ? 'Up to ' + remaining + ' more \u00b7 jpg, png, heic \u00b7 15mb each \u00b7 landscape preferred'
          : 'Maximum ' + maxFiles + ' photos reached';
    }

    function getUrls() {
      return photos.filter(function(p) { return !p.uploading && p.url; }).map(function(p) { return p.url; });
    }

    function handleFiles(files) {
      var arr = Array.from(files);
      var available = maxFiles - photos.length;
      if (available <= 0) { showErr('Maximum ' + maxFiles + ' photos reached.'); return; }
      arr = arr.slice(0, available);

      arr.forEach(function(file) {
        if (!file.type.startsWith('image/')) return;
        if (file.size > 15 * 1024 * 1024) { showErr(file.name + ' is too large — max 15mb.'); return; }

        // Add placeholder immediately with local preview
        var reader = new FileReader();
        var idx = photos.length;
        var entry = { url: '', preview: '', uploading: true };
        photos.push(entry);
        render();

        reader.onload = function(e) {
          entry.preview = e.target.result;
          render();
        };
        reader.readAsDataURL(file);

        uploadFile(file, null).then(function(url) {
          entry.url = url;
          entry.uploading = false;
          render();
          onUpload(url);
          onChange(getUrls());
        }).catch(function(err) {
          photos.splice(photos.indexOf(entry), 1);
          render();
          showErr('Upload failed — try again.');
          console.error(err);
        });
      });
    }

    // Events
    drop.addEventListener('dragover', function(e) { e.preventDefault(); drop.classList.add('drag-over'); });
    drop.addEventListener('dragleave', function() { drop.classList.remove('drag-over'); });
    drop.addEventListener('drop', function(e) {
      e.preventDefault();
      drop.classList.remove('drag-over');
      if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
    });
    dropInput.addEventListener('change', function() {
      if (dropInput.files.length) handleFiles(dropInput.files);
      dropInput.value = '';
    });

    this.getUrls  = getUrls;
    this.getCount = function() { return photos.filter(function(p) { return !p.uploading; }).length; };
    this.clear    = function() { photos = []; render(); onChange([]); };
  }

  // ── PUBLIC API ───────────────────────────────────────────────────
  global.HoodTipUploader = {
    single: function(opts) { return new SingleUploader(opts); },
    multi:  function(opts) { return new MultiUploader(opts); }
  };

})(window);
