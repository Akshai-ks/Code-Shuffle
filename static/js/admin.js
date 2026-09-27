/* Admin Dashboard Master Actions & Modal Control Engine */

function updateQuoteStatus(quoteId, status, btnEl) {
  fetch(`/admin/quote/${quoteId}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: status })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(`Quote #${quoteId} status updated to: ${status.toUpperCase()}`, 'success');
      const row = document.getElementById(`quote-row-${quoteId}`);
      if (row) {
        if (window.location.pathname.includes('/pending') || window.location.pathname === '/admin/' || window.location.pathname === '/admin') {
          row.style.transition = 'all 0.3s ease';
          row.style.opacity = '0';
          setTimeout(() => row.remove(), 300);
        } else {
          location.reload();
        }
      } else {
        location.reload();
      }
    } else {
      showToast(data.error || 'Failed to update quote status', 'danger');
    }
  })
  .catch(err => console.error('Error updating status:', err));
}

function deleteQuote(quoteId, reportId = null) {
  if (!confirm('Are you sure you want to permanently delete this quote?')) return;

  fetch(`/admin/quote/${quoteId}/delete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast('Quote permanently deleted.', 'info');
      const quoteRow = document.getElementById(`quote-row-${quoteId}`);
      if (quoteRow) quoteRow.remove();

      if (reportId) {
        const reportRow = document.getElementById(`report-row-${reportId}`);
        if (reportRow) reportRow.remove();
      } else {
        // Also check if any report row referencing this quote exists
        const rows = document.querySelectorAll(`[id^="report-row-"]`);
        rows.forEach(r => {
          if (r.getAttribute('data-quote-id') == quoteId) {
            r.remove();
          }
        });
      }
    }
  })
  .catch(err => console.error('Error deleting quote:', err));
}

function toggleFeatured(quoteId, btnEl) {
  fetch(`/admin/quote/${quoteId}/featured`, {
    method: 'POST'
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.is_featured ? 'Quote set as Featured! ⭐' : 'Quote removed from Featured', 'success');
      if (btnEl) {
        if (data.is_featured) {
          btnEl.classList.add('btn-warning');
          btnEl.textContent = '⭐ Featured';
        } else {
          btnEl.classList.remove('btn-warning');
          btnEl.textContent = '☆ Feature';
        }
      }
    }
  });
}

function toggleMoment(quoteId, btnEl) {
  fetch(`/admin/quote/${quoteId}/moment`, {
    method: 'POST'
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(data.is_quote_of_the_moment ? 'Quote set as Quote of the Moment! ⏱️' : 'Quote of the Moment cleared', 'success');
      location.reload();
    }
  });
}

function toggleBlockUser(userId, btnEl) {
  fetch(`/admin/user/${userId}/block`, {
    method: 'POST'
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      const isBlocked = data.is_blocked;
      showToast(isBlocked ? 'User account blocked 🚫' : 'User account unblocked ✅', isBlocked ? 'warning' : 'success');
      location.reload();
    }
  });
}

function resolveReport(reportId, status) {
  fetch(`/admin/report/${reportId}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: status })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast(`Report marked as ${status}`, 'success');
      const row = document.getElementById(`report-row-${reportId}`);
      if (row) row.remove();
    }
  });
}

// Edit Quote Modal Control
function openEditQuoteModal(quoteId, text, author, categoryId) {
  const modal = document.getElementById('adminEditQuoteModal');
  if (!modal) return;

  const form = document.getElementById('adminEditQuoteForm');
  if (form) {
    form.action = `/admin/quote/${quoteId}/edit`;
  }

  const textInput = document.getElementById('editQuoteText');
  const authorInput = document.getElementById('editQuoteAuthor');
  const categorySelect = document.getElementById('editQuoteCategory');

  if (textInput) textInput.value = text;
  if (authorInput) authorInput.value = author;
  if (categorySelect) categorySelect.value = categoryId;

  modal.classList.add('active');
}

function closeEditQuoteModal() {
  const modal = document.getElementById('adminEditQuoteModal');
  if (modal) modal.classList.remove('active');
}

// Add Quote Modal Control
function openAddQuoteModal() {
  const modal = document.getElementById('adminAddQuoteModal');
  if (modal) modal.classList.add('active');
}

function closeAddQuoteModal() {
  const modal = document.getElementById('adminAddQuoteModal');
  if (modal) modal.classList.remove('active');
}
