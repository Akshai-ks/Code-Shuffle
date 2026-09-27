/* User Interactions: Likes, Saves, Sharing, Reporting & Modals */

// Toggle Like
function toggleLike(quoteId, btnEl) {
  fetch(`/api/like/${quoteId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      let countEl = btnEl.querySelector('.count');
      let iconEl = btnEl.querySelector('.icon');
      
      if (!iconEl) {
        btnEl.innerHTML = `<span class="icon">${data.is_liked ? '❤️' : '🤍'}</span><span class="count">${data.likes_count > 0 ? data.likes_count : ''}</span>`;
      } else {
        iconEl.textContent = data.is_liked ? '❤️' : '🤍';
        if (countEl) {
          countEl.textContent = data.likes_count > 0 ? data.likes_count : '';
        }
      }
      
      if (data.is_liked) {
        btnEl.classList.add('liked', 'heart-pop');
      } else {
        btnEl.classList.remove('liked');
      }
      setTimeout(() => btnEl.classList.remove('heart-pop'), 400);
    }
  })
  .catch(err => console.error('Error toggling like:', err));
}

// Toggle Save
function toggleSave(quoteId, btnEl) {
  fetch(`/api/save/${quoteId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      let iconEl = btnEl.querySelector('.icon');
      
      if (data.is_saved) {
        btnEl.classList.add('saved');
        if (iconEl) iconEl.textContent = '🔖';
        showToast('Quote saved to collection! 🔖', 'success');
      } else {
        btnEl.classList.remove('saved');
        if (iconEl) iconEl.textContent = '📑';
        showToast('Quote removed from saved collection.', 'info');
      }
    }
  })
  .catch(err => console.error('Error toggling save:', err));
}

// Open Share Modal & Generate Branded Canvas Image
function openShareModal(quoteId) {
  const modal = document.getElementById('shareModal');
  if (!modal) return;

  fetch(`/api/quote/${quoteId}`)
    .then(res => res.json())
    .then(data => {
      if (data.success && data.quote) {
        generateShareCardCanvas(data.quote);
        modal.classList.add('active');
      }
    });
}

function closeShareModal() {
  const modal = document.getElementById('shareModal');
  if (modal) modal.classList.remove('active');
}

function generateShareCardCanvas(quote) {
  const canvas = document.getElementById('shareCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  canvas.width = 1080;
  canvas.height = 1080;

  // Bright Clean Canvas Background
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, 1080, 1080);

  // Soft Subtle Border Accent
  ctx.strokeStyle = 'rgba(216, 27, 96, 0.2)';
  ctx.lineWidth = 14;
  ctx.strokeRect(30, 30, 1020, 1020);

  ctx.strokeStyle = '#ff6f00';
  ctx.lineWidth = 4;
  ctx.strokeRect(42, 42, 996, 996);

  // Draw Official Rotaract Logo
  const logoImg = new Image();
  logoImg.src = '/static/images/rotaract-logo.png';
  logoImg.onload = () => {
    // Draw Logo at top center with clean scaling
    const logoWidth = 620;
    const logoHeight = (logoImg.height / logoImg.width) * logoWidth;
    ctx.drawImage(logoImg, (1080 - logoWidth) / 2, 70, logoWidth, logoHeight);

    drawCanvasText();
  };

  logoImg.onerror = () => {
    ctx.fillStyle = '#d81b60';
    ctx.font = 'bold 36px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Rotaract Club of St. Thomas College (Autonomous), Thrissur', 540, 120);
    drawCanvasText();
  };

  function drawCanvasText() {
    // Decorative Quote Mark
    ctx.fillStyle = 'rgba(216, 27, 96, 0.08)';
    ctx.font = 'bold 180px Georgia, serif';
    ctx.textAlign = 'center';
    ctx.fillText('“', 540, 380);

    // Quote Text Wrap (Dark readable text)
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 44px Outfit, sans-serif';
    ctx.textAlign = 'center';

    const words = quote.text.split(' ');
    let line = '';
    let y = 460;
    const maxWidth = 880;
    const lineHeight = 64;

    for (let n = 0; n < words.length; n++) {
      const testLine = line + words[n] + ' ';
      const metrics = ctx.measureText(testLine);
      const testWidth = metrics.width;
      if (testWidth > maxWidth && n > 0) {
        ctx.fillText(line.trim(), 540, y);
        line = words[n] + ' ';
        y += lineHeight;
      } else {
        line = testLine;
      }
    }
    ctx.fillText(line.trim(), 540, y);

    // Author (Magenta Rotaract Accent)
    ctx.fillStyle = '#d81b60';
    ctx.font = 'bold 36px Inter, sans-serif';
    ctx.fillText(`— ${quote.author}`, 540, y + 90);

    // Category Badge
    ctx.fillStyle = '#64748b';
    ctx.font = '28px Inter, sans-serif';
    ctx.fillText(`[ ${quote.category_name} ]`, 540, y + 150);

    // Footer Credit
    ctx.fillStyle = '#94a3b8';
    ctx.font = '22px Inter, sans-serif';
    ctx.fillText('Discover & Share Quotes | Rotaract Student Community', 540, 990);
  }
}

function downloadShareCard() {
  const canvas = document.getElementById('shareCanvas');
  if (!canvas) return;
  const link = document.createElement('a');
  link.download = 'rotaract-quote.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
}

function nativeShare() {
  const canvas = document.getElementById('shareCanvas');
  if (navigator.share && canvas) {
    canvas.toBlob(blob => {
      const file = new File([blob], 'rotaract-quote.png', { type: 'image/png' });
      navigator.share({
        title: 'Rotaract Quote',
        text: 'Discovered on Rotaract STC Quote Platform!',
        files: [file]
      }).catch(err => console.log('Share canceled'));
    });
  } else {
    downloadShareCard();
  }
}

// Report Modal
function openReportModal(quoteId) {
  const modal = document.getElementById('reportModal');
  if (!modal) return;
  document.getElementById('reportQuoteId').value = quoteId;
  modal.classList.add('active');
}

function closeReportModal() {
  const modal = document.getElementById('reportModal');
  if (modal) modal.classList.remove('active');
}

function submitReport(e) {
  if (e) e.preventDefault();
  const quoteId = document.getElementById('reportQuoteId').value;
  const reason = document.getElementById('reportReason').value;
  const details = document.getElementById('reportDetails').value;

  fetch(`/api/report/${quoteId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason, details })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      closeReportModal();
      showToast(data.message, 'success');
    } else {
      showToast(data.error || 'Failed to submit report', 'danger');
    }
  });
}

// Toast notification helper
function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toastContainer';
    toastContainer.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 2000; display: flex; flex-direction: column; gap: 10px;';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = `alert alert-${type} animate-reveal`;
  toast.style.cssText = 'margin: 0; min-width: 280px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);';
  toast.innerHTML = `<span>${message}</span>`;

  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 3500);
}
