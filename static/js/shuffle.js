/* Master 3D Folded-Paper Discovery Engine */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const introScreen = document.getElementById('introScreen');
  const mainScreen = document.getElementById('mainScreen');

  const startDiscoveringBtn = document.getElementById('startDiscoveringBtn');

  const shuffleBtn = document.getElementById('shuffleBtn');
  const paperContainer = document.getElementById('paperContainer');
  const floatingHeartsLayer = document.getElementById('floatingHeartsLayer');
  const paperStateCaption = document.getElementById('paperStateCaption');

  // SCREEN 01 -> SCREEN 02 Transition (Get Started Button)
  if (startDiscoveringBtn) {
    startDiscoveringBtn.addEventListener('click', (e) => {
      e.preventDefault();

      if (introScreen && mainScreen) {
        introScreen.classList.add('animate-screen-out');
        setTimeout(() => {
          introScreen.style.display = 'none';
          mainScreen.style.display = 'block';
          mainScreen.classList.add('animate-screen-in');
          
          const quoteContentEl = paperContainer ? paperContainer.querySelector('.paper-quote-content') : null;
          if (quoteContentEl) quoteContentEl.style.opacity = '1';
        }, 450);
      }
    });
  }

  if (!shuffleBtn) return;

  let isShuffling = false;

  shuffleBtn.addEventListener('click', () => {
    if (isShuffling) return;
    performPhysicalPaperDiscovery();
  });

  function performPhysicalPaperDiscovery() {
    isShuffling = true;

    // STEP 1: Button state change & initial caption (0.0s)
    shuffleBtn.disabled = true;
    shuffleBtn.classList.add('shuffling');
    shuffleBtn.innerHTML = `<svg class="shuffle-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M16 3h5v5M4 20L21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/></svg> DISCOVERING...`;

    if (paperStateCaption) {
      paperStateCaption.textContent = "✨ Shuffling thoughts...";
      paperStateCaption.style.opacity = '1';
    }

    if (floatingHeartsLayer) floatingHeartsLayer.innerHTML = '';

    const foldedNote = paperContainer.querySelector('.paper-folded-note');
    const quoteContentEl = paperContainer.querySelector('.paper-quote-content');
    const stackBg = paperContainer.querySelector('.paper-stack-bg');

    if (foldedNote) {
      foldedNote.classList.remove('animate-card-glow');
    }

    // Initiate API fetch early
    let fetchedQuote = null;
    let fetchError = null;

    const fetchPromise = fetch('/api/shuffle')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.quote) {
          fetchedQuote = data.quote;
        } else {
          fetchError = 'No quotes available right now.';
        }
      })
      .catch(() => {
        fetchError = 'Failed to load quote. Please try again.';
      });

    // STEP 2: 3D Stack Shuffling Wiggles (0.2s)
    if (stackBg) {
      stackBg.classList.add('shuffling');
      setTimeout(() => stackBg.classList.remove('shuffling'), 1100);
    }

    // STEP 3: Fold paper back if unfolded (0.6s)
    setTimeout(() => {
      if (foldedNote && foldedNote.classList.contains('is-unfolded')) {
        if (quoteContentEl) quoteContentEl.style.opacity = '0';
        if (paperStateCaption) paperStateCaption.textContent = "Folding paper back...";
        foldedNote.classList.remove('is-unfolded');
        foldedNote.classList.add('animate-paper-foldback');
      }

      // STEP 4: Paper Note Rises from Stack in 3D (1.4s)
      setTimeout(() => {
        if (foldedNote) {
          foldedNote.classList.remove('animate-paper-foldback', 'animate-paper-rise');
          void foldedNote.offsetWidth; // trigger reflow
          foldedNote.classList.add('animate-paper-rise');
        }

        if (paperStateCaption) paperStateCaption.textContent = "📜 Selecting an inspiring note...";

        if (quoteContentEl) {
          quoteContentEl.style.opacity = '0';
        }

        // STEP 5: 3D Unfold Paper Flaps (2.5s)
        setTimeout(() => {
          if (paperStateCaption) paperStateCaption.textContent = "✨ Unfolding paper...";
          
          if (foldedNote) {
            foldedNote.classList.add('is-unfolded');
          }

          // STEP 6: Final Quote Reveal & Sparkle Bloom (3.6s)
          setTimeout(async () => {
            await fetchPromise;
            if (fetchedQuote) {
              renderPaperQuote(fetchedQuote);
              renderFloatingHearts();
              if (foldedNote) foldedNote.classList.add('animate-card-glow');
              if (paperStateCaption) paperStateCaption.textContent = "💖 A thought revealed for you! ✨";
            } else {
              showErrorPaper(fetchError || 'No quotes available right now.');
              if (paperStateCaption) paperStateCaption.textContent = "Try again!";
            }
            resetShuffleButton();
          }, 1100); // 2500 + 1100 = 3600ms total

        }, 1100); // 1400 + 1100 = 2500ms

      }, 800); // 600 + 800 = 1400ms

    }, 600);
  }

  function resetShuffleButton() {
    isShuffling = false;
    shuffleBtn.disabled = false;
    shuffleBtn.classList.remove('shuffling');
    shuffleBtn.innerHTML = `<svg class="shuffle-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M16 3h5v5M4 20L21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/></svg> DISCOVER ANOTHER`;
  }

  function renderPaperQuote(q) {
    const isLiked = q.is_liked ? 'liked' : '';
    const isSaved = q.is_saved ? 'saved' : '';
    const heartIcon = q.is_liked ? '❤️' : '🤍';

    const quoteContentEl = paperContainer.querySelector('.paper-quote-content');
    if (!quoteContentEl) return;

    // Category Pill
    const categoryName = q.category_name ? escapeHtml(q.category_name) : 'Inspiration';
    const categoryPillHtml = `<div style="margin-bottom: 0.85rem;"><span class="quote-category-pill">✨ ${categoryName}</span></div>`;

    const authorHtml = q.author ? `<span class="paper-quote-author" style="animation-delay: 0.18s;">— ${escapeHtml(q.author)}</span>` : '';

    quoteContentEl.innerHTML = `
      <div class="animate-quote-reveal">
        <span class="paper-quote-mark">❝</span>
        <p class="paper-quote-text">${escapeHtml(q.text)}</p>
        ${categoryPillHtml}
        ${authorHtml}
        
        <div class="paper-quote-actions">
          <div class="action-buttons-group">
            <button class="action-btn-circle like-btn ${isLiked}" onclick="toggleLike(${q.id}, this)" title="Like Quote">
              <span class="icon">${heartIcon}</span>
              <span class="count">${q.likes_count > 0 ? q.likes_count : ''}</span>
            </button>
            <button class="action-btn-circle save-btn ${isSaved}" onclick="toggleSave(${q.id}, this)" title="Bookmark Quote">
              <span class="icon">${q.is_saved ? '🔖' : '📑'}</span>
            </button>
            <button class="action-btn-circle share-btn" onclick="openShareModal(${q.id})" title="Share Quote">
              <span class="icon">↗</span>
            </button>
          </div>
        </div>
      </div>
    `;
    quoteContentEl.style.opacity = '1';
  }

  /* Render 6 to 9 floating pink & gold sparkle items around unfolded paper card */
  function renderFloatingHearts() {
    if (!floatingHeartsLayer) return;
    floatingHeartsLayer.innerHTML = '';

    const symbols = ['♥', '♡', '✨', '🌸', '🌟', '💖'];
    const count = 7;
    const positions = [
      { top: '6%', left: '5%' },
      { top: '10%', right: '6%' },
      { top: '42%', left: '3%' },
      { top: '48%', right: '4%' },
      { bottom: '12%', left: '8%' },
      { bottom: '10%', right: '9%' },
      { top: '22%', left: '12%' }
    ];

    for (let i = 0; i < count; i++) {
      const item = document.createElement('div');
      item.className = 'floating-heart';
      item.innerHTML = symbols[i % symbols.length];

      const pos = positions[i % positions.length];
      if (pos.top) item.style.top = pos.top;
      if (pos.bottom) item.style.bottom = pos.bottom;
      if (pos.left) item.style.left = pos.left;
      if (pos.right) item.style.right = pos.right;

      const size = Math.floor(Math.random() * 8) + 16; // 16px to 24px
      item.style.fontSize = `${size}px`;
      item.style.animation = `floatSparkleHeart 2.2s cubic-bezier(0.22, 1, 0.36, 1) forwards`;
      item.style.animationDelay = `${(i * 0.12).toFixed(2)}s`;

      floatingHeartsLayer.appendChild(item);
    }
  }

  function showErrorPaper(msg) {
    const quoteContentEl = paperContainer.querySelector('.paper-quote-content');
    if (quoteContentEl) {
      quoteContentEl.innerHTML = `
        <div style="padding: 1.5rem 0;" class="animate-quote-reveal">
          <p style="color: var(--muted); font-size: 1.1rem;">${escapeHtml(msg)}</p>
        </div>
      `;
      quoteContentEl.style.opacity = '1';
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }
});
