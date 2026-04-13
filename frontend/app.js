async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const notes = await fetchJSON('/notes/');
  for (const n of notes) {
    const li = document.createElement('li');
    li.textContent = `${n.title}: ${n.content}`;
    list.appendChild(li);
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  loadNotes();
  loadActions();
});

// Logic xử lý nút Delete All Notes
document.addEventListener('DOMContentLoaded', () => {
    const deleteAllBtn = document.getElementById('deleteAllBtn');
    
    if (deleteAllBtn) {
        deleteAllBtn.addEventListener('click', async () => {
            // Xác nhận trước khi xóa
            const isConfirmed = confirm("Are you sure you want to delete ALL notes? This action cannot be undone.");
            
            if (isConfirmed) {
                try {
                    const response = await fetch('/notes/', {
                        method: 'DELETE',
                    });

                    if (response.ok) {
                        alert("All notes have been deleted successfully!");
                        // Tải lại danh sách notes (Giả sử app có hàm loadNotes())
                        // Nếu app dùng hàm khác để tải, hãy thay đổi cho phù hợp
                        if (typeof loadNotes === 'function') {
                            loadNotes();
                        } else {
                            window.location.reload(); // Cách cùi bắp nhất: F5 lại trang
                        }
                    } else {
                        const errorData = await response.json();
                        alert(`Failed to delete notes: ${errorData.detail}`);
                    }
                } catch (error) {
                    console.error("Error deleting notes:", error);
                    alert("An error occurred while deleting notes.");
                }
            }
        });
    }
});