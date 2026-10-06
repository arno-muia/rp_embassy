/* Real-time drag-and-drop image upload handler for Django admin */
(function() {
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function initDropzone(wrapper) {
    if (wrapper.dataset.initialized) return;
    wrapper.dataset.initialized = 'true';

    const input = wrapper.querySelector('input[type="text"]');
    const dropzone = wrapper.querySelector('.realtime-upload-dropzone');
    const fileInput = wrapper.querySelector('.realtime-upload-fileinput');
    const previewImg = wrapper.querySelector('.realtime-upload-preview-img');
    const previewContainer = wrapper.querySelector('.realtime-upload-preview-container');
    const previewUrl = wrapper.querySelector('.realtime-upload-preview-url');
    const progressBar = wrapper.querySelector('.realtime-upload-progress-bar');
    const progressContainer = wrapper.querySelector('.realtime-upload-progress');
    const errorEl = wrapper.querySelector('.realtime-upload-error');
    const folder = wrapper.dataset.folder || 'general';

    function updatePreview(url) {
      if (!url) {
        if (previewContainer) previewContainer.style.display = 'none';
        return;
      }
      if (previewImg) {
        previewImg.src = url;
        previewImg.onerror = function() {
          previewImg.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100%" height="100%" fill="%23eee"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23aaa" font-size="12">Broken</text></svg>';
        };
      }
      if (previewUrl) {
        previewUrl.textContent = url;
      }
      if (previewContainer) {
        previewContainer.style.display = 'flex';
      }
    }

    if (input && input.value) {
      updatePreview(input.value);
    }

    if (input) {
      input.addEventListener('change', function() {
        updatePreview(input.value.trim());
      });
      input.addEventListener('input', function() {
        updatePreview(input.value.trim());
      });
    }

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', function(e) {
      e.preventDefault();
      fileInput.click();
    });

    fileInput.addEventListener('change', function() {
      if (fileInput.files && fileInput.files[0]) {
        uploadFile(fileInput.files[0]);
      }
    });

    ['dragenter', 'dragover'].forEach(function(ev) {
      dropzone.addEventListener(ev, function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('drag-active');
      }, false);
    });

    ['dragleave', 'drop'].forEach(function(ev) {
      dropzone.addEventListener(ev, function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('drag-active');
      }, false);
    });

    dropzone.addEventListener('drop', function(e) {
      const dt = e.dataTransfer;
      if (dt && dt.files && dt.files.length > 0) {
        uploadFile(dt.files[0]);
      }
    }, false);

    function uploadFile(file) {
      if (errorEl) {
        errorEl.style.display = 'none';
        errorEl.textContent = '';
      }
      if (progressContainer) progressContainer.style.display = 'block';
      if (progressBar) progressBar.style.width = '10%';

      try {
        const reader = new FileReader();
        reader.onload = function(e) {
          if (previewImg) previewImg.src = e.target.result;
          if (previewContainer) previewContainer.style.display = 'flex';
        };
        reader.readAsDataURL(file);
      } catch (e) {}

      const formData = new FormData();
      formData.append('file', file);
      formData.append('folder', folder);

      const csrfToken = getCookie('csrftoken');
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/api/content/upload-image/', true);
      xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      if (csrfToken) xhr.setRequestHeader('X-CSRFToken', csrfToken);

      xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable && progressBar) {
          progressBar.style.width = Math.round((e.loaded / e.total) * 90) + '%';
        }
      });

      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
          if (progressContainer) progressContainer.style.display = 'none';
          if (progressBar) progressBar.style.width = '0%';

          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const res = JSON.parse(xhr.responseText);
              if (res.url) {
                if (input) {
                  input.value = res.url;
                  input.dispatchEvent(new Event('change', { bubbles: true }));
                }
                updatePreview(res.url);
              }
            } catch (err) {
              showError('Invalid server response format.');
            }
          } else {
            let msg = 'Upload failed (HTTP ' + xhr.status + ')';
            try {
              const res = JSON.parse(xhr.responseText);
              if (res.error) msg = res.error;
            } catch (err) {}
            showError(msg);
          }
        }
      };
      xhr.send(formData);
    }

    function showError(msg) {
      if (errorEl) {
        errorEl.textContent = msg;
        errorEl.style.display = 'block';
      } else {
        alert(msg);
      }
    }
  }

  function initAll() {
    document.querySelectorAll('.realtime-upload-field').forEach(initDropzone);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }

  if (window.django && window.django.jQuery) {
    window.django.jQuery(document).on('formset:added', function() {
      setTimeout(initAll, 50);
    });
  }
})();
