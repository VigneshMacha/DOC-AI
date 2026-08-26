document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // 2. Render Markdown & Code Highlighting
  if (window.marked) {
    marked.setOptions({
      highlight: function (code, lang) {
        if (window.hljs && hljs.getLanguage(lang)) {
          return hljs.highlight(code, { language: lang }).value;
        }
        return window.hljs ? hljs.highlightAuto(code).value : code;
      },
      breaks: true,
      gfm: true
    });

    document.querySelectorAll('.markdown-body').forEach((el) => {
      const rawText = el.getAttribute('data-content') || el.textContent;
      el.innerHTML = marked.parse(rawText.trim());

      // Append Copy Button to each pre block
      el.querySelectorAll('pre').forEach((preBlock) => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'code-copy-btn';
        copyBtn.textContent = 'Copy';
        copyBtn.onclick = () => {
          const codeText = preBlock.querySelector('code')?.innerText || preBlock.innerText;
          navigator.clipboard.writeText(codeText).then(() => {
            copyBtn.textContent = 'Copied!';
            setTimeout(() => (copyBtn.textContent = 'Copy'), 2000);
          });
        };
        preBlock.appendChild(copyBtn);
      });
    });
  }

  // 3. Auto-scroll chat feed
  const messageContainer = document.getElementById('message-container');
  if (messageContainer) {
    messageContainer.scrollTop = messageContainer.scrollHeight;
  }

  // 4. Auto-resizing Textarea & Loading State on Submit
  const queryInput = document.getElementById('query-input');
  const queryForm = document.getElementById('query-form');
  const querySubmitBtn = document.getElementById('query-submit-btn');

  if (queryInput && queryForm) {
    queryInput.addEventListener('input', () => {
      queryInput.style.height = 'auto';
      queryInput.style.height = `${Math.min(queryInput.scrollHeight, 180)}px`;
    });

    queryInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (queryInput.value.trim().length > 0) {
          triggerQueryLoading();
          queryForm.submit();
        }
      }
    });

    queryForm.addEventListener('submit', () => {
      if (queryInput.value.trim().length > 0) {
        triggerQueryLoading();
      }
    });
  }

  function triggerQueryLoading() {
    if (querySubmitBtn) {
      querySubmitBtn.disabled = true;
      querySubmitBtn.innerHTML = '<div class="dot-flashing my-1 mx-2"></div>';
    }
  }

  // 5. Drag and Drop PDF Upload handling
  const dropzone = document.getElementById('upload-dropzone');
  const fileInput = document.getElementById('file-input');
  const uploadForm = document.getElementById('upload-form');
  const uploadText = document.getElementById('upload-text');

  if (dropzone && fileInput && uploadForm) {
    ['dragenter', 'dragover'].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        fileInput.files = files;
        handleUploadSubmission();
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        handleUploadSubmission();
      }
    });
  }

  function handleUploadSubmission() {
    if (uploadText) {
      uploadText.innerHTML = '<span class="text-violet-400 animate-pulse font-medium">Processing vectors...</span>';
    }
    uploadForm.submit();
  }

  // 6. Quick Starters Click to Prompt
  document.querySelectorAll('.query-starter-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const promptText = btn.getAttribute('data-prompt');
      if (queryInput && promptText) {
        queryInput.value = promptText;
        queryInput.focus();
        queryInput.style.height = `${Math.min(queryInput.scrollHeight, 180)}px`;
      }
    });
  });
});

// 7. Citation Inspector Modal Functions
function openCitationModal(source, page) {
  const modal = document.getElementById('citation-modal');
  const modalSource = document.getElementById('citation-modal-source');
  const modalPage = document.getElementById('citation-modal-page');
  
  if (modal && modalSource && modalPage) {
    modalSource.innerText = source;
    modalPage.innerText = page;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}

function closeCitationModal() {
  const modal = document.getElementById('citation-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}